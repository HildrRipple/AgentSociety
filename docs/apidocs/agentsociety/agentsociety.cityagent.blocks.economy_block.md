# {py:mod}`agentsociety.cityagent.blocks.economy_block`

```{py:module} agentsociety.cityagent.blocks.economy_block
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`WorkBlock <agentsociety.cityagent.blocks.economy_block.WorkBlock>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.WorkBlock
    :summary:
    ```
* - {py:obj}`ConsumptionBlock <agentsociety.cityagent.blocks.economy_block.ConsumptionBlock>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.ConsumptionBlock
    :summary:
    ```
* - {py:obj}`EconomyNoneBlock <agentsociety.cityagent.blocks.economy_block.EconomyNoneBlock>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyNoneBlock
    :summary:
    ```
* - {py:obj}`EconomyBlockParams <agentsociety.cityagent.blocks.economy_block.EconomyBlockParams>`
  -
* - {py:obj}`EconomyBlockContext <agentsociety.cityagent.blocks.economy_block.EconomyBlockContext>`
  -
* - {py:obj}`EconomyBlock <agentsociety.cityagent.blocks.economy_block.EconomyBlock>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyBlock
    :summary:
    ```
* - {py:obj}`MonthEconomyPlanBlock <agentsociety.cityagent.blocks.economy_block.MonthEconomyPlanBlock>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.MonthEconomyPlanBlock
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`softmax <agentsociety.cityagent.blocks.economy_block.softmax>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.softmax
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`WORKTIME_ESTIMATE_PROMPT <agentsociety.cityagent.blocks.economy_block.WORKTIME_ESTIMATE_PROMPT>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.WORKTIME_ESTIMATE_PROMPT
    :summary:
    ```
````

### API

````{py:data} WORKTIME_ESTIMATE_PROMPT
:canonical: agentsociety.cityagent.blocks.economy_block.WORKTIME_ESTIMATE_PROMPT
:value: <Multiline-String>

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.WORKTIME_ESTIMATE_PROMPT
```

````

````{py:function} softmax(x, gamma=1.0)
:canonical: agentsociety.cityagent.blocks.economy_block.softmax

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.softmax
```
````

`````{py:class} WorkBlock(llm: agentsociety.llm.LLM, environment: agentsociety.environment.Environment, memory: agentsociety.memory.Memory, worktime_estimation_prompt: str = WORKTIME_ESTIMATE_PROMPT)
:canonical: agentsociety.cityagent.blocks.economy_block.WorkBlock

Bases: {py:obj}`agentsociety.agent.Block`

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.WorkBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.WorkBlock.__init__
```

````{py:attribute} name
:canonical: agentsociety.cityagent.blocks.economy_block.WorkBlock.name
:value: >
   'WorkBlock'

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.WorkBlock.name
```

````

````{py:attribute} description
:canonical: agentsociety.cityagent.blocks.economy_block.WorkBlock.description
:value: >
   'Handles work-related economic activities and time tracking'

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.WorkBlock.description
```

````

````{py:method} forward(context: agentsociety.agent.DotDict)
:canonical: agentsociety.cityagent.blocks.economy_block.WorkBlock.forward
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.WorkBlock.forward
```

````

`````

`````{py:class} ConsumptionBlock(llm: agentsociety.llm.LLM, environment: agentsociety.environment.Environment, agent_memory: agentsociety.memory.Memory)
:canonical: agentsociety.cityagent.blocks.economy_block.ConsumptionBlock

Bases: {py:obj}`agentsociety.agent.Block`

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.ConsumptionBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.ConsumptionBlock.__init__
```

````{py:attribute} name
:canonical: agentsociety.cityagent.blocks.economy_block.ConsumptionBlock.name
:value: >
   'ConsumptionBlock'

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.ConsumptionBlock.name
```

````

