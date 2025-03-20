# {py:mod}`agentsociety.utils.config_const`

```{py:module} agentsociety.utils.config_const
```

```{autodoc2-docstring} agentsociety.utils.config_const
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`WorkflowType <agentsociety.utils.config_const.WorkflowType>`
  - ```{autodoc2-docstring} agentsociety.utils.config_const.WorkflowType
    :summary:
    ```
* - {py:obj}`LLMProviderType <agentsociety.utils.config_const.LLMProviderType>`
  - ```{autodoc2-docstring} agentsociety.utils.config_const.LLMProviderType
    :summary:
    ```
* - {py:obj}`DistributionType <agentsociety.utils.config_const.DistributionType>`
  - ```{autodoc2-docstring} agentsociety.utils.config_const.DistributionType
    :summary:
    ```
* - {py:obj}`MetricType <agentsociety.utils.config_const.MetricType>`
  - ```{autodoc2-docstring} agentsociety.utils.config_const.MetricType
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`LLMProviderTypeValues <agentsociety.utils.config_const.LLMProviderTypeValues>`
  - ```{autodoc2-docstring} agentsociety.utils.config_const.LLMProviderTypeValues
    :summary:
    ```
````

### API

`````{py:class} WorkflowType()
:canonical: agentsociety.utils.config_const.WorkflowType

Bases: {py:obj}`str`, {py:obj}`enum.Enum`

```{autodoc2-docstring} agentsociety.utils.config_const.WorkflowType
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.utils.config_const.WorkflowType.__init__
```

````{py:attribute} STEP
:canonical: agentsociety.utils.config_const.WorkflowType.STEP
:value: >
   'step'

```{autodoc2-docstring} agentsociety.utils.config_const.WorkflowType.STEP
```

````

````{py:attribute} RUN
:canonical: agentsociety.utils.config_const.WorkflowType.RUN
:value: >
   'run'

```{autodoc2-docstring} agentsociety.utils.config_const.WorkflowType.RUN
```

````

````{py:attribute} INTERVIEW
:canonical: agentsociety.utils.config_const.WorkflowType.INTERVIEW
:value: >
   'interview'

```{autodoc2-docstring} agentsociety.utils.config_const.WorkflowType.INTERVIEW
```

````

````{py:attribute} SURVEY
:canonical: agentsociety.utils.config_const.WorkflowType.SURVEY
:value: >
   'survey'

```{autodoc2-docstring} agentsociety.utils.config_const.WorkflowType.SURVEY
```

````

````{py:attribute} ENVIRONMENT_INTERVENE
:canonical: agentsociety.utils.config_const.WorkflowType.ENVIRONMENT_INTERVENE
:value: >
   'environment'

```{autodoc2-docstring} agentsociety.utils.config_const.WorkflowType.ENVIRONMENT_INTERVENE
```

````

````{py:attribute} UPDATE_STATE_INTERVENE
:canonical: agentsociety.utils.config_const.WorkflowType.UPDATE_STATE_INTERVENE
:value: >
   'update_state'

```{autodoc2-docstring} agentsociety.utils.config_const.WorkflowType.UPDATE_STATE_INTERVENE
```

````

````{py:attribute} MESSAGE_INTERVENE
:canonical: agentsociety.utils.config_const.WorkflowType.MESSAGE_INTERVENE
:value: >
   'message'

```{autodoc2-docstring} agentsociety.utils.config_const.WorkflowType.MESSAGE_INTERVENE
```

````

````{py:attribute} INTERVENE
:canonical: agentsociety.utils.config_const.WorkflowType.INTERVENE
:value: >
   'other'

```{autodoc2-docstring} agentsociety.utils.config_const.WorkflowType.INTERVENE
```

````

````{py:attribute} FUNCTION
:canonical: agentsociety.utils.config_const.WorkflowType.FUNCTION
:value: >
   'function'

```{autodoc2-docstring} agentsociety.utils.config_const.WorkflowType.FUNCTION
```

````

`````

