from __future__ import annotations

from enum import Enum
import logging
from collections.abc import Callable
from typing import Any, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, field_serializer, model_validator

from ..agent import Agent, Block
from ..agent.distribution import Distribution, DistributionConfig
from ..cityagent.blocks import MobilityBlock, EconomyBlock, SocialBlock, OtherBlock

__all__ = [
    "AgentConfig",
]

# TODO: 同BlockClassType
class AgentClassType(str, Enum):
    """
    Defines the types of agent class types.
    """

    CITIZEN = "citizen"
    FIRM = "firm"
    GOVERNMENT = "government"
    BANK = "bank"
    NBS = "nbs"

# TODO: 暂时使用
BLOCK_MAPPING = {
    "mobilityblock": MobilityBlock,
    "economyblock": EconomyBlock,
    "socialblock": SocialBlock,
    "otherblock": OtherBlock,
}

class BlockClassType(str, Enum):
    """
    Defines the types of block class types.
    """

    MOBILITYBLOCK = "mobilityblock"
    ECONOMYBLOCK = "economyblock"
    SOCIALBLOCK = "socialblock"
    OTHERBLOCK = "otherblock"

class AgentConfig(BaseModel):
    """Configuration for different types of agents in the simulation."""

    model_config = ConfigDict(
        use_enum_values=True,
        use_attribute_docstrings=True,
        arbitrary_types_allowed=True,
    )

    agent_class: Union[type[Agent], AgentClassType]
    """The class of the agent"""

    number: int = Field(gt=0)
    """The number of agents"""

    agent_params: Optional[Any] = None
    """Agent configuration"""

    blocks: Optional[dict[Union[type[Block], BlockClassType], Any]] = None
    """Blocks configuration"""

    # Choose one of the following:
    # 1. memory_config_func: Optional[Callable] = None
    # 2. memory_from_file: Optional[str] = None
    # 3. memory_distributions: Optional[dict[str, DistributionConfig]] = None

    memory_config_func: Optional[Callable] = None
    """Memory configuration function"""

    memory_from_file: Optional[str] = None
    """Memory configuration file. If s3 is enabled, the file will be downloaded from S3"""

    memory_distributions: Optional[
        dict[str, Union[Distribution, DistributionConfig]]
    ] = None
    """Memory distributions"""

    @field_serializer("agent_class")
    def serialize_agent_class(self, agent_class, info):
        if isinstance(agent_class, (AgentClassType, str)):
            return agent_class
        else:
            return agent_class.__name__

    @field_serializer("memory_config_func")
    def serialize_memory_config_func(self, memory_config_func, info):
        if memory_config_func is None:
            return None
        else:
            return memory_config_func.__name__

    @field_serializer("memory_distributions")
    def serialize_memory_distributions(self, memory_distributions, info):
        if memory_distributions is None:
            return None
        else:
            result = {}
            for key, value in memory_distributions.items():
                if isinstance(value, Distribution):
                    result[key] = value.__repr__()
                else:
                    result[key] = value
            return result
        
    @model_validator(mode="after")
    def validate_func(self):
        if self.blocks is not None:
            blocks = {}
            for key, value in self.blocks.items():
                if isinstance(key, str):
                    value_ = BLOCK_MAPPING[key].ParamsType(**value)
                    blocks[BLOCK_MAPPING[key]] = value_
            self.blocks = blocks
        return self
