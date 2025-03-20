# {py:mod}`agentsociety.configs.exp_config`

```{py:module} agentsociety.configs.exp_config
```

```{autodoc2-docstring} agentsociety.configs.exp_config
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`WorkflowStep <agentsociety.configs.exp_config.WorkflowStep>`
  -
* - {py:obj}`MetricExtractor <agentsociety.configs.exp_config.MetricExtractor>`
  -
* - {py:obj}`DistributionConfig <agentsociety.configs.exp_config.DistributionConfig>`
  -
* - {py:obj}`MemoryConfig <agentsociety.configs.exp_config.MemoryConfig>`
  -
* - {py:obj}`AgentConfig <agentsociety.configs.exp_config.AgentConfig>`
  -
* - {py:obj}`EnvironmentConfig <agentsociety.configs.exp_config.EnvironmentConfig>`
  -
* - {py:obj}`MessageInterceptConfig <agentsociety.configs.exp_config.MessageInterceptConfig>`
  -
* - {py:obj}`ExpConfig <agentsociety.configs.exp_config.ExpConfig>`
  -
````

### API

`````{py:class} WorkflowStep(/, **data: typing.Any)
:canonical: agentsociety.configs.exp_config.WorkflowStep

Bases: {py:obj}`pydantic.BaseModel`

````{py:attribute} type
:canonical: agentsociety.configs.exp_config.WorkflowStep.type
:type: agentsociety.utils.WorkflowType
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.WorkflowStep.type
```

````

````{py:attribute} func
:canonical: agentsociety.configs.exp_config.WorkflowStep.func
:type: typing.Optional[collections.abc.Callable]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.WorkflowStep.func
```

````

````{py:attribute} days
:canonical: agentsociety.configs.exp_config.WorkflowStep.days
:type: float
:value: >
   1.0

```{autodoc2-docstring} agentsociety.configs.exp_config.WorkflowStep.days
```

````

````{py:attribute} times
:canonical: agentsociety.configs.exp_config.WorkflowStep.times
:type: int
:value: >
   1

```{autodoc2-docstring} agentsociety.configs.exp_config.WorkflowStep.times
```

````

````{py:attribute} target_agent
:canonical: agentsociety.configs.exp_config.WorkflowStep.target_agent
:type: typing.Optional[list]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.WorkflowStep.target_agent
```

````

````{py:attribute} interview_message
:canonical: agentsociety.configs.exp_config.WorkflowStep.interview_message
:type: typing.Optional[str]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.WorkflowStep.interview_message
```

````

````{py:attribute} survey
:canonical: agentsociety.configs.exp_config.WorkflowStep.survey
:type: typing.Optional[agentsociety.survey.Survey]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.WorkflowStep.survey
```

````

````{py:attribute} key
:canonical: agentsociety.configs.exp_config.WorkflowStep.key
:type: typing.Optional[str]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.WorkflowStep.key
```

````

````{py:attribute} value
:canonical: agentsociety.configs.exp_config.WorkflowStep.value
:type: typing.Optional[typing.Any]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.WorkflowStep.value
```

````

````{py:attribute} intervene_message
:canonical: agentsociety.configs.exp_config.WorkflowStep.intervene_message
:type: typing.Optional[str]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.WorkflowStep.intervene_message
```

````

````{py:attribute} description
:canonical: agentsociety.configs.exp_config.WorkflowStep.description
:type: typing.Optional[str]
:value: >
   'None'

```{autodoc2-docstring} agentsociety.configs.exp_config.WorkflowStep.description
```

````

`````

`````{py:class} MetricExtractor(/, **data: typing.Any)
:canonical: agentsociety.configs.exp_config.MetricExtractor

Bases: {py:obj}`pydantic.BaseModel`

````{py:attribute} type
:canonical: agentsociety.configs.exp_config.MetricExtractor.type
:type: agentsociety.utils.MetricType
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.MetricExtractor.type
```

````

````{py:attribute} func
:canonical: agentsociety.configs.exp_config.MetricExtractor.func
:type: typing.Optional[collections.abc.Callable]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.MetricExtractor.func
```

````

````{py:attribute} step_interval
:canonical: agentsociety.configs.exp_config.MetricExtractor.step_interval
:type: int
:value: >
   10

```{autodoc2-docstring} agentsociety.configs.exp_config.MetricExtractor.step_interval
```

````

````{py:attribute} target_agent
:canonical: agentsociety.configs.exp_config.MetricExtractor.target_agent
:type: typing.Optional[list]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.MetricExtractor.target_agent
```

````

````{py:attribute} key
:canonical: agentsociety.configs.exp_config.MetricExtractor.key
:type: typing.Optional[str]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.MetricExtractor.key
```

````

