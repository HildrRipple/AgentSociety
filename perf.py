import os
import importlib.util
import ray
import json
from typing import Dict, Any, Type

from agentsociety.configs import Config, LLMConfig, EnvConfig, MapConfig, AgentsConfig, AgentConfig, ExpConfig, WorkflowStepConfig, WorkflowType, EnvironmentConfig
from agentsociety.llm import LLMProviderType
from agentsociety.simulation import AgentSociety
from agentsociety.cityagent import default


async def run():
    """
    Run the agent simulation with the given file.
    
    Args:
        file_path: Path to the input file (Python or JSON)
        is_json: Whether the input file is JSON (True) or Python (False)
        profile_path: Optional path to the profile file
    """

    # Default configurations
    llm_configs = [
        LLMConfig(
            provider=LLMProviderType.VLLM,
            base_url="https://cloud.infini-ai.com/maas/v1",
            api_key="sk-acu5ev2rhrtidz6y",
            model="qwen2.5-14b-instruct",
            semaphore=200,
        ),
    ]

    env_config = EnvConfig.model_validate({
        "db": {
            "enabled": True,
        },
    })

    map_config = MapConfig(
        file_path="__test/srt.map_beijing_extend_20241201.pb",
    )

    config = Config(
        llm=llm_configs,
        env=env_config,
        map=map_config,
        agents=AgentsConfig(
            citizens=[
                AgentConfig(
                    agent_class="citizen",
                    number=10000,
                )
            ],
            firms=[],
            banks=[],
            nbs=[],
            governments=[],
            others=[],
            supervisor=None,
            init_funcs=[],
        ),
        exp=ExpConfig(
            name="hurricane_impact",
            workflow=[
                WorkflowStepConfig(
                    type=WorkflowType.STEP,
                    steps=1,
                ),
            ],
            environment=EnvironmentConfig(
                start_tick=6 * 60 * 60,
            ),
        ),
    )

    config = default(config)
    agentsociety = AgentSociety(config)
    await agentsociety.init()
    await agentsociety.run()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run())
