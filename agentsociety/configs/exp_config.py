from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any, List, Literal, Optional, Union

from pydantic import BaseModel, Field, ConfigDict

from ..survey import Survey
from ..utils import DistributionType, MetricType, WorkflowType

class WorkflowStep(BaseModel):
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
    
    target_agent: Optional[list] = None
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
    
    description: Optional[str] = "None"
    """A descriptive text explaining the workflow step"""


class MetricExtractor(BaseModel):
    """Configuration for extracting metrics during simulation."""
    
    model_config = ConfigDict(use_enum_values=True, use_attribute_docstrings=True)

    type: MetricType = Field(MetricType.FUNCTION)
    """The type of metric extraction; defaults to FUNCTION"""
    
    func: Optional[Callable] = None
    """The function that extracts the metric - used for [FUNCTION] type"""
    
    step_interval: int = 10
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


class MemoryConfig(BaseModel):
    """Configuration for agent memory settings."""
    
    model_config = ConfigDict(use_enum_values=True, use_attribute_docstrings=True)

    memory_config_func: Optional[dict[type[Any], Callable]] = None
    """A dictionary mapping agent types to functions that return memory configurations"""
    
    memory_from_file: Optional[dict[type[Any], str]] = None
    """A dictionary mapping agent types to file paths containing memory configurations"""
    
    memory_distributions: Optional[dict[str, DistributionConfig]] = None
    """A dictionary mapping citizen agents profile attributes to distribution configurations"""


class AgentConfig(BaseModel):
    """Configuration for different types of agents in the simulation."""
    
    model_config = ConfigDict(use_enum_values=True, use_attribute_docstrings=True)

    number_of_citizen: int = Field(1)
    """Number of citizens"""
    
    number_of_firm: int = Field(1)
    """Number of firms"""
    
    number_of_government: int = Field(1)
    """Number of governments"""
    
    number_of_bank: int = Field(1)
    """Number of banks"""
    
    number_of_nbs: int = Field(1)
    """Number of neighborhood-based services"""
    
    group_size: int = Field(100)
    """Size of agent groups"""
    
    embedding_model: Any = Field(None)
    """Embedding model"""
    
    extra_agent_class: Optional[dict[Any, int]] = None
    """Additional agent classes and their quantities"""
    
    agent_class_configs: Optional[dict[Any, dict[str, Any]]] = None
    """Configuration settings for different agent classes"""
    
    init_func: Optional[list[Callable[[Any], None]]] = None
    """Initialization functions for agents"""
    
    memory_config: Optional[MemoryConfig] = None
    """Memory configuration for agents"""

    @property
    def prop_memory_config(self) -> MemoryConfig:
        if self.memory_config is None:
            return MemoryConfig(
                memory_config_func=None,
                memory_from_file=None,
                memory_distributions=None,
            )
        return self.memory_config

    def SetMemoryConfig(
        self,
        memory_config_func: Optional[dict[type[Any], Callable]] = None,
        memory_from_file: Optional[dict[Any, str]] = None,
        memory_distributions: Optional[dict[str, DistributionConfig]] = None,
    ) -> "AgentConfig":
        self.memory_config = MemoryConfig(
            memory_config_func=memory_config_func,
            memory_from_file=memory_from_file,
            memory_distributions=memory_distributions,
        )
        return self


class EnvironmentConfig(BaseModel):
    """Configuration for the simulation environment."""
    
    model_config = ConfigDict(use_enum_values=True, use_attribute_docstrings=True)

    weather: str = Field(default="The weather is sunny")
    """Current weather condition in the environment"""
    
    temperature: str = Field(default="The temperature is 23C")
    """Current temperature in the environment"""
    
    workday: bool = Field(default=True)
    """Indicates if it's a working day"""
    
    other_information: str = Field(default="")
    """Additional environment information"""


class MessageInterceptConfig(BaseModel):
    """Configuration for message interception in the simulation."""
    
    model_config = ConfigDict(use_enum_values=True, use_attribute_docstrings=True)

    mode: Optional[Union[Literal["point"], Literal["edge"]]] = None
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

    agent_config: AgentConfig
    """Configuration for agents"""
    
    workflow: List[WorkflowStep]
    """List of workflow steps"""
    
    environment: EnvironmentConfig = EnvironmentConfig()
    """Environment configuration"""
    
    message_intercept: Optional[MessageInterceptConfig] = None
    """Message interception configuration"""
    
    metric_extractors: Optional[list[MetricExtractor]] = None
    """List of metric extractors"""
    
    logging_level: str = Field("info")
    """Logging level for the experiment"""
    
    exp_name: str = Field("default_experiment")
    """Name of the experiment"""
    
    llm_semaphore: int = Field(200)
    """Semaphore value for LLM operations"""

    def SetAgentConfig(
        self,
        number_of_citizen: int = 1,
        number_of_firm: int = 1,
        number_of_government: int = 1,
        number_of_bank: int = 1,
        number_of_nbs: int = 1,
        group_size: int = 100,
        embedding_model: Any = None,
        extra_agent_class: Optional[dict[Any, int]] = None,
        agent_class_configs: Optional[dict[Any, dict[str, Any]]] = None,
        memory_config: Optional[MemoryConfig] = None,
        init_func: Optional[list[Callable[[Any], None]]] = None,
    ) -> "ExpConfig":
        self.agent_config = AgentConfig(
            number_of_citizen=number_of_citizen,
            number_of_firm=number_of_firm,
            number_of_government=number_of_government,
            number_of_bank=number_of_bank,
            number_of_nbs=number_of_nbs,
            group_size=group_size,
            embedding_model=embedding_model,
            extra_agent_class=extra_agent_class,
            agent_class_configs=agent_class_configs,
            memory_config=memory_config,
            init_func=init_func,
        )
        return self

    def SetMemoryConfig(
        self,
        memory_config_func: Optional[dict[type[Any], Callable]] = None,
        memory_from_file: Optional[dict[Any, str]] = None,
        memory_distributions: Optional[dict[str, DistributionConfig]] = None,
    ) -> "ExpConfig":
        assert self.agent_config is not None
        self.agent_config.memory_config = MemoryConfig(
            memory_config_func=memory_config_func,
            memory_from_file=memory_from_file,
            memory_distributions=memory_distributions,
        )
        return self

    def SetEnvironment(
        self,
        weather: str = "The weather is normal",
        temperature: str = "The temperature is normal",
        workday: bool = True,
        other_information: str = "",
    ) -> "ExpConfig":
        self.environment = EnvironmentConfig(
            weather=weather,
            temperature=temperature,
            workday=workday,
            other_information=other_information,
        )
        return self

    def SetMessageIntercept(
        self,
        mode: Optional[Union[Literal["point"], Literal["edge"]]] = None,
        max_violation_time: int = 3,
        message_interceptor_blocks: Optional[list[Any]] = None,
        message_listener: Optional[Any] = None,
    ) -> "ExpConfig":
        self.message_intercept = MessageInterceptConfig(
            mode=mode,
            max_violation_time=max_violation_time,
            message_interceptor_blocks=message_interceptor_blocks,
            message_listener=message_listener,
        )
        return self

    def SetMetricExtractors(self, metric_extractors: list[MetricExtractor]):
        self.metric_extractors = metric_extractors
        return self

    def SetWorkFlow(self, workflows: list[WorkflowStep]):
        self.workflow = workflows
        return self