````{py:attribute} method
:canonical: agentsociety.configs.exp_config.MetricExtractor.method
:type: typing.Optional[typing.Literal[mean, sum, max, min]]
:value: >
   'sum'

```{autodoc2-docstring} agentsociety.configs.exp_config.MetricExtractor.method
```

````

````{py:attribute} extract_time
:canonical: agentsociety.configs.exp_config.MetricExtractor.extract_time
:type: int
:value: >
   0

```{autodoc2-docstring} agentsociety.configs.exp_config.MetricExtractor.extract_time
```

````

````{py:attribute} description
:canonical: agentsociety.configs.exp_config.MetricExtractor.description
:type: str
:value: >
   'None'

```{autodoc2-docstring} agentsociety.configs.exp_config.MetricExtractor.description
```

````

`````

`````{py:class} DistributionConfig(/, **data: typing.Any)
:canonical: agentsociety.configs.exp_config.DistributionConfig

Bases: {py:obj}`pydantic.BaseModel`

````{py:attribute} dist_type
:canonical: agentsociety.configs.exp_config.DistributionConfig.dist_type
:type: agentsociety.utils.DistributionType
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.DistributionConfig.dist_type
```

````

````{py:attribute} choices
:canonical: agentsociety.configs.exp_config.DistributionConfig.choices
:type: typing.Optional[list[typing.Any]]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.DistributionConfig.choices
```

````

````{py:attribute} weights
:canonical: agentsociety.configs.exp_config.DistributionConfig.weights
:type: typing.Optional[list[float]]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.DistributionConfig.weights
```

````

````{py:attribute} min_value
:canonical: agentsociety.configs.exp_config.DistributionConfig.min_value
:type: typing.Optional[typing.Union[int, float]]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.DistributionConfig.min_value
```

````

````{py:attribute} max_value
:canonical: agentsociety.configs.exp_config.DistributionConfig.max_value
:type: typing.Optional[typing.Union[int, float]]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.DistributionConfig.max_value
```

````

````{py:attribute} mean
:canonical: agentsociety.configs.exp_config.DistributionConfig.mean
:type: typing.Optional[float]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.DistributionConfig.mean
```

````

````{py:attribute} std
:canonical: agentsociety.configs.exp_config.DistributionConfig.std
:type: typing.Optional[float]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.DistributionConfig.std
```

````

````{py:attribute} value
:canonical: agentsociety.configs.exp_config.DistributionConfig.value
:type: typing.Optional[typing.Any]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.DistributionConfig.value
```

````

`````

`````{py:class} MemoryConfig(/, **data: typing.Any)
:canonical: agentsociety.configs.exp_config.MemoryConfig

Bases: {py:obj}`pydantic.BaseModel`

````{py:attribute} memory_config_func
:canonical: agentsociety.configs.exp_config.MemoryConfig.memory_config_func
:type: typing.Optional[dict[type[typing.Any], collections.abc.Callable]]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.MemoryConfig.memory_config_func
```

````

````{py:attribute} memory_from_file
:canonical: agentsociety.configs.exp_config.MemoryConfig.memory_from_file
:type: typing.Optional[dict[type[typing.Any], str]]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.MemoryConfig.memory_from_file
```

````

````{py:attribute} memory_distributions
:canonical: agentsociety.configs.exp_config.MemoryConfig.memory_distributions
:type: typing.Optional[dict[str, agentsociety.configs.exp_config.DistributionConfig]]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.MemoryConfig.memory_distributions
```

````

`````

`````{py:class} AgentConfig(/, **data: typing.Any)
:canonical: agentsociety.configs.exp_config.AgentConfig

Bases: {py:obj}`pydantic.BaseModel`

````{py:attribute} number_of_citizen
:canonical: agentsociety.configs.exp_config.AgentConfig.number_of_citizen
:type: int
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.number_of_citizen
```

````

````{py:attribute} number_of_firm
:canonical: agentsociety.configs.exp_config.AgentConfig.number_of_firm
:type: int
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.number_of_firm
```

````

````{py:attribute} number_of_government
:canonical: agentsociety.configs.exp_config.AgentConfig.number_of_government
:type: int
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.number_of_government
```

````

````{py:attribute} number_of_bank
:canonical: agentsociety.configs.exp_config.AgentConfig.number_of_bank
:type: int
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.number_of_bank
```

````

````{py:attribute} number_of_nbs
:canonical: agentsociety.configs.exp_config.AgentConfig.number_of_nbs
:type: int
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.number_of_nbs
```

````

````{py:attribute} group_size
:canonical: agentsociety.configs.exp_config.AgentConfig.group_size
:type: int
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.group_size
```

````

````{py:attribute} embedding_model
:canonical: agentsociety.configs.exp_config.AgentConfig.embedding_model
:type: typing.Any
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.embedding_model
```

