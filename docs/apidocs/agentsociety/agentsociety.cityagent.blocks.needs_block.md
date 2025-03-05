# {py:mod}`agentsociety.cityagent.blocks.needs_block`

```{py:module} agentsociety.cityagent.blocks.needs_block
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.needs_block
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`NeedsBlock <agentsociety.cityagent.blocks.needs_block.NeedsBlock>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.needs_block.NeedsBlock
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <agentsociety.cityagent.blocks.needs_block.logger>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.needs_block.logger
    :summary:
    ```
* - {py:obj}`INITIAL_NEEDS_PROMPT <agentsociety.cityagent.blocks.needs_block.INITIAL_NEEDS_PROMPT>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.needs_block.INITIAL_NEEDS_PROMPT
    :summary:
    ```
* - {py:obj}`EVALUATION_PROMPT <agentsociety.cityagent.blocks.needs_block.EVALUATION_PROMPT>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.needs_block.EVALUATION_PROMPT
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: agentsociety.cityagent.blocks.needs_block.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} agentsociety.cityagent.blocks.needs_block.logger
```

````

````{py:data} INITIAL_NEEDS_PROMPT
:canonical: agentsociety.cityagent.blocks.needs_block.INITIAL_NEEDS_PROMPT
:value: <Multiline-String>

```{autodoc2-docstring} agentsociety.cityagent.blocks.needs_block.INITIAL_NEEDS_PROMPT
```

````

````{py:data} EVALUATION_PROMPT
:canonical: agentsociety.cityagent.blocks.needs_block.EVALUATION_PROMPT
:value: <Multiline-String>

```{autodoc2-docstring} agentsociety.cityagent.blocks.needs_block.EVALUATION_PROMPT
```

````

`````{py:class} NeedsBlock(llm: agentsociety.llm.LLM, memory: agentsociety.memory.Memory, simulator: agentsociety.Simulator)
:canonical: agentsociety.cityagent.blocks.needs_block.NeedsBlock

Bases: {py:obj}`agentsociety.workflow.Block`

```{autodoc2-docstring} agentsociety.cityagent.blocks.needs_block.NeedsBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.needs_block.NeedsBlock.__init__
```

````{py:method} initialize()
:canonical: agentsociety.cityagent.blocks.needs_block.NeedsBlock.initialize
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.needs_block.NeedsBlock.initialize
```

````

````{py:method} time_decay()
:canonical: agentsociety.cityagent.blocks.needs_block.NeedsBlock.time_decay
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.needs_block.NeedsBlock.time_decay
```

````

````{py:method} update_when_plan_completed()
:canonical: agentsociety.cityagent.blocks.needs_block.NeedsBlock.update_when_plan_completed
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.needs_block.NeedsBlock.update_when_plan_completed
```

````

````{py:method} determine_current_need()
:canonical: agentsociety.cityagent.blocks.needs_block.NeedsBlock.determine_current_need
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.needs_block.NeedsBlock.determine_current_need
```

````

````{py:method} evaluate_and_adjust_needs(completed_plan)
:canonical: agentsociety.cityagent.blocks.needs_block.NeedsBlock.evaluate_and_adjust_needs
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.needs_block.NeedsBlock.evaluate_and_adjust_needs
```

````

````{py:method} forward()
:canonical: agentsociety.cityagent.blocks.needs_block.NeedsBlock.forward
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.needs_block.NeedsBlock.forward
```

````

`````