`````{py:class} LLMProviderType()
:canonical: agentsociety.utils.config_const.LLMProviderType

Bases: {py:obj}`str`, {py:obj}`enum.Enum`

```{autodoc2-docstring} agentsociety.utils.config_const.LLMProviderType
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.utils.config_const.LLMProviderType.__init__
```

````{py:attribute} OpenAI
:canonical: agentsociety.utils.config_const.LLMProviderType.OpenAI
:value: >
   'openai'

```{autodoc2-docstring} agentsociety.utils.config_const.LLMProviderType.OpenAI
```

````

````{py:attribute} DeepSeek
:canonical: agentsociety.utils.config_const.LLMProviderType.DeepSeek
:value: >
   'deepseek'

```{autodoc2-docstring} agentsociety.utils.config_const.LLMProviderType.DeepSeek
```

````

````{py:attribute} Qwen
:canonical: agentsociety.utils.config_const.LLMProviderType.Qwen
:value: >
   'qwen'

```{autodoc2-docstring} agentsociety.utils.config_const.LLMProviderType.Qwen
```

````

````{py:attribute} ZhipuAI
:canonical: agentsociety.utils.config_const.LLMProviderType.ZhipuAI
:value: >
   'zhipuai'

```{autodoc2-docstring} agentsociety.utils.config_const.LLMProviderType.ZhipuAI
```

````

````{py:attribute} SiliconFlow
:canonical: agentsociety.utils.config_const.LLMProviderType.SiliconFlow
:value: >
   'siliconflow'

```{autodoc2-docstring} agentsociety.utils.config_const.LLMProviderType.SiliconFlow
```

````

````{py:attribute} VLLM
:canonical: agentsociety.utils.config_const.LLMProviderType.VLLM
:value: >
   'vllm'

```{autodoc2-docstring} agentsociety.utils.config_const.LLMProviderType.VLLM
```

````

`````

````{py:data} LLMProviderTypeValues
:canonical: agentsociety.utils.config_const.LLMProviderTypeValues
:value: >
   None

```{autodoc2-docstring} agentsociety.utils.config_const.LLMProviderTypeValues
```

````

`````{py:class} DistributionType()
:canonical: agentsociety.utils.config_const.DistributionType

Bases: {py:obj}`str`, {py:obj}`enum.Enum`

```{autodoc2-docstring} agentsociety.utils.config_const.DistributionType
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.utils.config_const.DistributionType.__init__
```

````{py:attribute} CHOICE
:canonical: agentsociety.utils.config_const.DistributionType.CHOICE
:value: >
   'choice'

```{autodoc2-docstring} agentsociety.utils.config_const.DistributionType.CHOICE
```

````

````{py:attribute} UNIFORM_INT
:canonical: agentsociety.utils.config_const.DistributionType.UNIFORM_INT
:value: >
   'uniform_int'

```{autodoc2-docstring} agentsociety.utils.config_const.DistributionType.UNIFORM_INT
```

````

````{py:attribute} UNIFORM_FLOAT
:canonical: agentsociety.utils.config_const.DistributionType.UNIFORM_FLOAT
:value: >
   'uniform_float'

```{autodoc2-docstring} agentsociety.utils.config_const.DistributionType.UNIFORM_FLOAT
```

````

````{py:attribute} NORMAL
:canonical: agentsociety.utils.config_const.DistributionType.NORMAL
:value: >
   'normal'

```{autodoc2-docstring} agentsociety.utils.config_const.DistributionType.NORMAL
```

````

````{py:attribute} CONSTANT
:canonical: agentsociety.utils.config_const.DistributionType.CONSTANT
:value: >
   'constant'

```{autodoc2-docstring} agentsociety.utils.config_const.DistributionType.CONSTANT
```

````

`````

`````{py:class} MetricType()
:canonical: agentsociety.utils.config_const.MetricType

Bases: {py:obj}`str`, {py:obj}`enum.Enum`

```{autodoc2-docstring} agentsociety.utils.config_const.MetricType
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.utils.config_const.MetricType.__init__
```

````{py:attribute} FUNCTION
:canonical: agentsociety.utils.config_const.MetricType.FUNCTION
:value: >
   'function'

```{autodoc2-docstring} agentsociety.utils.config_const.MetricType.FUNCTION
```

````

````{py:attribute} STATE
:canonical: agentsociety.utils.config_const.MetricType.STATE
:value: >
   'state'

```{autodoc2-docstring} agentsociety.utils.config_const.MetricType.STATE
```

````

`````
