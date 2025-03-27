"""Simulator: Urban Simulator"""

import asyncio
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Literal, Optional, Union, cast, overload

from pydantic import BaseModel, ConfigDict, Field
from mosstool.type import TripMode
from mosstool.util.format_converter import dict2pb
from pycityproto.city.map.v2 import map_pb2 as map_pb2
from pycityproto.city.person.v2 import person_pb2 as person_pb2
from pycityproto.city.person.v2 import person_service_pb2 as person_service
from pyproj import Proj
from shapely.geometry import Point

from ..logger import get_logger
from ..utils.decorators import log_execution_time
from .economy.econ_client import EconomyClient
from .mapdata import MapData, MapConfig
from .sim import CityClient, ControlSimEnv
from .syncerclient import SyncerClient
from .utils.const import *

__all__ = [
    "Environment",
    "EnvironmentStarter",
    "SimulatorConfig",
    "EnvironmentConfig",
]


class SimulatorConfig(BaseModel):
    """Simulator configuration class."""

    log_dir: str = Field("./log")
    """Directory path for saving logs"""

    primary_node_ip: str = Field("localhost")
    """Primary node IP address for distributed simulation. 
    If you want to run the simulation on a single machine, you can set it to "localhost".
    If you want to run the simulation on a distributed machine, you can set it to the IP address of the machine and keep all the ports of the primary node can be accessed from the other nodes (the code will automatically set the ports).
    """

    timeout: float = Field(60, gt=0)
    """Timeout for the initialization of the simulation"""


class EnvironmentConfig(BaseModel):
    """Configuration for the simulation environment."""

    model_config = ConfigDict(use_enum_values=True, use_attribute_docstrings=True)

    max_day: int = Field(1000)
    """Maximum number of days to simulate"""

    start_tick: int = Field(6 * 60 * 60)
    """Starting tick of one day, in seconds"""

    total_tick: int = Field(18 * 60 * 60)
    """Total number of ticks in one day"""

    weather: str = Field(default="The weather is sunny")
    """Current weather condition in the environment"""

    temperature: str = Field(default="The temperature is 23C")
    """Current temperature in the environment"""

    workday: bool = Field(default=True)
    """Indicates if it's a working day"""

    other_information: str = Field(default="")
    """Additional environment information"""

    def to_prompts(self) -> dict[str, Any]:
        """Convert the environment config to prompts"""
        return {
            "weather": self.weather,
            "temperature": self.temperature,
            "workday": self.workday,
            "other_information": self.other_information,
        }