````{py:attribute} description
:canonical: agentsociety.cityagent.blocks.economy_block.ConsumptionBlock.description
:value: >
   'Used to determine the consumption amount, and items'

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.ConsumptionBlock.description
```

````

````{py:method} forward(context: agentsociety.agent.DotDict)
:canonical: agentsociety.cityagent.blocks.economy_block.ConsumptionBlock.forward
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.ConsumptionBlock.forward
```

````

`````

`````{py:class} EconomyNoneBlock(llm: agentsociety.llm.LLM, memory: agentsociety.memory.Memory)
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyNoneBlock

Bases: {py:obj}`agentsociety.agent.Block`

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyNoneBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyNoneBlock.__init__
```

````{py:attribute} name
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyNoneBlock.name
:value: >
   'EconomyNoneBlock'

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyNoneBlock.name
```

````

````{py:attribute} description
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyNoneBlock.description
:value: >
   'Fallback block for other activities'

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyNoneBlock.description
```

````

````{py:method} forward(context: agentsociety.agent.DotDict)
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyNoneBlock.forward
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyNoneBlock.forward
```

````

`````

`````{py:class} EconomyBlockParams(/, **data: typing.Any)
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyBlockParams

Bases: {py:obj}`agentsociety.agent.BlockParams`

````{py:attribute} worktime_estimation_prompt
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyBlockParams.worktime_estimation_prompt
:type: str
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyBlockParams.worktime_estimation_prompt
```

````

`````

```{py:class} EconomyBlockContext(/, **data: typing.Any)
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyBlockContext

Bases: {py:obj}`agentsociety.agent.BlockContext`

```

`````{py:class} EconomyBlock(llm: agentsociety.llm.LLM, environment: agentsociety.environment.Environment, agent_memory: agentsociety.memory.Memory, block_params: typing.Optional[agentsociety.cityagent.blocks.economy_block.EconomyBlockParams] = None)
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyBlock

Bases: {py:obj}`agentsociety.agent.Block`

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyBlock.__init__
```

````{py:attribute} ParamsType
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyBlock.ParamsType
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyBlock.ParamsType
```

````

````{py:attribute} OutputType
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyBlock.OutputType
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyBlock.OutputType
```

````

````{py:attribute} ContextType
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyBlock.ContextType
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyBlock.ContextType
```

````

````{py:attribute} NeedAgent
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyBlock.NeedAgent
:value: >
   True

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyBlock.NeedAgent
```

````

````{py:attribute} name
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyBlock.name
:value: >
   'EconomyBlock'

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyBlock.name
```

````

````{py:attribute} description
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyBlock.description
:value: >
   'Responsible for all kinds of economic-related operations'

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyBlock.description
```

````

````{py:attribute} actions
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyBlock.actions
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyBlock.actions
```

````

````{py:method} forward(agent_context: agentsociety.agent.DotDict) -> agentsociety.cityagent.sharing_params.SocietyAgentBlockOutput
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyBlock.forward
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyBlock.forward
```

````

`````

`````{py:class} MonthEconomyPlanBlock(llm: agentsociety.llm.LLM, environment: agentsociety.environment.Environment, agent_memory: agentsociety.memory.Memory, ubi: float = 0, num_labor_hours: int = 168, productivity_per_labor: float = 1, time_diff: int = 30 * 24 * 60 * 60)
:canonical: agentsociety.cityagent.blocks.economy_block.MonthEconomyPlanBlock

Bases: {py:obj}`agentsociety.agent.Block`

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.MonthEconomyPlanBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.MonthEconomyPlanBlock.__init__
```

````{py:method} month_trigger()
:canonical: agentsociety.cityagent.blocks.economy_block.MonthEconomyPlanBlock.month_trigger
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.MonthEconomyPlanBlock.month_trigger
```

````

````{py:method} forward()
:canonical: agentsociety.cityagent.blocks.economy_block.MonthEconomyPlanBlock.forward
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.MonthEconomyPlanBlock.forward
```

````

`````
