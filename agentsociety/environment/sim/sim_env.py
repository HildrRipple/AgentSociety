import logging
import os
import signal
import subprocess
from multiprocessing import cpu_count
from subprocess import Popen
from typing import Optional

import yaml

from ...logger import get_logger
from ..syncer import Server as Syncer
from ..utils import encode_to_base64, find_free_ports

__all__ = ["ControlSimEnv"]

JOB_NAME = "agentsociety"


def _generate_yaml_config(
    map_file: str, max_day: int, start_step: int, total_step: int
) -> str:
    config_dict = {
        "input": {"map": {"file": os.path.abspath(map_file)}},
        "control": {
            "day": max_day,
            "step": {"start": start_step, "total": total_step, "interval": 1},
            "skip_overtime_trip_when_init": True,
            "enable_platoon": False,
            "enable_indoor": False,
            "prefer_fixed_light": True,
            "enable_collision_avoidance": False,
            "enable_go_astray": True,
            "lane_change_model": "earliest",
        },
        "output": None,
    }
    return yaml.dump(config_dict, allow_unicode=True)


class ControlSimEnv:
    def __init__(
        self,
        map_file: str,
        max_day: int,
        start_step: int,
        total_step: int,
        log_dir: str,
        primary_node_ip: str,
        max_process: int = cpu_count(),
        logging_level: str = "info",
    ):
        """
        A control environment for managing a agentsociety-sim process.

        - **Description**:
            - This class sets up and manages a simulation environment using the specified parameters.
            - It can start a new simulation process or connect to an existing one.
        """
        self._map_file = map_file
        self._max_day = max_day
        self._start_step = start_step
        self._total_step = total_step
        self._log_dir = log_dir
        self._primary_node_ip = primary_node_ip
        self._max_procs = max_process
        self._logging_level = logging_level
        self._sim_config = _generate_yaml_config(
            map_file, max_day, start_step, total_step
        )
        # sim
        self._sim_proc = None
        os.makedirs(log_dir, exist_ok=True)
        self._syncer: Optional[Syncer] = None
        self.sim_addr: Optional[str] = None

    async def init(self):
        """
        Initialize the simulation environment by either starting a new simulation process.

        - **Returns**:
            - tuple[str, str]: The address of the simulation server and the syncer server.

        - **Raises**:
            - `AssertionError`: If trying to start a new simulation when one is already running.
        """
        sim_port, syncer_port = find_free_ports(2)
        # start syncer
        syncer_addr = f"localhost:{syncer_port}"
        self._syncer = Syncer(syncer_addr)
        await self._syncer.init()

        # start agentsociety-sim
        config_base64 = encode_to_base64(self._sim_config)
        os.environ["GOMAXPROCS"] = str(self._max_procs)
        self.sim_addr = self._primary_node_ip.rstrip("/") + f":{sim_port}"
        self._sim_proc = Popen(
            [
                "agentsociety-sim",
                "-config-data",
                config_base64,
                "-job",
                JOB_NAME,
                "-listen",
                self.sim_addr,
                "-syncer",
                "http://" + syncer_addr,
                "-output",
                self._log_dir,
                "-cache",
                "",
                "-log.level",
                self._logging_level,
            ],
            env=os.environ,
        )

        # step 1 tick as the syncer init
        await self.syncer.step()

        get_logger().info(f"start agentsociety-sim at {self.sim_addr}, PID={self._sim_proc.pid}")

    async def close(self):
        """
        Terminate the simulation process if it's running.
        """
        if self._syncer is not None:
            await self._syncer.close()
            self._syncer = None
        if self._sim_proc is not None and self._sim_proc.poll() is None:
            get_logger().info(f"Terminating agentsociety-sim at {self.sim_addr}, PID={self._sim_proc.pid}, please ignore the PANIC message")
            self._sim_proc.kill()
            # wait for the process to terminate
            self._sim_proc.wait()
        self._sim_proc = None

    @property
    def syncer(self):
        assert self._syncer is not None, "Syncer not initialized"
        return self._syncer
