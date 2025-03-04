from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Dict, Literal, Optional, Union, List

from pydantic import BaseModel, Field

from ..utils import WorkflowType, DistributionType

# if TYPE_CHECKING:
#     from ..simulation import AgentSimulation


class WorkflowStep(BaseModel):
    type: WorkflowType
    func: Optional[Callable] = None
    days: int = 1
    times: int = 1
    description: str = "no description"


class DistributionConfig(BaseModel):
    """
    Configuration for a distribution.
    - **Description**:
        - Defines the parameters for a specific distribution type.

    - **Args**:
        - `dist_type` (DistributionType): Type of distribution
        - Various parameters specific to each distribution type

    - **Returns**:
        - None
    """
    dist_type: DistributionType
    choices: Optional[List[Any]] = None
    weights: Optional[List[float]] = None
    min_value: Optional[Union[int, float]] = None
    max_value: Optional[Union[int, float]] = None
    mean: Optional[float] = None
    std: Optional[float] = None
    value: Optional[Any] = None


class MemoryConfig(BaseModel):
    memory_from_file: Optional[Dict[Any, str]] = None
    memory_config_func: Optional[Dict[type[Any], Callable]] = None
    memory_distributions: Optional[Dict[str, DistributionConfig]] = None


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
            return MemoryConfig()
        return self.memory_config  # type:ignore
    
    def SetMemoryConfig(
        self,
        memory_from_file: Optional[Dict[Any, str]] = None,
        memory_config_func: Optional[Dict[type[Any], Callable]] = None,
        memory_distributions: Optional[Dict[str, DistributionConfig]] = None,
    ) -> "AgentConfig":
        self.memory_config = MemoryConfig(
            memory_from_file=memory_from_file,
            memory_config_func=memory_config_func,
            memory_distributions=memory_distributions,
        )
        return self
    
class EnvironmentConfig(BaseModel):
    weather: str = Field(default="The weather is normal")
    temperature: str = Field(default="The temperature is normal")
    day: str = Field(default="Workday")
    global_prompt: str = Field(default="")

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
    metric_extractors: Optional[list[tuple[int, Callable]]] = None
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
    ) -> list[tuple[int, Callable]]:
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

    def SetEnvironment(
        self,
        weather: str = "The weather is normal",
        temperature: str = "The temperature is normal",
        day: str = "Workday",
        global_prompt: str = "",
    ) -> "ExpConfig":
        self.environment = EnvironmentConfig(
            weather=weather,
            temperature=temperature,
            day=day,
            global_prompt=global_prompt,
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

    def SetMetricExtractors(self, metric_extractors: list[tuple[int, Callable]]):
        self.metric_extractors = metric_extractors
        return self

    def SetWorkFlow(self, workflows: list[WorkflowStep]):
        self.workflow = workflows
        return self
