from typing import List, Optional, Union

from pydantic import BaseModel, Field, model_validator

from ..message import RedisConfig
from ..metrics import MlflowConfig
from ..storage import PostgreSQLConfig
from ..s3 import S3Config, S3Client
from ..filesystem import FileSystemClient

__all__ = [
    "EnvConfig",
]


class EnvConfig(BaseModel):
    """Environment configuration class."""

    redis: RedisConfig
    """Redis configuration"""

    pgsql: PostgreSQLConfig
    """PostgreSQL configuration"""

    mlflow: MlflowConfig
    """MLflow configuration"""

    s3: S3Config = Field(default_factory=lambda: S3Config.model_validate({}))
    """S3 configuration, if enabled, the file will be downloaded from S3"""

    home_dir: str = Field(default="./agentsociety_data")
    """Home directory for AgentSociety's webui if s3 is not enabled"""

    enable_avro: bool = Field(default=False)
    """Enable avro storage"""

    @model_validator(mode="after")
    def validate_storage_mutually_exclusive(self):
        """
        Validates that enable_avro and s3.enabled are mutually exclusive.
        - **Description**:
            - Ensures that enable_avro and s3.enabled cannot both be True simultaneously.
            - This prevents conflicts between different storage backends.

        - **Returns**:
            - `EnvConfig`: The validated configuration instance.

        - **Raises**:
            - `ValueError`: If both enable_avro and s3.enabled are True.
        """
        if self.enable_avro and self.s3.enabled:
            raise ValueError("enable_avro and s3.enabled cannot both be True simultaneously")
        return self

    @property
    def fs_client(self) -> Union[S3Client, FileSystemClient]:
        if self.s3.enabled:
            return S3Client(self.s3)
        else:
            return FileSystemClient(self.home_dir)
