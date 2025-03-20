# {py:mod}`agentsociety.webapi.api.experiment_runner`

```{py:module} agentsociety.webapi.api.experiment_runner
```

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ExperimentConfig <agentsociety.webapi.api.experiment_runner.ExperimentConfig>`
  - ```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.ExperimentConfig
    :summary:
    ```
* - {py:obj}`ExperimentResponse <agentsociety.webapi.api.experiment_runner.ExperimentResponse>`
  - ```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.ExperimentResponse
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`run_experiment <agentsociety.webapi.api.experiment_runner.run_experiment>`
  - ```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.run_experiment
    :summary:
    ```
* - {py:obj}`get_experiments <agentsociety.webapi.api.experiment_runner.get_experiments>`
  - ```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.get_experiments
    :summary:
    ```
* - {py:obj}`get_experiment_status <agentsociety.webapi.api.experiment_runner.get_experiment_status>`
  - ```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.get_experiment_status
    :summary:
    ```
* - {py:obj}`stop_experiment <agentsociety.webapi.api.experiment_runner.stop_experiment>`
  - ```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.stop_experiment
    :summary:
    ```
* - {py:obj}`update_experiment_status <agentsociety.webapi.api.experiment_runner.update_experiment_status>`
  - ```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.update_experiment_status
    :summary:
    ```
* - {py:obj}`startup_event <agentsociety.webapi.api.experiment_runner.startup_event>`
  - ```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.startup_event
    :summary:
    ```
* - {py:obj}`shutdown_event <agentsociety.webapi.api.experiment_runner.shutdown_event>`
  - ```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.shutdown_event
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <agentsociety.webapi.api.experiment_runner.__all__>`
  - ```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.__all__
    :summary:
    ```
* - {py:obj}`router <agentsociety.webapi.api.experiment_runner.router>`
  - ```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.router
    :summary:
    ```
* - {py:obj}`logger <agentsociety.webapi.api.experiment_runner.logger>`
  - ```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.logger
    :summary:
    ```
* - {py:obj}`running_experiments <agentsociety.webapi.api.experiment_runner.running_experiments>`
  - ```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.running_experiments
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: agentsociety.webapi.api.experiment_runner.__all__
:value: >
   ['router']

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.__all__
```

````

````{py:data} router
:canonical: agentsociety.webapi.api.experiment_runner.router
:value: >
   'APIRouter(...)'

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.router
```

````

````{py:data} logger
:canonical: agentsociety.webapi.api.experiment_runner.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.logger
```

````

````{py:data} running_experiments
:canonical: agentsociety.webapi.api.experiment_runner.running_experiments
:type: typing.Dict[str, typing.Dict]
:value: >
   None

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.running_experiments
```

````

`````{py:class} ExperimentConfig(/, **data: typing.Any)
:canonical: agentsociety.webapi.api.experiment_runner.ExperimentConfig

Bases: {py:obj}`pydantic.BaseModel`

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.ExperimentConfig
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.ExperimentConfig.__init__
```

````{py:attribute} environment
:canonical: agentsociety.webapi.api.experiment_runner.ExperimentConfig.environment
:type: typing.Dict
:value: >
   None

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.ExperimentConfig.environment
```

````

````{py:attribute} agent
:canonical: agentsociety.webapi.api.experiment_runner.ExperimentConfig.agent
:type: typing.Dict
:value: >
   None

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.ExperimentConfig.agent
```

````

````{py:attribute} workflow
:canonical: agentsociety.webapi.api.experiment_runner.ExperimentConfig.workflow
:type: typing.Dict
:value: >
   None

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.ExperimentConfig.workflow
```

````

````{py:attribute} map
:canonical: agentsociety.webapi.api.experiment_runner.ExperimentConfig.map
:type: typing.Dict
:value: >
   None

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.ExperimentConfig.map
```

````

````{py:attribute} name
:canonical: agentsociety.webapi.api.experiment_runner.ExperimentConfig.name
:type: str
:value: >
   None

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.ExperimentConfig.name
```

````

`````

`````{py:class} ExperimentResponse(/, **data: typing.Any)
:canonical: agentsociety.webapi.api.experiment_runner.ExperimentResponse

Bases: {py:obj}`pydantic.BaseModel`

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.ExperimentResponse
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.ExperimentResponse.__init__
```

````{py:attribute} id
:canonical: agentsociety.webapi.api.experiment_runner.ExperimentResponse.id
:type: str
:value: >
   None

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.ExperimentResponse.id
```

````

````{py:attribute} name
:canonical: agentsociety.webapi.api.experiment_runner.ExperimentResponse.name
:type: str
:value: >
   None

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.ExperimentResponse.name
```

````

````{py:attribute} status
:canonical: agentsociety.webapi.api.experiment_runner.ExperimentResponse.status
:type: str
:value: >
   None

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.ExperimentResponse.status
```

````

`````

````{py:function} run_experiment(request: fastapi.Request, config: agentsociety.webapi.api.experiment_runner.ExperimentConfig) -> agentsociety.webapi.models.ApiResponseWrapper[agentsociety.webapi.api.experiment_runner.ExperimentResponse]
:canonical: agentsociety.webapi.api.experiment_runner.run_experiment
:async:

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.run_experiment
```
````

````{py:function} get_experiments(request: fastapi.Request) -> agentsociety.webapi.models.ApiResponseWrapper[typing.List[typing.Dict]]
:canonical: agentsociety.webapi.api.experiment_runner.get_experiments
:async:

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.get_experiments
```
````

````{py:function} get_experiment_status(request: fastapi.Request, experiment_id: str) -> agentsociety.webapi.models.ApiResponseWrapper[typing.Dict]
:canonical: agentsociety.webapi.api.experiment_runner.get_experiment_status
:async:

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.get_experiment_status
```
````

````{py:function} stop_experiment(request: fastapi.Request, experiment_id: str) -> agentsociety.webapi.models.ApiResponseWrapper[typing.Dict]
:canonical: agentsociety.webapi.api.experiment_runner.stop_experiment
:async:

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.stop_experiment
```
````

````{py:function} update_experiment_status(experiment_id: str)
:canonical: agentsociety.webapi.api.experiment_runner.update_experiment_status
:async:

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.update_experiment_status
```
````

````{py:function} startup_event()
:canonical: agentsociety.webapi.api.experiment_runner.startup_event
:async:

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.startup_event
```
````

````{py:function} shutdown_event()
:canonical: agentsociety.webapi.api.experiment_runner.shutdown_event
:async:

```{autodoc2-docstring} agentsociety.webapi.api.experiment_runner.shutdown_event
```
````
