from typing import List, Optional

from pydantic import BaseModel, Field

from ..utils import LLMProviderType

__all__ = [
    "LLMConfig",
    "RedisConfig",
    "PostgreSQLConfig",
    "AvroConfig",
    "MlflowConfig",
    "SimulatorConfig",
    "MapConfig",
    "EnvConfig",
]


class LLMConfig(BaseModel):
    """LLM configuration class."""

    provider: LLMProviderType = Field(...)
    """The type of the LLM provider"""

    base_url: Optional[str] = Field(None)
    """The base URL for the LLM provider"""

    api_key: str = Field(...)
    """API key for accessing the LLM provider"""

    model: str = Field(...)
    """The model to use"""

    semaphore: int = Field(200, ge=1)
    """Semaphore value for LLM operations to avoid rate limit"""


class RedisConfig(BaseModel):
    """Redis configuration class."""

    server: str = Field(...)
    """Redis server address"""

    port: int = Field(...)
    """Port number for Redis connection"""

    password: Optional[str] = Field(None)
    """Password for Redis connection"""

    db: str = Field("0")
    """Database number for Redis connection"""

    timeout: float = Field(60, ge=0)
    """Timeout for Redis connection"""


class PostgreSQLConfig(BaseModel):
    """PostgreSQL configuration class."""

    enabled: bool = Field(True)
    """Whether PostgreSQL storage is enabled"""

    dsn: str = Field(...)
    """Data source name for PostgreSQL"""

    num_workers: int = Field(4, ge=1)
    """Number of workers for PostgreSQL"""


class AvroConfig(BaseModel):
    """Avro configuration class."""

    enabled: bool = Field(False)
    """Whether Avro storage is enabled"""

    path: str = Field(...)
    """Avro file storage path"""


class MlflowConfig(BaseModel):
    """MLflow configuration class."""

    enabled: bool = Field(False)
    """Whether MLflow is enabled"""

    username: Optional[str] = Field(None)
    """Username for MLflow"""

    password: Optional[str] = Field(None)
    """Password for MLflow"""

    mlflow_uri: str = Field(...)
    """URI for MLflow server"""


class SimulatorConfig(BaseModel):
    """Simulator configuration class."""

    log_dir: str = Field("./log")
    """Directory path for saving logs"""

    primary_node_ip: str = Field("localhost")
    """Primary node IP address for distributed simulation. 
    If you want to run the simulation on a single machine, you can set it to "localhost".
    If you want to run the simulation on a distributed machine, you can set it to the IP address of the machine and keep all the ports of the primary node can be accessed from the other nodes (the code will automatically set the ports).
    """


class MapConfig(BaseModel):
    """Map configuration class."""

    file_path: str = Field(...)
    """Path to the map file"""

    cache_path: Optional[str] = Field(None)
    """Cache for the processed map"""


class EnvConfig(BaseModel):
    """Environment configuration class."""

    llm: List[LLMConfig] = Field(..., min_length=1)
    """List of LLM configurations"""

    simulator: SimulatorConfig
    """Simulator configuration"""

    redis: RedisConfig
    """Redis configuration"""

    pgsql: PostgreSQLConfig
    """PostgreSQL configuration"""

    avro: AvroConfig
    """Avro configuration"""

    mlflow: MlflowConfig
    """MLflow configuration"""

    map: MapConfig
    """Map configuration"""
