from typing import Optional, Union

from pydantic import BaseModel, Field

from ..utils import LLMProviderType

__all__ = [
    "SimConfig",
]


class LLMConfig(BaseModel):
    provider: LLMProviderType = Field(
        ..., description="The type of the LLM provider"
    )
    base_url: Optional[str] = Field(
        None, description="The base URL for the LLM provider"
    )
    api_key: Union[list[str], str] = Field(
        ..., description="API key for accessing the LLM provider"
    )
    model: str = Field(..., description="The model to use")


class RedisConfig(BaseModel):
    server: str = Field(..., description="Redis server address")
    port: int = Field(..., description="Port number for Redis connection")
    password: Optional[str] = Field(None, description="Password for Redis connection")
    username: Optional[str] = Field(None, description="Username for Redis connection")


class SimulatorConfig(BaseModel):
    task_name: str = Field("citysim", description="Name of the simulation task")
    max_day: int = Field(1000, description="Maximum number of days to simulate")
    start_step: int = Field(28800, description="Starting step of the simulation")
    total_step: int = Field(
        24 * 60 * 60 * 365, description="Total number of steps in the simulation"
    )
    log_dir: str = Field("./log", description="Directory path for saving logs")
    steps_per_simulation_step: int = Field(
        300,
        description="Urban space forward time (in seconds) during one simulation forward step",
    )
    steps_per_simulation_day: int = Field(
        3600,
        description="Urban space forward time (in seconds) during one simulation forward day",
    )
    primary_node_ip: str = Field(
        "localhost", description="Primary node IP address for distributed simulation"
    )


class MapConfig(BaseModel):
    file_path: str = Field(..., description="Path to the map file")


class MlflowConfig(BaseModel):
    username: Optional[str] = Field(None, description="Username for MLflow")
    password: Optional[str] = Field(None, description="Password for MLflow")
    mlflow_uri: str = Field(..., description="URI for MLflow server")


class PostgreSQLConfig(BaseModel):
    enabled: Optional[bool] = Field(
        True, description="Whether PostgreSQL storage is enabled"
    )
    dsn: str = Field(..., description="Data source name for PostgreSQL")


class AvroConfig(BaseModel):
    enabled: Optional[bool] = Field(
        False, description="Whether Avro storage is enabled"
    )
    path: str = Field(..., description="Avro file storage path")


class MetricConfig(BaseModel):
    mlflow: Optional[MlflowConfig] = Field(None)


class SimStatus(BaseModel):
    simulator_activated: bool = False


class SimConfig(BaseModel):
    llm_config: Optional["LLMConfig"] = None
    simulator_config: Optional["SimulatorConfig"] = None
    redis: Optional["RedisConfig"] = None
    map_config: Optional["MapConfig"] = None
    metric_config: Optional["MetricConfig"] = None
    pgsql: Optional["PostgreSQLConfig"] = None
    avro: Optional["AvroConfig"] = None
    simulator_server_address: Optional[str] = None
    status: Optional["SimStatus"] = SimStatus()

    @property
    def prop_llm_config(self) -> "LLMConfig":
        return self.llm_config  # type:ignore

    @property
    def prop_status(self) -> "SimStatus":
        return self.status  # type:ignore

    @property
    def prop_simulator_config(self) -> "SimulatorConfig":
        return self.simulator_config  # type:ignore

    @property
    def prop_redis(self) -> "RedisConfig":
        return self.redis  # type:ignore

    @property
    def prop_map_config(self) -> "MapConfig":
        return self.map_config  # type:ignore

    @property
    def prop_avro_config(self) -> "AvroConfig":
        return self.avro  # type:ignore

    @property
    def prop_postgre_sql_config(self) -> "PostgreSQLConfig":
        return self.pgsql  # type:ignore

    @property
    def prop_simulator_server_address(self) -> str:
        return self.simulator_server_address  # type:ignore

    @property
    def prop_metric_config(self) -> "MetricConfig":
        return self.metric_config  # type:ignore

    def SetLLMConfig(
        self, provider: LLMProviderType, api_key: Union[list[str], str], model: str, base_url: Optional[str] = None
    ) -> "SimConfig":
        self.llm_config = LLMConfig(
            provider=provider, api_key=api_key, model=model, base_url=base_url
        )
        return self

    def SetSimulatorConfig(
        self,
        task_name: str = "citysim",
        max_day: int = 1000,
        start_step: int = 28800,
        total_step: int = 24 * 60 * 60 * 365,
        log_dir: str = "./log",
        steps_per_simulation_step: int = 300,
        steps_per_simulation_day: int = 3600,
        primary_node_ip: str = "localhost",
    ) -> "SimConfig":
        self.simulator_config = SimulatorConfig(
            task_name=task_name,
            max_day=max_day,
            start_step=start_step,
            total_step=total_step,
            log_dir=log_dir,
            steps_per_simulation_step=steps_per_simulation_step,
            steps_per_simulation_day=steps_per_simulation_day,
            primary_node_ip=primary_node_ip,
        )
        return self

    def SetRedis(
        self,
        server: str,
        port: int,
        username: Optional[str] = None,
        password: Optional[str] = None,
    ) -> "SimConfig":
        self.redis = RedisConfig(
            server=server, port=port, username=username, password=password
        )
        return self

    def SetMapConfig(self, file_path: str) -> "SimConfig":
        self.map_config = MapConfig(file_path=file_path)
        return self

    def SetMetricConfig(
        self, username: str, password: str, mlflow_uri: str
    ) -> "SimConfig":
        self.metric_config = MetricConfig(
            mlflow=MlflowConfig(
                username=username, password=password, mlflow_uri=mlflow_uri
            )
        )
        return self

    def SetAvro(self, path: str, enabled: bool = False) -> "SimConfig":
        self.avro = AvroConfig(path=path, enabled=enabled)
        return self

    def SetPostgreSql(self, dsn: str, enabled: bool = False) -> "SimConfig":
        self.pgsql = PostgreSQLConfig(dsn=dsn, enabled=enabled)
        return self

    def SetServerAddress(self, simulator_server_address: str) -> "SimConfig":
        self.simulator_server_address = simulator_server_address
        return self

    def model_dump(self, *args, **kwargs):
        exclude_fields = {
            "status",
        }
        data = super().model_dump(*args, **kwargs)
        return {k: v for k, v in data.items() if k not in exclude_fields}


if __name__ == "__main__":
    config = (
        SimConfig()
        .SetLLMRequest("openai", "key", "model")  # type:ignore
        .SetRedis("server", 6379, "username", "password")
        .SetMapRequest("./path/to/map")
        .SetMetricRequest("username", "password", "uri")
        .SetPostgreSql("dsn", True)
    )
    print(config.llm_config)
