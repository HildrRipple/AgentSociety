# Conduct Your First Experiment with Interventions

This guide will help you conduct a simple experiment involving interventions and data collection. We'll walk through how to introduce interventions such as weather changes, collect relevant data, and store it using MLflow.

## Step 1: Adding Interventions

Interventions can be introduced by modifying the environment or agent properties within the simulation code. In this example, we will change the weather conditions during the simulation.

### Example of Setting Weather Interventions

Here’s how you can modify the global weather condition in your Python code:

```python
import asyncio
import logging
from typing import Literal, Union

import ray

from agentsociety.cityagent.metrics import mobility_metric
from agentsociety.configs import (AgentsConfig, Config, EnvConfig, ExpConfig,
                                  LLMConfig, MapConfig)
from agentsociety.configs.agent import AgentClassType, AgentConfig
from agentsociety.configs.exp import (MetricExtractorConfig, MetricType,
                                      WorkflowStepConfig, WorkflowType)
from agentsociety.environment import EnvironmentConfig
from agentsociety.llm import LLMProviderType
from agentsociety.message import RedisConfig
from agentsociety.metrics import MlflowConfig
from agentsociety.simulation import AgentSociety
from agentsociety.storage import AvroConfig, PostgreSQLConfig

logging.getLogger("agentsociety").setLevel(logging.INFO)

ray.init(logging_level=logging.WARNING, log_to_driver=False)


async def update_weather_and_temperature(
    weather: Union[Literal["wind"], Literal["no-wind"]], simulation: AgentSociety
):
    if weather == "wind":
        await simulation.update_environment(
            "weather",
            "Hurricane Dorian has made landfall in other cities, travel is slightly affected, and winds can be felt",
        )
    elif weather == "no-wind":
        await simulation.update_environment(
            "weather", "The weather is normal and does not affect travel"
        )
    else:
        raise ValueError(f"Invalid weather {weather}")
```

For more details on agent properties and configurations, refer to the [Agent Description Documentation](../04-custom-agents/01-concept.md).

### Add Intervention to Workflow

Add the weather intervention to your workflow configuration:

```python
config = Config(
    llm=[
        LLMConfig(
            provider=LLMProviderType.Qwen,
            base_url=None,
            api_key="<YOUR-API-KEY>",
            model="<YOUR-MODEL>",
            semaphore=200,
        )
    ],
    env=EnvConfig(
        redis=RedisConfig(
            server="<SERVER-ADDRESS>",
            port=6379,
            password="<PASSWORD>",
        ),  # type: ignore
        pgsql=PostgreSQLConfig(
            enabled=True,
            dsn="<PGSQL-DSN>",
            num_workers="auto",
        ),
        avro=AvroConfig(
            path="<SAVE-PATH>",
            enabled=True,
        ),
        mlflow=MlflowConfig(
            enabled=True,
            mlflow_uri="<MLFLOW-URI>",
            username="<USERNAME>",
            password="<PASSWORD>",
        ),
    ),
    map=MapConfig(
        file_path="<MAP-FILE-PATH>",
        cache_path="<CACHE-FILE-PATH>",
    ),
    agents=AgentsConfig(
        citizens=[
            AgentConfig(
                agent_class=AgentClassType.CITIZEN,
                number=100,
            )
        ]
    ),  # type: ignore
    exp=ExpConfig(
        name="social_control",
        workflow=[
            WorkflowStepConfig(
                type=WorkflowType.INTERVENE,
                func=update_weather_and_temperature,
            ),
            WorkflowStepConfig(
                type=WorkflowType.RUN,
                days=3,
            ),
            WorkflowStepConfig(
                type=WorkflowType.INTERVENE,
                func=update_weather_and_temperature,
            ),
            WorkflowStepConfig(
                type=WorkflowType.RUN,
                days=3,
            ),
        ],
        environment=EnvironmentConfig(
            start_tick=6 * 60 * 60,
            total_tick=18 * 60 * 60,
        ),
        metric_extractors=[
            MetricExtractorConfig(
                type=MetricType.FUNCTION,
                func=mobility_metric,
                step_interval=1,
            )
        ],
    ),
)

```

## Step 2: Storing Data with MLflow

Collect relevant data during the simulation. This could include numerical data such as population movement patterns or resource usage.

### Example of Collecting Data

Use the following code snippet to extract metrics and send them to MLflow:

```python
from agentsociety.cityagent.metrics import mobility_metric

exp_config.SetMetricExtractors(metric_extractors=[(1, mobility_metric)])
```

For more information on data collection APIs and methods, refer to the [Metric Collection Documentation](../03-experiment-design/02-metrics-collection.md).

### Example of Storing Data in MLflow

Ensure that your MLflow setup is correctly configured in your simulation environment configuration file. 

```yaml
env:
  mlflow:
    enabled: true # Whether to enable MLflow
    mlflow_uri: http://localhost:59000 # MLflow server URI``
    username: <CHANGE_ME> # MLflow server username
    password: <CHANGE_ME> # MLflow server password
```


## Step 3: Running the Simulation

To run the simulation, use the following script:

```python
async def main():
    agentsociety = AgentSociety(config)
    await agentsociety.init()
    await agentsociety.run()
    await agentsociety.close()
    ray.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
```

## Step 4: Analyzing Experiment Results

After completing the first experiment, analyze the results to understand the impact of the interventions and data collected.

### Example of Analyzing Results

Review the logs and visualizations provided by MLflow to interpret the outcomes of your experiment. Based on these insights, you can plan and execute larger and more complex experiments.

## Next Steps

Congratulations! You have successfully completed your first experiment. To expand your research, consider implementing custom agents with richer functionalities. Refer to the [Design Experiment](../03-experiment-design/index.md) and [Custom Agent](../04-custom-agents/index.md) for guidance on creating advanced agents and integrating them into your simulations.
