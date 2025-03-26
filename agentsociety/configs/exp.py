from __future__ import annotations

from collections.abc import Callable
from typing import Any, List, Literal, Optional, Union

from pydantic import BaseModel, Field, ConfigDict, model_validator

from ..survey import Survey
from ..utils import MetricType, WorkflowType

__all__ = [
    "WorkflowStepConfig",
    "MetricExtractorConfig",
    "EnvironmentConfig",
    "MessageInterceptConfig",
    "ExpConfig",
]


class WorkflowStepConfig(BaseModel):
    """Represents a step in the workflow process."""

    model_config = ConfigDict(use_enum_values=True, use_attribute_docstrings=True)

    type: WorkflowType = Field(...)
    """The type of the workflow step"""

    func: Optional[Callable] = None
    """Optional function to be executed during this step - used for [FUNCTION, INTERVENE] type"""

    days: float = 1.0
    """Duration (in days) for which this step lasts - used for [RUN] type"""

    times: int = 1
    """Number of repetitions for this step - used for [RUN] type"""

    ticks_per_step: int = 300
    """Number of ticks per step - used for [RUN, STEP] type. For example, if it is 300, then the step will run 300 ticks in the environment."""

    target_agent: Optional[list[int]] = None
    """List specifying the agents targeted by this step - used for [INTERVIEW, SURVEY, UPDATE_STATE_INTERVENE, MESSAGE_INTERVENE] type"""

    interview_message: Optional[str] = None
    """Optional message used for interviews during this step - used for [INTERVIEW] type"""

    survey: Optional[Survey] = None
    """Optional survey instance associated with this step - used for [SURVEY] type"""

    key: Optional[str] = None
    """Optional key identifier for the step - used for [ENVIRONMENT_INTERVENE, UPDATE_STATE_INTERVENE] type"""

    value: Optional[Any] = None
    """Optional value associated with the step - used for [ENVIRONMENT_INTERVENE, UPDATE_STATE_INTERVENE] type"""

    intervene_message: Optional[str] = None
    """Optional message used for interventions - used for [MESSAGE_INTERVENE] type"""

    description: Optional[str] = None
    """A descriptive text explaining the workflow step"""


class MetricExtractorConfig(BaseModel):
    """Configuration for extracting metrics during simulation."""

    model_config = ConfigDict(use_enum_values=True, use_attribute_docstrings=True)

    type: MetricType = Field(MetricType.FUNCTION)
    """The type of metric extraction; defaults to FUNCTION"""

    func: Optional[Callable] = None
    """The function that extracts the metric - used for [FUNCTION] type"""

    step_interval: int = Field(10, ge=1)
    """Frequency interval (in simulation steps) for metric extraction"""

    target_agent: Optional[list] = None
    """List specifying the agents from which to extract metrics - used for [STATE] type"""

    key: Optional[str] = None
    """Optional key to store or identify the extracted metric - used for [STATE] type"""

    method: Optional[Literal["mean", "sum", "max", "min"]] = "sum"
    """Aggregation method applied to the metric values - used for [STATE] type"""

    extract_time: int = 0
    """The simulation time or step at which extraction occurs"""

    description: str = "None"
    """A descriptive text explaining the metric extractor"""

    # customize validator for target_agent and key
    @model_validator(mode="after")
    def validate_target_agent(self):
        if self.type == MetricType.STATE:
            if self.target_agent is None:
                raise ValueError("target_agent is required for STATE type")
            if self.key is None:
                raise ValueError("key is required for STATE type")
        return self


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


class MessageInterceptConfig(BaseModel):
    """Configuration for message interception in the simulation."""

    model_config = ConfigDict(use_enum_values=True, use_attribute_docstrings=True)

    mode: Union[Literal["point"], Literal["edge"]]
    """Mode of message interception"""

    max_violation_time: int = 3
    """Maximum number of allowed violations"""

    message_interceptor_blocks: Optional[list[Any]] = None
    """List of message interceptor blocks"""

    message_listener: Optional[Any] = None
    """Message listener configuration"""


class ExpConfig(BaseModel):
    """Main configuration for the experiment."""

    model_config = ConfigDict(use_enum_values=True, use_attribute_docstrings=True)

    name: str = Field("default_experiment")
    """Name of the experiment"""

    workflow: List[WorkflowStepConfig] = Field(..., min_length=1)
    """List of workflow steps"""

    environment: EnvironmentConfig
    """Environment configuration"""

    message_intercept: Optional[MessageInterceptConfig] = None
    """Message interception configuration"""

    metric_extractors: Optional[list[MetricExtractorConfig]] = None
    """List of metric extractors"""
