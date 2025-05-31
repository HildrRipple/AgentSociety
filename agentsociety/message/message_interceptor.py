import asyncio
import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from copy import deepcopy
from typing import Any, Optional, Set, TypeVar, Union

import networkx as nx
import ray
from ray.util.queue import Empty, Queue

from ..llm import LLM, LLMConfig, monitor_requests
from ..logger import get_logger
from ..utils.decorators import lock_decorator

DEFAULT_ERROR_STRING = """
From `{from_id}` To `{to_id}` abort due to block `{block_name}`
"""

logger = logging.getLogger("message_interceptor")

__all__ = [
    "MessageInterceptor",
]

BlackSetEntry = TypeVar(
    "BlackSetEntry", bound=tuple[Union[int, None], Union[int, None]]
)
BlackSet = Set[BlackSetEntry]

MessageIdentifierEntry = TypeVar(
    "MessageIdentifierEntry", bound=tuple[Union[int, None], Union[int, None], str]
)
MessageIdentifier = dict[MessageIdentifierEntry, bool]


@ray.remote
class MessageInterceptor:
    """
    A class to intercept and process messages based on configured rules.
    """

    def __init__(
        self,
        llm_config: list[LLMConfig],
    ) -> None:
        """
        Initialize the MessageInterceptor with optional configuration.

        - **Args**:
            - `llm_config` (LLMConfig): Configuration dictionary for initializing the LLM instance. Defaults to None.
        """
        self._violation_counts: dict[int, int] = defaultdict(int)
        self._llm = LLM(llm_config)
        # round related
        self.round_blocked_messages_count = 0
        self.round_communicated_agents_count = 0
        self.validation_dict: MessageIdentifier = {}
        # blocked agent ids and blocked social edges
        self.blocked_agent_ids = []
        self.blocked_social_edges = []
        self._lock = asyncio.Lock()

    async def init(self):
        asyncio.create_task(monitor_requests(self._llm))

    async def close(self):
        pass

    # Property accessors
    @property
    def llm(self) -> LLM:
        """
        Access the Large Language Model instance.

        - **Description**:
            - Provides access to the internal LLM instance. Raises an error if accessed before assignment.

        - **Raises**:
            - `RuntimeError`: If accessed before setting the LLM.

        - **Returns**:
            - `LLM`: The Large Language Model instance.
        """
        if self._llm is None:
            raise RuntimeError(f"LLM access before assignment, please `set_llm` first!")
        return self._llm

    # Message forwarding related methods
    @lock_decorator
    async def violation_counts(self) -> dict[int, int]:
        """
        Retrieve the violation counts.

        - **Description**:
            - Returns a deep copy of the violation counts to prevent external modification of the original data.

        - **Returns**:
            - `dict[str, int]`: The dictionary of violation counts.
        """
        return deepcopy(self._violation_counts)

    @lock_decorator
    async def add_message(self, from_id: int, to_id: int, msg: str) -> None:
        self.validation_dict[(from_id, to_id, msg)] = True

    @lock_decorator
    async def forward(self):
        # reset round related variables
        self.round_blocked_messages_count = 0
        self.round_communicated_agents_count = 0
        self.validation_dict = {}

    @lock_decorator
    async def update_blocked_agent_ids(
        self, blocked_agent_ids: Optional[list[int]] = None
    ):
        if blocked_agent_ids is not None:
            self.blocked_agent_ids.extend(blocked_agent_ids)
            self.blocked_agent_ids = list(set(self.blocked_agent_ids))

    @lock_decorator
    async def update_blocked_social_edges(
        self, blocked_social_edges: Optional[list[tuple[int, int]]] = None
    ):
        if blocked_social_edges is not None:
            self.blocked_social_edges.extend(blocked_social_edges)
            self.blocked_social_edges = list(set(self.blocked_social_edges))
            # check can be blocked social edges (not in private network)
            self.blocked_social_edges = [edge for edge in self.blocked_social_edges]

    @lock_decorator
    async def modify_validation_dict(
        self, validation_dict: MessageIdentifier
    ) -> MessageIdentifier:
        # update validation_dict
        self.validation_dict.update(validation_dict)
        # modify validation_dict
        for (from_id, to_id, msg), is_valid in list(self.validation_dict.items()):
            # blocked agent ids
            if from_id in self.blocked_agent_ids:
                is_valid = False
            # blocked social edges
            if (from_id, to_id) in self.blocked_social_edges:
                is_valid = False
            self.validation_dict[(from_id, to_id, msg)] = is_valid
        return self.validation_dict

    @lock_decorator
    async def get_blocked_agent_ids(self) -> list[int]:
        return self.blocked_agent_ids

    @lock_decorator
    async def clear_validation_dict(self) -> None:
        self.validation_dict = {}

    @lock_decorator
    async def get_validation_dict(self) -> MessageIdentifier:
        return self.validation_dict
