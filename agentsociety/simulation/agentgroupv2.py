from typing import Any, Optional

import ray

from ..agent import Agent
from ..cityagent.memory_config import MemoryConfigGenerator
from ..configs import Config
from ..environment import Environment
from ..llm import LLM, init_embedding
from ..logger import get_logger, set_logger_level
from ..memory import FaissQuery, Memory
from ..message import Messager
from ..metrics import MlflowClient
from ..storage import AvroSaver

__all__ = ["AgentGroupV2"]


@ray.remote
class AgentGroupV2:
    def __init__(
        self,
        tenant_id: str,
        exp_name: str,
        exp_id: str,
        group_id: str,
        config: Config,
        agent_inits: list[tuple[int, type[Agent], MemoryConfigGenerator, int]],
        environment_init: dict,
        # PostgreSQL
        pgsql_writer: Optional[ray.ObjectRef],
        # Message Interceptor
        message_interceptor: ray.ObjectRef,
        # MLflow
        mlflow_run_id: Optional[str],
        # Others
        agent_config_file: Optional[dict[type[Agent], Any]] = None,
    ):
        """
        Initialize the AgentGroupV2.

        """
        set_logger_level(config.logging_level)

        self._tenant_id = tenant_id
        self._exp_name = exp_name
        self._exp_id = exp_id
        self._group_id = group_id
        self._config = config
        self._agent_inits = agent_inits
        self._environment_init = environment_init
        self._pgsql_writer = pgsql_writer
        self._message_interceptor = message_interceptor
        self._mlflow_run_id = mlflow_run_id
        self._agent_config_file = agent_config_file
        self._embedding_model = init_embedding(config.embedding_model)
        self._faiss_query = FaissQuery(self._embedding_model)

        # typing definition
        self._llm: Optional[LLM] = None
        self._environment: Optional[Environment] = None
        self._messager: Optional[Messager] = None
        self._avro_saver: Optional[AvroSaver] = None
        self._mlflow_client: Optional[MlflowClient] = None

        self._agents: list[Agent] = []
    @property
    def config(self):
        return self._config

    @property
    def embedding_model(self):
        return self._embedding_model

    @property
    def faiss_query(self):
        return self._faiss_query

    @property
    def llm(self):
        assert self._llm is not None, "llm is not initialized"
        return self._llm

    @property
    def environment(self):
        assert self._environment is not None, "environment is not initialized"
        return self._environment

    @property
    def messager(self):
        assert self._messager is not None, "messager is not initialized"
        return self._messager

    async def init(self):
        """Initialize the AgentGroupV2."""

        # ====================
        # Initialize LLM client
        # ====================
        get_logger().info(f"Initializing LLM client...")
        self._llm = LLM(self._config.env.llm)
        get_logger().info(f"LLM client initialized")

        # ====================
        # Initialize environment
        # ====================
        get_logger().info(f"Initializing environment...")
        self._environment = Environment(**self._environment_init)
        get_logger().info(f"Environment initialized")

        # ====================
        # Initialize messager
        # ====================
        get_logger().info(f"Initializing messager...")
        self._messager = Messager(self._config.env.redis, self._exp_id)
        # TODO: message interceptor
        get_logger().info(f"Messager initialized")

        # ====================
        # Initialize the avro saver
        # ====================
        if self._config.env.avro.enabled:
            get_logger().info(f"Initializing the avro saver...")
            self._avro_saver = AvroSaver(
                self._config.env.avro, self._exp_id, self._group_id
            )
            get_logger().info(f"Avro saver initialized")

        # ====================
        # Initialize the mlflow
        # ====================
        if self._config.env.mlflow.enabled:
            get_logger().info(f"Initializing the mlflow...")
            self._mlflow_client = MlflowClient(
                config=self._config.env.mlflow,
                exp_name=self._exp_name,
                exp_id=self._exp_id,
                current_run_id=self._mlflow_run_id,
            )
            get_logger().info(f"Mlflow initialized")

        # ====================================
        # Initialize the agents
        # ====================================
        get_logger().info(f"Initializing the agents...")
        for agent_init in self._agent_inits:
            id, agent_class, memory_config_generator, index_for_generator = agent_init
            memory_dict = memory_config_generator.generate(index_for_generator)
            extra_attributes = memory_dict.get("extra_attributes", {})
            profile = memory_dict.get("profile", {})
            base = memory_dict.get("base", {})
            memory_init = Memory(config=extra_attributes, profile=profile, base=base)

        get_logger().info(f"Agents initialized")

    async def close(self):
        """Close the AgentGroupV2."""

        if self._mlflow_client is not None:
            self._mlflow_client.close()
            self._mlflow_client = None

        if self._avro_saver is not None:
            self._avro_saver.close()
            self._avro_saver = None

        if self._messager is not None:
            await self._messager.close()
            self._messager = None

        if self._environment is not None:
            self._environment.close()
            self._environment = None

        if self._llm is not None:
            await self._llm.close()
            self._llm = None