class Environment:
    """
    The environment, including map data, simulator clients, and environment variables.
    """

    def __init__(
        self,
        map_data: MapData,
        server_addr: str,
        environment_config: EnvironmentConfig,
        # TEMP
        # TODO: try to remove this
        citizen_ids: set[int] = set(),
        firm_ids: set[int] = set(),
        bank_ids: set[int] = set(),
        nbs_ids: set[int] = set(),
        government_ids: set[int] = set(),
    ):
        """
        Initialize the Environment.

        - **Args**:
            - `map_data`: `MapData`, map data
            - `server_addr`: `str`, server address
            - `environment_config`: `EnvironmentConfig`, environment config
        """
        self._map = map_data
        self._create_poi_id_2_aoi_id()
        self._server_addr = server_addr
        self.poi_cate = POI_CATG_DICT
        """poi categories"""

        self._projector = Proj(self._map.get_projector())

        self._environment_prompt = environment_config.to_prompts()

        self._client = CityClient(self._server_addr)
        self._economy_client = EconomyClient(self._server_addr)
        self._economy_client.set_ids(
            citizen_ids=citizen_ids,
            firm_ids=firm_ids,
            bank_ids=bank_ids,
            nbs_ids=nbs_ids,
            government_ids=government_ids,
        )

        self.time: int = 0
        """current time of simulator"""

        self._log_list = []
        """log list"""

        self._lock = asyncio.Lock()
        """lock for simulator"""

    def close(self):
        """Close the Environment."""
        pass

    def _create_poi_id_2_aoi_id(self):
        assert self._map is not None
        pois = self._map.get_all_pois()
        self.poi_id_2_aoi_id: dict[int, int] = {
            poi["id"]: poi["aoi_id"] for poi in pois
        }

    @property
    def map(self):
        assert self._map is not None, "Map not initialized"
        return self._map

    @property
    def economy_client(self):
        return self._economy_client

    @property
    def projector(self):
        return self._projector

    def get_log_list(self):
        return self._log_list

    def clear_log_list(self):
        self._log_list = []

    def get_poi_cate(self):
        return self.poi_cate

    def get_aoi_ids(self):
        aois = self._map.get_all_aois()
        return [aoi["id"] for aoi in aois]

    @property
    def environment(self) -> dict[str, str]:
        """
        Get the current state of environment variables.
        """
        return self._environment_prompt

    def set_environment(self, environment: dict[str, str]):
        """
        Set the entire dictionary of environment variables.

        - **Args**:
            - `environment` (`Dict[str, str]`): Key-value pairs of environment variables.
        """
        self._environment_prompt = environment

    def sense(self, key: str) -> Any:
        """
        Retrieve the value of an environment variable by its key.

        - **Args**:
            - `key` (`str`): The key of the environment variable.

        - **Returns**:
            - `Any`: The value of the corresponding key, or an empty string if not found.
        """
        return self._environment_prompt.get(key, "")

    def update_environment(self, key: str, value: Any):
        """
        Update the value of a single environment variable.

        - **Args**:
            - `key` (`str`): The key of the environment variable.
            - `value` (`Any`): The new value to set.
        """
        self._environment_prompt[key] = value

    def get_environment(self) -> str:
        global_prompt = ""
        for key in self._environment_prompt:
            value = self._environment_prompt[key]
            if isinstance(value, str):
                global_prompt += f"{key}: {value}\n"
            elif isinstance(value, dict):
                for k, v in value.items():
                    global_prompt += f"{key}.{k}: {v}\n"
            elif isinstance(value, bool):
                global_prompt += f"Is it {key}: {value}\n"
            elif isinstance(value, list):
                global_prompt += f"{key} elements: {value}\n"
            else:
                global_prompt += f"{key}: {value}\n"
        return global_prompt

    @log_execution_time
    def get_poi_categories(
        self,
        center: Optional[Union[tuple[float, float], Point]] = None,
        radius: Optional[float] = None,
    ) -> list[str]:
        """
        Retrieve unique categories of Points of Interest (POIs) around a central point.

        - **Args**:
            - `center` (`Optional[Union[Tuple[float, float], Point]]`): The central point as a tuple or Point object.
              Defaults to (0, 0) if not provided.
            - `radius` (`Optional[float]`): The search radius in meters. If not provided, all POIs are considered.

        - **Returns**:
            - `List[str]`: A list of unique POI category names.
        """
        categories: list[str] = []
        if center is None:
            center = (0, 0)
        assert self._map is not None
        _pois: list[Any] = self._map.query_pois(
            center=center,
            radius=radius,
            return_distance=False,
        )
        for poi in _pois:
            catg = poi["category"]
            categories.append(catg.split("|")[-1])
        return list(set(categories))

    @overload
    async def get_time(self) -> int: ...
    @overload
    async def get_time(self, format_time: Literal[False]) -> int: ...
    @overload
    async def get_time(
        self, format_time: Literal[True], format: str = "%H:%M:%S"
    ) -> str: ...

    @log_execution_time
    async def get_time(
        self, format_time: bool = False, format: str = "%H:%M:%S"
    ) -> Union[int, str]:
        """
        Get the current time of the simulator.

        By default, returns the number of seconds since midnight. Supports formatted output.

        - **Args**:
            - `format_time` (`bool`): Whether to return the time in a formatted string. Defaults to `False`.
            - `format` (`str`): The format string for formatting the time. Defaults to "%H:%M:%S".

        - **Returns**:
            - `Union[int, str]`: The current simulation time either as an integer representing seconds since midnight or as a formatted string.
        """
        now = await self._client.clock_service.Now({})
        now = cast(dict[str, int], now)
        self.time = now["t"]
        if format_time:
            current_date = datetime.now().date()
            start_of_day = datetime.combine(current_date, datetime.min.time())
            current_time = start_of_day + timedelta(seconds=now["t"])
            formatted_time = current_time.strftime(format)
            return formatted_time
        else:
            return int(now["t"])

    @log_execution_time
    async def get_simulator_day(self) -> int:
        """
        Get the current day of the simulation.

        - **Returns**:
            - `int`: The day number since the start of the simulation.
        """
        now = await self._client.clock_service.Now({})
        now = cast(dict[str, int], now)
        day = int(now["t"] // (24 * 60 * 60))
        return day

    @log_execution_time
    async def get_simulator_second_from_start_of_day(self) -> int:
        """
        Get the number of seconds elapsed from the start of the current day in the simulation.

        - **Returns**:
            - `int`: The number of seconds from 00:00:00 of the current day.
        """
        now = await self._client.clock_service.Now({})
        now = cast(dict[str, int], now)
        return now["t"] % (24 * 60 * 60)

    @log_execution_time
    async def get_person(self, person_id: int) -> dict:
        """
        Retrieve information about a specific person by ID.

        - **Args**:
            - `person_id` (`int`): The ID of the person to retrieve information for.

        - **Returns**:
            - `Dict`: Information about the specified person.
        """
        person = await self._client.person_service.GetPerson(
            req={"person_id": person_id}
        )
        return person

    @log_execution_time
    async def add_person(self, dict_person: dict) -> dict:
        """
        Add a new person to the simulation.

        - **Args**:
            - `dict_person` (`dict`): The person object to add.

        - **Returns**:
            - `Dict`: Response from adding the person.
        """
        person = dict2pb(dict_person, person_pb2.Person())
        if isinstance(person, person_pb2.Person):
            req = person_service.AddPersonRequest(person=person)
        else:
            req = person
        resp: dict = await self._client.person_service.AddPerson(req)
        return resp

    @log_execution_time
    async def set_aoi_schedules(
        self,
        person_id: int,
        target_positions: Union[
            list[Union[int, tuple[int, int]]], Union[int, tuple[int, int]]
        ],
        departure_times: Optional[list[float]] = None,
        modes: Optional[list[TripMode]] = None,
    ):
        """
        Set schedules for a person to visit Areas of Interest (AOIs).

        - **Args**:
            - `person_id` (`int`): The ID of the person whose schedule is being set.
            - `target_positions` (`Union[List[Union[int, Tuple[int, int]]], Union[int, Tuple[int, int]]]`):
              A list of AOI or POI IDs or tuples of (AOI ID, POI ID) that the person will visit.
            - `departure_times` (`Optional[List[float]]`): Departure times for each trip in the schedule.
              If not provided, current time will be used for all trips.
            - `modes` (`Optional[List[int]]`): Travel modes for each trip.
              Defaults to `TRIP_MODE_DRIVE_ONLY` if not specified.
        """
        cur_time = float(await self.get_time())
        if not isinstance(target_positions, list):
            target_positions = [target_positions]
        if departure_times is None:
            departure_times = [cur_time for _ in range(len(target_positions))]
        else:
            for _ in range(len(target_positions) - len(departure_times)):
                departure_times.append(cur_time)
        if modes is None:
            modes = [
                TripMode.TRIP_MODE_DRIVE_ONLY for _ in range(len(target_positions))
            ]
        else:
            for _ in range(len(target_positions) - len(modes)):
                modes.append(TripMode.TRIP_MODE_DRIVE_ONLY)
        _schedules = []
        for target_pos, _time, _mode in zip(target_positions, departure_times, modes):
            if isinstance(target_pos, int):
                if target_pos >= POI_START_ID:
                    poi_id = target_pos
                    end = {
                        "aoi_position": {
                            "aoi_id": self.poi_id_2_aoi_id[poi_id],
                            "poi_id": poi_id,
                        }
                    }
                else:
                    aoi_id = target_pos
                    end = {
                        "aoi_position": {
                            "aoi_id": aoi_id,
                        }
                    }
            else:
                aoi_id, poi_id = target_pos
                end = {"aoi_position": {"aoi_id": aoi_id, "poi_id": poi_id}}
                # activity = ""
            trips = [
                {
                    "mode": _mode,
                    "end": end,
                    "departure_time": _time,
                },
            ]
            _schedules.append(
                {"trips": trips, "loop_count": 1, "departure_time": _time}
            )
        req = {"person_id": person_id, "schedules": _schedules}
        await self._client.person_service.SetSchedule(req)

    @log_execution_time
    async def reset_person_position(
        self,
        person_id: int,
        aoi_id: Optional[int] = None,
        poi_id: Optional[int] = None,
        lane_id: Optional[int] = None,
        s: Optional[float] = None,
    ):
        """
        Reset the position of a person within the simulation.

        - **Args**:
            - `person_id` (`int`): The ID of the person whose position is being reset.
            - `aoi_id` (`Optional[int]`): The ID of the Area of Interest (AOI) where the person should be placed.
            - `poi_id` (`Optional[int]`): The ID of the Point of Interest (POI) within the AOI.
            - `lane_id` (`Optional[int]`): The ID of the lane on which the person should be placed.
            - `s` (`Optional[float]`): The longitudinal position along the lane.
        """
        reset_position = {}
        if aoi_id is not None:
            reset_position["aoi_position"] = {"aoi_id": aoi_id}
            if poi_id is not None:
                reset_position["aoi_position"]["poi_id"] = poi_id
            get_logger().debug(
                f"Setting person {person_id} pos to AoiPosition {reset_position}"
            )
            await self._client.person_service.ResetPersonPosition(
                {"person_id": person_id, "position": reset_position}
            )
        elif lane_id is not None:
            reset_position["lane_position"] = {
                "lane_id": lane_id,
                "s": 0.0,
            }
            if s is not None:
                reset_position["lane_position"]["s"] = s
            get_logger().debug(
                f"Setting person {person_id} pos to LanePosition {reset_position}"
            )
            await self._client.person_service.ResetPersonPosition(
                {"person_id": person_id, "position": reset_position}
            )
        else:
            get_logger().debug(
                f"Neither aoi or lane pos provided for person {person_id} position reset!!"
            )

    @log_execution_time
    def get_around_poi(
        self,
        center: Union[tuple[float, float], Point],
        radius: float,
        poi_type: Union[str, list[str]],
    ) -> list[dict]:
        """
        Get Points of Interest (POIs) around a central point based on type.

        - **Args**:
            - `center` (`Union[Tuple[float, float], Point]`): The central point as a tuple or Point object.
            - `radius` (`float`): The search radius in meters.
            - `poi_type` (`Union[str, List[str]]`): The category or categories of POIs to filter by.

        - **Returns**:
            - `List[Dict]`: A list of dictionaries containing information about the POIs found.
        """
        if isinstance(poi_type, str):
            poi_type = [poi_type]
        transformed_poi_type: list[str] = []
        for t in poi_type:
            if t not in self.poi_cate:
                transformed_poi_type.append(t)
            else:
                transformed_poi_type += self.poi_cate[t]
        poi_type_set = set(transformed_poi_type)
        # query pois within the radius
        assert self._map is not None
        _pois: list[dict] = self._map.query_pois(
            center=center,
            radius=radius,
            return_distance=False,
        )
        # Filter out POIs that do not meet the category prefix
        pois = []
        for poi in _pois:
            catg = poi["category"]
            if catg.split("|")[-1] not in poi_type_set:
                continue
            pois.append(poi)
        return pois


class EnvironmentStarter(Environment):
    """
    The entrypoint of the simulator, used to initialize the simulator and map.

    - **Description**:
        - This class is the core of the simulator, responsible for initializing and managing the simulation environment.
        - It reads parameters from a configuration dictionary, initializes map data, and starts or connects to a simulation server as needed.
    """

    def __init__(
        self,
        map_config: MapConfig,
        simulator_config: SimulatorConfig,
        environment_config: EnvironmentConfig,
    ):
        """
        Environment config

        - **Args**:
            - `map_config` (MapConfig): Map config
            - `simulator_config` (SimulatorConfig): Simulator config
            - `environment_config` (EnvironmentConfig): Environment config
        """
        mapdata = MapData(map_config)
        self._sim_env = ControlSimEnv(
            map_file=map_config.file_path,
            max_day=environment_config.max_day,
            start_step=environment_config.start_tick,
            total_step=environment_config.total_tick,
            log_dir=simulator_config.log_dir,
            primary_node_ip=simulator_config.primary_node_ip,
        )
        self._environment_config = environment_config

        super().__init__(mapdata, self._sim_env.sim_addr, environment_config)

        self._syncer = SyncerClient(
            syncer_address=self._sim_env.syncer_addr,
            name="within-syncer",
            secure=self._server_addr.startswith("https"),
        )
        for _ in range(int(simulator_config.timeout)):
            try:
                self._syncer.init()
                break
            except Exception as e:
                get_logger().warning(
                    f"Failed to connect to syncer {self._sim_env.syncer_addr}, retrying..."
                )
                time.sleep(1)
                continue
        else:
            raise ValueError(
                f"Failed to connect to syncer {self._sim_env.syncer_addr} after {simulator_config.timeout} retries!"
            )

    def to_init_args(self):
        return {
            "map_data": self._map,
            "server_addr": self._server_addr,
            "environment_config": self._environment_config,
            "citizen_ids": self.economy_client._citizen_ids,
            "firm_ids": self.economy_client._firm_ids,
            "bank_ids": self.economy_client._bank_ids,
            "nbs_ids": self.economy_client._nbs_ids,
            "government_ids": self.economy_client._government_ids,
        }

    def close(self):
        if self._sim_env is not None:
            self._sim_env.close()
            self._sim_env = None

    def step(self, n: int):
        if self._syncer is None:
            raise ValueError("Step can only be called in primary node!")
        if n <= 0:
            raise ValueError("`n` must >=1!")
        for _ in range(n):
            self._syncer.step()
