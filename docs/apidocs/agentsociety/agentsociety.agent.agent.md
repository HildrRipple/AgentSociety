# {py:mod}`agentsociety.agent.agent`

```{py:module} agentsociety.agent.agent
```

```{autodoc2-docstring} agentsociety.agent.agent
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CitizenAgent <agentsociety.agent.agent.CitizenAgent>`
  - ```{autodoc2-docstring} agentsociety.agent.agent.CitizenAgent
    :summary:
    ```
* - {py:obj}`InstitutionAgent <agentsociety.agent.agent.InstitutionAgent>`
  - ```{autodoc2-docstring} agentsociety.agent.agent.InstitutionAgent
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <agentsociety.agent.agent.__all__>`
  - ```{autodoc2-docstring} agentsociety.agent.agent.__all__
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: agentsociety.agent.agent.__all__
:value: >
   ['InstitutionAgent', 'CitizenAgent']

```{autodoc2-docstring} agentsociety.agent.agent.__all__
```

````

`````{py:class} CitizenAgent(name: str, llm_client: typing.Optional[agentsociety.llm.LLM] = None, simulator: typing.Optional[agentsociety.environment.Simulator] = None, memory: typing.Optional[agentsociety.memory.Memory] = None, economy_client: typing.Optional[agentsociety.environment.EconomyClient] = None, messager: typing.Optional[agentsociety.message.Messager] = None, message_interceptor: typing.Optional[agentsociety.message.MessageInterceptor] = None, avro_file: typing.Optional[dict] = None)
:canonical: agentsociety.agent.agent.CitizenAgent

Bases: {py:obj}`agentsociety.agent.agent_base.Agent`

```{autodoc2-docstring} agentsociety.agent.agent.CitizenAgent
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.agent.agent.CitizenAgent.__init__
```

````{py:method} bind_to_simulator()
:canonical: agentsociety.agent.agent.CitizenAgent.bind_to_simulator
:async:

```{autodoc2-docstring} agentsociety.agent.agent.CitizenAgent.bind_to_simulator
```

````

````{py:method} _bind_to_simulator()
:canonical: agentsociety.agent.agent.CitizenAgent._bind_to_simulator
:async:

```{autodoc2-docstring} agentsociety.agent.agent.CitizenAgent._bind_to_simulator
```

````

````{py:method} _bind_to_economy()
:canonical: agentsociety.agent.agent.CitizenAgent._bind_to_economy
:async:

```{autodoc2-docstring} agentsociety.agent.agent.CitizenAgent._bind_to_economy
```

````

````{py:method} handle_gather_message(payload: dict)
:canonical: agentsociety.agent.agent.CitizenAgent.handle_gather_message
:async:

```{autodoc2-docstring} agentsociety.agent.agent.CitizenAgent.handle_gather_message
```

````

````{py:property} mlflow_client
:canonical: agentsociety.agent.agent.CitizenAgent.mlflow_client
:type: agentsociety.metrics.MlflowClient

```{autodoc2-docstring} agentsociety.agent.agent.CitizenAgent.mlflow_client
```

````

````{py:method} set_mlflow_client(mlflow_client: agentsociety.metrics.MlflowClient)
:canonical: agentsociety.agent.agent.CitizenAgent.set_mlflow_client

```{autodoc2-docstring} agentsociety.agent.agent.CitizenAgent.set_mlflow_client
```

````

`````

`````{py:class} InstitutionAgent(name: str, llm_client: typing.Optional[agentsociety.llm.LLM] = None, simulator: typing.Optional[agentsociety.environment.Simulator] = None, memory: typing.Optional[agentsociety.memory.Memory] = None, economy_client: typing.Optional[agentsociety.environment.EconomyClient] = None, messager: typing.Optional[agentsociety.message.Messager] = None, message_interceptor: typing.Optional[agentsociety.message.MessageInterceptor] = None, avro_file: typing.Optional[dict] = None)
:canonical: agentsociety.agent.agent.InstitutionAgent

Bases: {py:obj}`agentsociety.agent.agent_base.Agent`

```{autodoc2-docstring} agentsociety.agent.agent.InstitutionAgent
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.agent.agent.InstitutionAgent.__init__
```

````{py:method} bind_to_simulator()
:canonical: agentsociety.agent.agent.InstitutionAgent.bind_to_simulator
:async:

```{autodoc2-docstring} agentsociety.agent.agent.InstitutionAgent.bind_to_simulator
```

````

````{py:method} _bind_to_economy()
:canonical: agentsociety.agent.agent.InstitutionAgent._bind_to_economy
:async:

```{autodoc2-docstring} agentsociety.agent.agent.InstitutionAgent._bind_to_economy
```

````

````{py:method} handle_gather_message(payload: dict)
:canonical: agentsociety.agent.agent.InstitutionAgent.handle_gather_message
:async:

```{autodoc2-docstring} agentsociety.agent.agent.InstitutionAgent.handle_gather_message
```

````

````{py:method} gather_messages(agent_ids: list[int], target: str) -> list[dict]
:canonical: agentsociety.agent.agent.InstitutionAgent.gather_messages
:async:

```{autodoc2-docstring} agentsociety.agent.agent.InstitutionAgent.gather_messages
```

````

````{py:property} mlflow_client
:canonical: agentsociety.agent.agent.InstitutionAgent.mlflow_client
:type: agentsociety.metrics.MlflowClient

```{autodoc2-docstring} agentsociety.agent.agent.InstitutionAgent.mlflow_client
```

````

````{py:method} set_mlflow_client(mlflow_client: agentsociety.metrics.MlflowClient)
:canonical: agentsociety.agent.agent.InstitutionAgent.set_mlflow_client

```{autodoc2-docstring} agentsociety.agent.agent.InstitutionAgent.set_mlflow_client
```

````

`````
