# Start Your First Simulation

Follow the steps below to begin our simulation of societal dynamics for 50 individuals over a period of 1 day in Beijing.

## Step 0: Installation

To install the necessary package, run the following command:

```bash
pip install agentsociety
```

```{admonition} Warning
:class: warning
Please ensure your environment matches the supported platforms shown in the [Prerequisites](../01-prerequisites.md) section.
```

```{admonition} Hint
:class: hint
If you look the error like `ERROR: Could not find a version that satisfies the requirement agentsociety`, it means your OS, architecture or python version is not supported.
Please refer to the [Prerequisites](../01-prerequisites.md) section for more details.
It could also be the Python mirror source problem. In that case, please switch the mirror source and try again.
```

## Step 1: Download City Scene Data

Before the simulation starts, it is necessary to download the city scene data file of [Beijing](https://cloud.tsinghua.edu.cn/f/f5c777485d2748fa8535/?dl=1), and save it as `./data/beijing_map.pb`.

## Step 2: Edit Configurations

We need to create one configuration file, which is assumed to be named `exp_config.yaml`.
An example configuration file is shown below, you can refer to it to create your own configuration file, remember to replace the placeholders with your own values.

``` yaml
llm: [ { api_key: <API-KEY>, base_url: <BASE-URL>, model: <YOUR-MODEL>, provider: <PROVIDER> } ]
env:
  avro:
    enabled: true # Whether to enable Avro
    path: <AVRO-OUTPUT-PATH> # Path to the Avro output file
  mlflow:
    enabled: true # Whether to enable MLflow
    mlflow_uri: http://localhost:59000 # MLflow server URI``
    username: <CHANGE_ME> # MLflow server username
    password: <CHANGE_ME> # MLflow server password
  pgsql:
    enabled: false # Whether to enable PostgreSQL
    dsn: postgresql://postgres:CHANGE_ME@localhost:5432/postgres # PostgreSQL connection string
  redis:
    server: <REDIS-SERVER> # Redis server address
    port: 6379 # Redis port
    password: <CHANGE_ME> # Redis password
map:
  file_path: <MAP-FILE-PATH> # Path to the map file
  cache_path: <CACHE-FILE-PATH> # Cache path for accelerating map file loading
agents:
  citizens: [ { agent_class: citizen, memory_config_func: null, memory_distributions: null, number: 100, init_funcs: [] } ]
exp:
  name: test # Experiment name
  environment:
    start_tick: 28800 # Start time in seconds
    total_tick: 7200 # Total time in seconds
  message_intercept:
    blocks: [] # List of message interception blocks
    listener: null # Message listener
    mode: point # Message interception mode, options: point, edge
  workflow:
  - func: null
    steps: 60 # Number of step to run the function
    ticks_per_step: 300 # Number of ticks per step - used for [RUN, STEP] type. For example, if it is 300, then the step will run 300 ticks in the environment.
    type: step # The type of the workflow step
advanced:
  group_size: 200 # Group size for each agentgroup
  logging_level: info # Logging level, options: debug, info, warning, error
```

```{admonition} Hint
:class: hint
You can run `agentsociety check -c exp_config.yaml` to check if your own configuration file is valid.
```

## Step 3：Launch the Simulation

1. From Python Code

```python
from agentsociety.configs import load_config_from_file, Config
import ray
import asyncio
import logging
from agentsociety.simulation import AgentSociety

ray.init(logging_level=logging.WARNING, log_to_driver=True)
config = load_config_from_file(
    filepath="exp_config.yaml",
    config_type=Config,
)


async def main():
    agentsociety = AgentSociety(config)
    await agentsociety.init()
    await agentsociety.run()
    await agentsociety.close()
    ray.shutdown()


if __name__ == "__main__":
    asyncio.run(main())

```

Fill in the placeholders in the configuration file with your own values, and run the code above to start the simulation.

2. From Command Line

```bash
agentsociety run -c exp_config.yaml
```

After running the command above, you will see the following output, indicating that the simulation has been successfully launched.
![ExampleStart](../_static/01-exp-start.png)

When the simulation is running, you will see the following output.
![ExampleRunning](../_static/01-exp-running.png)

After the simulation is finished, you will see the following output.
![ExampleClose](../_static/01-exp-close.png)

```{admonition} Note
:class: note
When the simulation is over, you can see an error `exception asyncio.CancelledError` in the output. This is normal and can be ignored.
```

## Step4：View the Results

```{admonition} Caution
:class: caution
To use this interface, you MUST deploy PostgreSQL, MLflow and Redis first.
```

When the simulation is done (or is running), you can use our visualization tool within the python package `agentsociety ui` to replay the simulation.

To activate the ui interface, you simply need to code these in your terminal, the `exp_config.yaml` is just the same file as the one you used to run the simulation.
```bash
agentsociety ui -c exp_config.yaml
```

Running the code above will activate the UI Interface, as shown below.

![start-ui](../_static/01-start-ui.png)

![home-page](../_static/01-ui-home-page.jpg) 

![exp-list](../_static/01-exp-list.jpg)

## Next Step

Congratulations🎇! Now that we have successfully completed a large model-driven social simulation, let's take it a step further and explore how to modify certain settings in the virtual world to [conduct social experiments](./03-conduct-your-first-experiment.md).