````

````{py:attribute} extra_agent_class
:canonical: agentsociety.configs.exp_config.AgentConfig.extra_agent_class
:type: typing.Optional[dict[typing.Any, int]]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.extra_agent_class
```

````

````{py:attribute} agent_class_configs
:canonical: agentsociety.configs.exp_config.AgentConfig.agent_class_configs
:type: typing.Optional[dict[typing.Any, dict[str, typing.Any]]]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.agent_class_configs
```

````

````{py:attribute} init_func
:canonical: agentsociety.configs.exp_config.AgentConfig.init_func
:type: typing.Optional[list[collections.abc.Callable[[typing.Any], None]]]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.init_func
```

````

````{py:attribute} memory_config
:canonical: agentsociety.configs.exp_config.AgentConfig.memory_config
:type: typing.Optional[agentsociety.configs.exp_config.MemoryConfig]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.memory_config
```

````

````{py:property} prop_memory_config
:canonical: agentsociety.configs.exp_config.AgentConfig.prop_memory_config
:type: agentsociety.configs.exp_config.MemoryConfig

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.prop_memory_config
```

````

````{py:method} SetMemoryConfig(memory_config_func: typing.Optional[dict[type[typing.Any], collections.abc.Callable]] = None, memory_from_file: typing.Optional[dict[typing.Any, str]] = None, memory_distributions: typing.Optional[dict[str, agentsociety.configs.exp_config.DistributionConfig]] = None) -> agentsociety.configs.exp_config.AgentConfig
:canonical: agentsociety.configs.exp_config.AgentConfig.SetMemoryConfig

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.SetMemoryConfig
```

````

`````

`````{py:class} EnvironmentConfig(/, **data: typing.Any)
:canonical: agentsociety.configs.exp_config.EnvironmentConfig

Bases: {py:obj}`pydantic.BaseModel`

````{py:attribute} weather
:canonical: agentsociety.configs.exp_config.EnvironmentConfig.weather
:type: str
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.EnvironmentConfig.weather
```

````

````{py:attribute} temperature
:canonical: agentsociety.configs.exp_config.EnvironmentConfig.temperature
:type: str
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.EnvironmentConfig.temperature
```

````

````{py:attribute} workday
:canonical: agentsociety.configs.exp_config.EnvironmentConfig.workday
:type: bool
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.EnvironmentConfig.workday
```

````

````{py:attribute} other_information
:canonical: agentsociety.configs.exp_config.EnvironmentConfig.other_information
:type: str
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.EnvironmentConfig.other_information
```

````

`````

`````{py:class} MessageInterceptConfig(/, **data: typing.Any)
:canonical: agentsociety.configs.exp_config.MessageInterceptConfig

Bases: {py:obj}`pydantic.BaseModel`

````{py:attribute} mode
:canonical: agentsociety.configs.exp_config.MessageInterceptConfig.mode
:type: typing.Optional[typing.Union[typing.Literal[point], typing.Literal[edge]]]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.MessageInterceptConfig.mode
```

````

````{py:attribute} max_violation_time
:canonical: agentsociety.configs.exp_config.MessageInterceptConfig.max_violation_time
:type: int
:value: >
   3

```{autodoc2-docstring} agentsociety.configs.exp_config.MessageInterceptConfig.max_violation_time
```

````

````{py:attribute} message_interceptor_blocks
:canonical: agentsociety.configs.exp_config.MessageInterceptConfig.message_interceptor_blocks
:type: typing.Optional[list[typing.Any]]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.MessageInterceptConfig.message_interceptor_blocks
```

````

````{py:attribute} message_listener
:canonical: agentsociety.configs.exp_config.MessageInterceptConfig.message_listener
:type: typing.Optional[typing.Any]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.MessageInterceptConfig.message_listener
```

````

`````

`````{py:class} ExpConfig(/, **data: typing.Any)
:canonical: agentsociety.configs.exp_config.ExpConfig

Bases: {py:obj}`pydantic.BaseModel`

````{py:attribute} agent_config
:canonical: agentsociety.configs.exp_config.ExpConfig.agent_config
:type: typing.Optional[agentsociety.configs.exp_config.AgentConfig]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.agent_config
```

````

````{py:attribute} workflow
:canonical: agentsociety.configs.exp_config.ExpConfig.workflow
:type: typing.Optional[list[agentsociety.configs.exp_config.WorkflowStep]]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.workflow
```

````

````{py:attribute} environment
:canonical: agentsociety.configs.exp_config.ExpConfig.environment
:type: typing.Optional[agentsociety.configs.exp_config.EnvironmentConfig]
:value: >
   'EnvironmentConfig(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.environment
```

