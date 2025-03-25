import logging
from multiprocessing import cpu_count
import os
import subprocess
from subprocess import Popen

import yaml

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

        self._sim_config = _generate_yaml_config(
            map_file, max_day, start_step, total_step
        )
        # sim
        self.sim_port = None
        self._sim_proc = None
        os.makedirs(log_dir, exist_ok=True)

        self.sim_addr, self.syncer_addr = self.init()

    def init(self):
        """
        Initialize the simulation environment by either starting a new simulation process.

        - **Returns**:
            - tuple[str, str]: The address of the simulation server and the syncer server.

        - **Raises**:
            - `AssertionError`: If trying to start a new simulation when one is already running.
        """
        syncer_addr = ""
        # 启动agentsociety-sim
        # agentsociety-sim -config-data configbase64 -job test -listen :51102
        assert self.sim_port is None, "Simulation already running"
        assert self._sim_proc is None, "Simulation already running"
        _ports = find_free_ports(2)
        self.sim_port, self.syncer_port = _ports
        config_base64 = encode_to_base64(self._sim_config)
        os.environ["GOMAXPROCS"] = str(self._max_procs)
        sim_addr = self._primary_node_ip.rstrip("/") + f":{self.sim_port}"
        syncer_addr = f"http://localhost:{self.syncer_port}"
        self._sim_proc = Popen(
            [
                "agentsociety-sim",
                "-config-data",
                config_base64,
                "-job",
                JOB_NAME,
                "-listen",
                sim_addr,
                "-syncer",
                syncer_addr,
                "-output",
                self._log_dir,
                "-cache",
                "",
                "-log.level",
                "info",
            ],
            env=os.environ,
        )
        logging.info(f"start agentsociety-sim at {sim_addr}, PID={self._sim_proc.pid}")
        
        return sim_addr, syncer_addr

    def close(self):
        """
        Terminate the simulation process if it's running.
        """
        if self._sim_proc is not None:
            self._sim_proc.terminate()
            try:
                sim_code = self._sim_proc.wait(10)
                logging.info(f"agentsociety-sim exit with code {sim_code}")
            except subprocess.TimeoutExpired as te:
                self._sim_proc.kill()
                logging.warning(f"agentsociety-sim killed: {te}")

        # sim
        self.sim_port = None
        self._sim_proc = None
