# {py:mod}`agentsociety.simulation.agentgroup`

```{py:module} agentsociety.simulation.agentgroup
```

```{autodoc2-docstring} agentsociety.simulation.agentgroup
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`AgentGroup <agentsociety.simulation.agentgroup.AgentGroup>`
  - ```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <agentsociety.simulation.agentgroup.__all__>`
  - ```{autodoc2-docstring} agentsociety.simulation.agentgroup.__all__
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: agentsociety.simulation.agentgroup.__all__
:value: >
   ['AgentGroup']

```{autodoc2-docstring} agentsociety.simulation.agentgroup.__all__
```

````

`````{py:class} AgentGroup(agent_class: typing.Union[type[agentsociety.agent.Agent], list[type[agentsociety.agent.Agent]]], number_of_agents: typing.Union[int, list[int]], memory_values_dict: dict[type[agentsociety.agent.Agent], list[dict]], config: agentsociety.configs.SimConfig, map_ref: ray.ObjectRef, exp_name: str, exp_id: typing.Union[str, uuid.UUID], tenant_id: str, enable_avro: bool, avro_path: pathlib.Path, enable_pgsql: bool, pgsql_writer: ray.ObjectRef, message_interceptor: ray.ObjectRef, mlflow_run_id: str, embedding_model: langchain_core.embeddings.Embeddings, logging_level: str, agent_config_file: typing.Optional[dict[type[agentsociety.agent.Agent], typing.Any]] = None, llm_semaphore: int = 200, environment: typing.Optional[dict] = None)
:canonical: agentsociety.simulation.agentgroup.AgentGroup

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.__init__
```

````{py:property} agent_count
:canonical: agentsociety.simulation.agentgroup.AgentGroup.agent_count

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.agent_count
```

````

````{py:property} agent_ids
:canonical: agentsociety.simulation.agentgroup.AgentGroup.agent_ids

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.agent_ids
```

````

````{py:property} agent_type
:canonical: agentsociety.simulation.agentgroup.AgentGroup.agent_type

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.agent_type
```

````

````{py:method} get_economy_ids()
:canonical: agentsociety.simulation.agentgroup.AgentGroup.get_economy_ids
:async:

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.get_economy_ids
```

````

````{py:method} set_economy_ids(agent_ids: set[int], firm_ids: set[int], bank_ids: set[int], nbs_ids: set[int], government_ids: set[int])
:canonical: agentsociety.simulation.agentgroup.AgentGroup.set_economy_ids
:async:

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.set_economy_ids
```

````

````{py:method} get_agent_count()
:canonical: agentsociety.simulation.agentgroup.AgentGroup.get_agent_count

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.get_agent_count
```

````

````{py:method} get_agent_ids()
:canonical: agentsociety.simulation.agentgroup.AgentGroup.get_agent_ids

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.get_agent_ids
```

````

````{py:method} get_agent_type()
:canonical: agentsociety.simulation.agentgroup.AgentGroup.get_agent_type

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.get_agent_type
```

````

````{py:method} __aexit__(exc_type, exc_value, traceback)
:canonical: agentsociety.simulation.agentgroup.AgentGroup.__aexit__
:async:

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.__aexit__
```

````

````{py:method} insert_agent()
:canonical: agentsociety.simulation.agentgroup.AgentGroup.insert_agent
:async:

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.insert_agent
```

````

````{py:method} init_agents()
:canonical: agentsociety.simulation.agentgroup.AgentGroup.init_agents
:async:

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.init_agents
```

````

````{py:method} update_environment(key: str, value: str)
:canonical: agentsociety.simulation.agentgroup.AgentGroup.update_environment
:async:

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.update_environment
```

````

````{py:method} filter(types: typing.Optional[list[typing.Type[agentsociety.agent.Agent]]] = None, keys: typing.Optional[list[str]] = None, values: typing.Optional[list[typing.Any]] = None) -> list[str]
:canonical: agentsociety.simulation.agentgroup.AgentGroup.filter
:async:

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.filter
```

````

````{py:method} gather(content: str, target_agent_ids: typing.Optional[list[int]] = None)
:canonical: agentsociety.simulation.agentgroup.AgentGroup.gather
:async:

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.gather
```

````

````{py:method} update(target_agent_id: int, target_key: str, content: typing.Any)
:canonical: agentsociety.simulation.agentgroup.AgentGroup.update
:async:

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.update
```

````

````{py:method} message_dispatch()
:canonical: agentsociety.simulation.agentgroup.AgentGroup.message_dispatch
:async:

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.message_dispatch
```

````

````{py:method} save_status(simulator_day: typing.Optional[int] = None, simulator_t: typing.Optional[int] = None)
:canonical: agentsociety.simulation.agentgroup.AgentGroup.save_status
:async:

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.save_status
```

````

````{py:method} get_llm_consumption()
:canonical: agentsociety.simulation.agentgroup.AgentGroup.get_llm_consumption

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.get_llm_consumption
```

````

````{py:method} get_llm_error_statistics()
:canonical: agentsociety.simulation.agentgroup.AgentGroup.get_llm_error_statistics
:async:

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.get_llm_error_statistics
```

````

````{py:method} react_to_intervention(intervention_message: str, agent_ids: list[int])
:canonical: agentsociety.simulation.agentgroup.AgentGroup.react_to_intervention
:async:

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.react_to_intervention
```

````

````{py:method} step()
:canonical: agentsociety.simulation.agentgroup.AgentGroup.step
:async:

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.step
```

````

````{py:method} save(day: int, t: int)
:canonical: agentsociety.simulation.agentgroup.AgentGroup.save
:async:

```{autodoc2-docstring} agentsociety.simulation.agentgroup.AgentGroup.save
```

````

`````