````

````{py:attribute} message_intercept
:canonical: agentsociety.configs.exp_config.ExpConfig.message_intercept
:type: typing.Optional[agentsociety.configs.exp_config.MessageInterceptConfig]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.message_intercept
```

````

````{py:attribute} metric_extractors
:canonical: agentsociety.configs.exp_config.ExpConfig.metric_extractors
:type: typing.Optional[list[agentsociety.configs.exp_config.MetricExtractor]]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.metric_extractors
```

````

````{py:attribute} logging_level
:canonical: agentsociety.configs.exp_config.ExpConfig.logging_level
:type: str
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.logging_level
```

````

````{py:attribute} exp_name
:canonical: agentsociety.configs.exp_config.ExpConfig.exp_name
:type: str
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.exp_name
```

````

````{py:attribute} llm_semaphore
:canonical: agentsociety.configs.exp_config.ExpConfig.llm_semaphore
:type: int
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.llm_semaphore
```

````

````{py:property} prop_agent_config
:canonical: agentsociety.configs.exp_config.ExpConfig.prop_agent_config
:type: agentsociety.configs.exp_config.AgentConfig

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.prop_agent_config
```

````

````{py:property} prop_workflow
:canonical: agentsociety.configs.exp_config.ExpConfig.prop_workflow
:type: list[agentsociety.configs.exp_config.WorkflowStep]

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.prop_workflow
```

````

````{py:property} prop_environment
:canonical: agentsociety.configs.exp_config.ExpConfig.prop_environment
:type: agentsociety.configs.exp_config.EnvironmentConfig

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.prop_environment
```

````

````{py:property} prop_message_intercept
:canonical: agentsociety.configs.exp_config.ExpConfig.prop_message_intercept
:type: agentsociety.configs.exp_config.MessageInterceptConfig

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.prop_message_intercept
```

````

````{py:property} prop_metric_extractors
:canonical: agentsociety.configs.exp_config.ExpConfig.prop_metric_extractors
:type: list[agentsociety.configs.exp_config.MetricExtractor]

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.prop_metric_extractors
```

````

````{py:method} SetAgentConfig(number_of_citizen: int = 1, number_of_firm: int = 1, number_of_government: int = 1, number_of_bank: int = 1, number_of_nbs: int = 1, group_size: int = 100, embedding_model: typing.Any = None, extra_agent_class: typing.Optional[dict[typing.Any, int]] = None, agent_class_configs: typing.Optional[dict[typing.Any, dict[str, typing.Any]]] = None, memory_config: typing.Optional[agentsociety.configs.exp_config.MemoryConfig] = None, init_func: typing.Optional[list[collections.abc.Callable[[typing.Any], None]]] = None) -> agentsociety.configs.exp_config.ExpConfig
:canonical: agentsociety.configs.exp_config.ExpConfig.SetAgentConfig

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.SetAgentConfig
```

````

````{py:method} SetMemoryConfig(memory_config_func: typing.Optional[dict[type[typing.Any], collections.abc.Callable]] = None, memory_from_file: typing.Optional[dict[typing.Any, str]] = None, memory_distributions: typing.Optional[dict[str, agentsociety.configs.exp_config.DistributionConfig]] = None) -> agentsociety.configs.exp_config.ExpConfig
:canonical: agentsociety.configs.exp_config.ExpConfig.SetMemoryConfig

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.SetMemoryConfig
```

````

````{py:method} SetEnvironment(weather: str = 'The weather is normal', temperature: str = 'The temperature is normal', workday: bool = True, other_information: str = '') -> agentsociety.configs.exp_config.ExpConfig
:canonical: agentsociety.configs.exp_config.ExpConfig.SetEnvironment

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.SetEnvironment
```

````

````{py:method} SetMessageIntercept(mode: typing.Optional[typing.Union[typing.Literal[point], typing.Literal[edge]]] = None, max_violation_time: int = 3, message_interceptor_blocks: typing.Optional[list[typing.Any]] = None, message_listener: typing.Optional[typing.Any] = None) -> agentsociety.configs.exp_config.ExpConfig
:canonical: agentsociety.configs.exp_config.ExpConfig.SetMessageIntercept

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.SetMessageIntercept
```

````

````{py:method} SetMetricExtractors(metric_extractors: list[agentsociety.configs.exp_config.MetricExtractor])
:canonical: agentsociety.configs.exp_config.ExpConfig.SetMetricExtractors

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.SetMetricExtractors
```

````

````{py:method} SetWorkFlow(workflows: list[agentsociety.configs.exp_config.WorkflowStep])
:canonical: agentsociety.configs.exp_config.ExpConfig.SetWorkFlow

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.SetWorkFlow
```

````

`````
