from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field

from ..survey import Survey
from ..utils import DistributionType, MetricType, WorkflowType

# if TYPE_CHECKING:
#     from ..simulation import AgentSimulation


class WorkflowStep(BaseModel):
    type: WorkflowType = Field(..., description="The type of the workflow step")
    func: Optional[Callable] = (
        None  # Optional function to be executed during this step - used for [FUNCTION, INTERVENE] type
    )
    days: float = (
        1.0  # Duration (in days) for which this step lasts - used for [RUN] type
    )
    times: int = 1  # Number of repetitions for this step - used for [RUN] type
    target_agent: Optional[list] = (
        None  # List specifying the agents targeted by this step - used for [INTERVIEW, SURVEY, UPDATE_STATE_INTERVENE, MESSAGE_INTERVENE] type
    )
    interview_message: Optional[str] = (
        None  # Optional message used for interviews during this step - used for [INTERVIEW] type
    )
    survey: Optional[Survey] = (
        None  # Optional survey instance associated with this step - used for [SURVEY] type
    )
    key: Optional[str] = (
        None  # Optional key identifier for the step - used for [ENVIRONMENT_INTERVENE, UPDATE_STATE_INTERVENE] type
    )
    value: Optional[Any] = (
        None  # Optional value associated with the step - used for [ENVIRONMENT_INTERVENE, UPDATE_STATE_INTERVENE] type
    )
    intervene_message: Optional[str] = (
        None  # Optional message used for interventions - used for [MESSAGE_INTERVENE] type
    )
    description: Optional[str] = (
        "None"  # A descriptive text explaining the workflow step
    )


class MetricExtractor(BaseModel):
    type: MetricType = Field(
        MetricType.FUNCTION,
        description="The type of metric extraction; defaults to FUNCTION",
    )
    func: Optional[Callable] = (
        None  # The function that extracts the metric - used for [FUNCTION] type
    )
    step_interval: int = (
        10  # Frequency interval (in simulation steps) for metric extraction
    )
    target_agent: Optional[list] = (
        None  # List specifying the agents from which to extract metrics - used for [STATE] type
    )
    key: Optional[str] = (
        None  # Optional key to store or identify the extracted metric - used for [STATE] type
    )
    method: Optional[Literal["mean", "sum", "max", "min"]] = (
        "sum"  # Aggregation method applied to the metric values - used for [STATE] type
    )
    extract_time: int = 0  # The simulation time or step at which extraction occurs
    description: str = "None"  # A descriptive text explaining the metric extractor


class DistributionConfig(BaseModel):
    dist_type: DistributionType = Field(..., description="The type of the distribution")
    choices: Optional[List[Any]] = (
        None  # A list of possible discrete values - used for [CHOICE] type
    )
    weights: Optional[List[float]] = (
        None  # Weights corresponding to each discrete choice - used for [CHOICE] type
    )
    min_value: Optional[Union[int, float]] = (
        None  # Minimum value for continuous distributions - used for [UNIFORM_INT, UNIFORM_FLOAT, NORMAL] type
    )
    max_value: Optional[Union[int, float]] = (
        None  # Maximum value for continuous distributions - used for [UNIFORM_INT, UNIFORM_FLOAT, NORMAL] type
    )
    mean: Optional[float] = (
        None  # Mean value for the distribution if applicable - used for [NORMAL] type
    )
    std: Optional[float] = (
        None  # Standard deviation for the distribution if applicable - used for [NORMAL] type
    )
    value: Optional[Any] = (
        None  # A fixed value that can be used instead of a distribution - used for [CONSTANT] type
    )


class MemoryConfig(BaseModel):
    memory_config_func: Optional[Dict[type[Any], Callable]] = (
        None  # A dictionary mapping agent types to functions that return memory configurations
    )
    memory_from_file: Optional[Dict[type[Any], str]] = (
        None  # A dictionary mapping agent types to file paths containing memory configurations
    )
    memory_distributions: Optional[Dict[str, DistributionConfig]] = (
        None  # A dictionary mapping citizen agents profile attributes to distribution configurations
    )


class AgentConfig(BaseModel):

    number_of_citizen: int = Field(1, description="Number of citizens")
    number_of_firm: int = Field(1, description="Number of firms")
    number_of_government: int = Field(1, description="Number of governments")
    number_of_bank: int = Field(1, description="Number of banks")
    number_of_nbs: int = Field(1, description="Number of neighborhood-based services")
    group_size: int = Field(100, description="Size of agent groups")
    embedding_model: Any = Field(None, description="Embedding model")
    extra_agent_class: Optional[dict[Any, int]] = None
    agent_class_configs: Optional[dict[Any, dict[str, Any]]] = None
    init_func: Optional[list[Callable[[Any], None]]] = None
    memory_config: Optional[MemoryConfig] = None

    @property
    def prop_memory_config(self) -> MemoryConfig:
        if self.memory_config is None:
            return MemoryConfig(
                memory_config_func=None,
                memory_from_file=None,
                memory_distributions=None,
            )
        return self.memory_config  # type:ignore

    def SetMemoryConfig(
        self,
        memory_config_func: Optional[Dict[type[Any], Callable]] = None,
        memory_from_file: Optional[Dict[Any, str]] = None,
        memory_distributions: Optional[Dict[str, DistributionConfig]] = None,
    ) -> "AgentConfig":
        self.memory_config = MemoryConfig(
            memory_config_func=memory_config_func,
            memory_from_file=memory_from_file,
            memory_distributions=memory_distributions,
        )
        return self


class EnvironmentConfig(BaseModel):
    weather: str = Field(default="The weather is sunny")
    temperature: str = Field(default="The temperature is 23C")
    workday: bool = Field(default=True)
    other_information: str = Field(default="")


class MessageInterceptConfig(BaseModel):
    mode: Optional[Union[Literal["point"], Literal["edge"]]] = None
    max_violation_time: int = 3
    message_interceptor_blocks: Optional[list[Any]] = None
    message_listener: Optional[Any] = None


class ExpConfig(BaseModel):
    agent_config: Optional[AgentConfig] = None
    workflow: Optional[list[WorkflowStep]] = None
    environment: Optional[EnvironmentConfig] = EnvironmentConfig()
    message_intercept: Optional[MessageInterceptConfig] = None
    metric_extractors: Optional[list[MetricExtractor]] = None
    logging_level: int = Field(logging.WARNING)
    exp_name: str = Field("default_experiment")
    llm_semaphore: int = Field(200)

    @property
    def prop_agent_config(self) -> AgentConfig:
        return self.agent_config  # type:ignore

    @property
    def prop_workflow(self) -> list[WorkflowStep]:
        return self.workflow  # type:ignore

    @property
    def prop_environment(self) -> EnvironmentConfig:
        return self.environment  # type:ignore

    @property
    def prop_message_intercept(self) -> MessageInterceptConfig:
        return self.message_intercept  # type:ignore

    @property
    def prop_metric_extractors(
        self,
    ) -> list[MetricExtractor]:
        return self.metric_extractors  # type:ignore

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
        memory_config_func: Optional[Dict[type[Any], Callable]] = None,
        memory_from_file: Optional[Dict[Any, str]] = None,
        memory_distributions: Optional[Dict[str, DistributionConfig]] = None,
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
