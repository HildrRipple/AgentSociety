from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any, List, Literal, Optional, Union

from pydantic import BaseModel, Field, ConfigDict

from ..utils import DistributionType, AgentClassType

__all__ = [
    "AgentConfig",
    "DistributionConfig",
]


class DistributionConfig(BaseModel):
    """Configuration for different types of distributions used in the simulation."""

    model_config = ConfigDict(use_enum_values=True, use_attribute_docstrings=True)

    dist_type: DistributionType = Field(...)
    """The type of the distribution"""

    choices: Optional[list[Any]] = None
    """A list of possible discrete values - used for [CHOICE] type"""

    weights: Optional[list[float]] = None
    """Weights corresponding to each discrete choice - used for [CHOICE] type"""

    min_value: Optional[Union[int, float]] = None
    """Minimum value for continuous distributions - used for [UNIFORM_INT, UNIFORM_FLOAT, NORMAL] type"""

    max_value: Optional[Union[int, float]] = None
    """Maximum value for continuous distributions - used for [UNIFORM_INT, UNIFORM_FLOAT, NORMAL] type"""

    mean: Optional[float] = None
    """Mean value for the distribution if applicable - used for [NORMAL] type"""

    std: Optional[float] = None
    """Standard deviation for the distribution if applicable - used for [NORMAL] type"""

    value: Optional[Any] = None
    """A fixed value that can be used instead of a distribution - used for [CONSTANT] type"""


class AgentConfig(BaseModel):
    """Configuration for different types of agents in the simulation."""

    model_config = ConfigDict(use_enum_values=True, use_attribute_docstrings=True)

    agent_class: Union[type, AgentClassType]
    """The class of the agent"""

    number: int = Field(gt=0)
    """The number of agents"""

    agent_config: Optional[dict[str, Any]] = None
    """Agent configuration"""

    # Choose one of the following:
    # 1. memory_config_func: Optional[Callable] = None
    # 2. memory_from_file: Optional[str] = None
    # 3. memory_distributions: Optional[dict[str, DistributionConfig]] = None

    memory_config_func: Optional[Callable] = None
    """Memory configuration function"""

    memory_from_file: Optional[str] = None
    """Memory configuration file"""

    memory_distributions: Optional[dict[str, DistributionConfig]] = None
    """Memory distributions"""
