import asyncio
import logging

import ray
from hurricane_memory_config import (
    memory_config_societyagent_hurrican,
)

from agentsociety.cityagent import (
    default,
)
from agentsociety.configs import (
    AgentsConfig,
    Config,
    EnvConfig,
    ExpConfig,
    LLMConfig,
    MapConfig,
)
from agentsociety.configs.agent import AgentConfig
from agentsociety.configs.exp import WorkflowStepConfig, WorkflowType
from agentsociety.environment import EnvironmentConfig
from agentsociety.llm import LLMProviderType
from agentsociety.simulation import AgentSociety
from agentsociety.storage import DatabaseConfig

ray.init(logging_level=logging.INFO)


config = Config(
    llm=[
        LLMConfig(
            provider=LLMProviderType.VLLM,
            base_url="https://cloud.infini-ai.com/maas/v1",
            api_key="sk-acu5ev2rhrtidz6y",
            model="qwen2.5-14b-instruct",
            concurrency=200,
            timeout=30,
        )
    ],
    env=EnvConfig(
        db=DatabaseConfig(
            enabled=True,
            db_type="sqlite",
            pg_dsn=None,
        ),
    ),
    map=MapConfig(
        file_path="/root/agentsociety/test/beijing.pb",
    ),
    agents=AgentsConfig(
        citizens=[
            AgentConfig(
                agent_class="citizen",
                number=1000,
                memory_config_func=memory_config_societyagent_hurrican,
                memory_from_file="profiles_hurricane.json",
            )
        ],
    ),  # type: ignore
    exp=ExpConfig(
        name="hurricane_impact",
        workflow=[
            WorkflowStepConfig(
                type=WorkflowType.RUN,
                days=3,
            ),
            WorkflowStepConfig(
                type=WorkflowType.ENVIRONMENT_INTERVENE,
                key="weather",
                value="Hurricane Dorian has made landfall in other cities, travel is slightly affected, and winds can be felt.",
            ),
            WorkflowStepConfig(
                type=WorkflowType.RUN,
                days=3,
            ),
            WorkflowStepConfig(
                type=WorkflowType.ENVIRONMENT_INTERVENE,
                key="weather",
                value="The weather is normal and does not affect travel",
            ),
            WorkflowStepConfig(
                type=WorkflowType.RUN,
                days=3,
            ),
        ],
        environment=EnvironmentConfig(
            start_tick=6 * 60 * 60,
        ),
    ),
)
config = default(config)


async def main():
    agentsociety = AgentSociety(config)
    try:
        await agentsociety.init()
        await agentsociety.run()
    finally:
        await agentsociety.close()
    ray.shutdown()


if __name__ == "__main__":
    asyncio.run(main())
