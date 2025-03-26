import asyncio
import json
import logging
import pickle as pkl

import ray

from agentsociety import AgentSimulation
from agentsociety.cityagent import memory_config_societyagent
from agentsociety.cityagent.metrics import economy_metric
from agentsociety.cityagent.societyagent import SocietyAgent
from agentsociety.configs import ExpConfig, SimConfig, WorkflowStep, MetricExtractor
from agentsociety.utils import LLMProviderType, WorkflowType, MetricType

logging.getLogger("agentsociety").setLevel(logging.INFO)

ray.init(logging_level=logging.WARNING, log_to_driver=False)


async def gather_ubi_opinions(simulation: AgentSimulation):
    citizen_agents = await simulation.filter(types=[SocietyAgent])
    opinions = await simulation.gather("ubi_opinion", citizen_agents)
    with open("opinions.pkl", "wb") as f:
        pkl.dump(opinions, f)


sim_config = (
    SimConfig()
    .AddLLMConfig(
        provider=LLMProviderType.ZhipuAI, api_key="YOUR-API-KEY", model="GLM-4-Flash"
    )
    .SetSimulatorConfig()
    .SetRedis(server="redis.example.com", port=6379, password="pass")
    # change to your file path
    .SetMapConfig(file_path="map.pb")
    # .SetAvro(path='./__avro', enabled=True)
    .SetPostgreSql(dsn="postgresql://user:pass@localhost:5432/db", enabled=True)
    .SetMetricConfig(
        username="mlflow_user", password="mlflow_pass", mlflow_uri="http://mlflow:59000"
    )
)
exp_config = (
    ExpConfig(
        name="allinone_economy", llm_semaphore=200, logging_level="INFO"
    )
    .SetAgentConfig(
        number_of_citizen=100,
        number_of_firm=5,
        agent_class_configs={
            SocietyAgent: json.load(open("society_agent_config.json"))
        },
    )
    .SetMemoryConfig(
        memory_config_func={SocietyAgent: memory_config_societyagent},
    )
    .SetMetricExtractors(
        metric_extractors=[
            MetricExtractor(
                type=MetricType.FUNCTION, func=economy_metric, step_interval=1
            ),
            MetricExtractor(
                type=MetricType.FUNCTION, func=gather_ubi_opinions, step_interval=12
            ),
        ]
    )
    .SetWorkFlow(
        [
            WorkflowStep(type=WorkflowType.RUN, days=10, times=1, description=""),
        ]
    )
)


async def main():
    await AgentSimulation.run_from_config(exp_config, sim_config)
    ray.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
