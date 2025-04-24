# {py:mod}`agentsociety.webapi.app`

```{py:module} agentsociety.webapi.app
```

```{autodoc2-docstring} agentsociety.webapi.app
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`empty_get_tenant_id <agentsociety.webapi.app.empty_get_tenant_id>`
  - ```{autodoc2-docstring} agentsociety.webapi.app.empty_get_tenant_id
    :summary:
    ```
* - {py:obj}`create_app <agentsociety.webapi.app.create_app>`
  - ```{autodoc2-docstring} agentsociety.webapi.app.create_app
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <agentsociety.webapi.app.__all__>`
  - ```{autodoc2-docstring} agentsociety.webapi.app.__all__
    :summary:
    ```
* - {py:obj}`_script_dir <agentsociety.webapi.app._script_dir>`
  - ```{autodoc2-docstring} agentsociety.webapi.app._script_dir
    :summary:
    ```
* - {py:obj}`_parent_dir <agentsociety.webapi.app._parent_dir>`
  - ```{autodoc2-docstring} agentsociety.webapi.app._parent_dir
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: agentsociety.webapi.app.__all__
:value: >
   ['create_app', 'empty_get_tenant_id']

```{autodoc2-docstring} agentsociety.webapi.app.__all__
```

````

````{py:data} _script_dir
:canonical: agentsociety.webapi.app._script_dir
:value: >
   'dirname(...)'

```{autodoc2-docstring} agentsociety.webapi.app._script_dir
```

````

````{py:data} _parent_dir
:canonical: agentsociety.webapi.app._parent_dir
:value: >
   'dirname(...)'

```{autodoc2-docstring} agentsociety.webapi.app._parent_dir
```

````

````{py:function} empty_get_tenant_id(_: fastapi.Request) -> str
:canonical: agentsociety.webapi.app.empty_get_tenant_id
:async:

```{autodoc2-docstring} agentsociety.webapi.app.empty_get_tenant_id
```
````

````{py:function} create_app(pg_dsn: str, mlflow_url: str, read_only: bool, env: agentsociety.configs.EnvConfig, get_tenant_id: typing.Callable[[fastapi.Request], typing.Awaitable[str]] = empty_get_tenant_id, more_router: typing.Optional[fastapi.APIRouter] = None, more_state: typing.Dict[str, typing.Any] = {}, session_secret_key: str = 'agentsociety-session')
:canonical: agentsociety.webapi.app.create_app

```{autodoc2-docstring} agentsociety.webapi.app.create_app
```
````
