import asyncio
from collections import deque
from copy import deepcopy
from dataclasses import dataclass
from typing import Any, Literal, Optional, Union

from fastembed import SparseTextEmbedding

from ..environment import Environment
from ..logger import get_logger
from ..memory.const import SocialRelation
from ..utils.decorators import lock_decorator
from ..vectorstore import VectorStore
from .const import *

__all__ = [
    "KVMemory",
    "StreamMemory",
    "Memory",
]


class KVMemory:
    def __init__(
        self,
        init_data: dict[str, Any],
        embedding: SparseTextEmbedding,
        should_embed_fields: set[str],
        semantic_templates: dict[str, str],
        key2topic: dict[str, str],
    ):
        """
        Initialize the StatusMemory with three types of memory.

        - **Args**:
            - `init_data` (dict[str, Any]): The initial data to initialize the memory.
            - `embedding` (SparseTextEmbedding): The embedding object.
            - `should_embed_fields` (set[str]): The fields that require embedding.
            - `semantic_templates` (dict[str, str]): The semantic templates for generating embedding text.
            - `key2topic` (dict[str, str]): The mapping of key to topic.
        """
        self._data = init_data
        self._vectorstore = VectorStore(embedding)
        self._semantic_templates = semantic_templates
        self._should_embed_fields = should_embed_fields
        self._key2topic = key2topic
        self._key_to_doc_id = {}
        self._lock = asyncio.Lock()

    async def initialize_embeddings(self) -> None:
        """Initialize embeddings for all fields that require them."""

        # Create embeddings for each field that requires it
        documents = []
        keys = []

        # Collect documents and keys from all memory types
        for key, value in self._data.items():
            if self.should_embed(key):
                semantic_text = self._generate_semantic_text(key, value)
                documents.append(semantic_text)
                keys.append(key)

        # Add all documents in one batch
        doc_ids = await self._vectorstore.add_documents(
            documents=documents,
            extra_tags={
                "key": keys,
            },
        )

        # Map document IDs back to their keys
        for key, doc_id in zip(keys, doc_ids):
            self._key_to_doc_id[key] = doc_id

    def _generate_semantic_text(self, key: str, value: Any) -> str:
        """
        Generate semantic text for a given key and value.
        """
        if key in self._semantic_templates:
            return self._semantic_templates[key].format(value)
        return f"My {key} is {value}"

    @lock_decorator
    async def search(
        self, query: str, top_k: int = 3, filter: Optional[dict] = None
    ) -> str:
        """
        Search for relevant memories based on the provided query.

        - **Args**:
            - `query` (str): The text query to search for.
            - `top_k` (int, optional): Number of top relevant memories to return. Defaults to 3.
            - `filter` (Optional[dict], optional): Additional filters for the search. Defaults to None.

        - **Returns**:
            - `str`: Formatted string of the search results.
        """
        filter_dict = {}
        if filter is not None:
            filter_dict.update(filter)
        top_results: list[tuple[str, float, dict]] = (
            await self._vectorstore.similarity_search(
                query=query,
                k=top_k,
                filter=filter_dict,
            )
        )
        # formatted results
        formatted_results = []
        for content, score, metadata in top_results:
            formatted_results.append(f"- {content} ")

        return "\n".join(formatted_results)

    def should_embed(self, key: str) -> bool:
        return key in self._should_embed_fields

    @lock_decorator
    async def get(
        self,
        key: Any,
        default_value: Optional[Any] = None,
    ) -> Any:
        """
        Retrieve a value from the memory.

        - **Args**:
            - `key` (Any): The key to retrieve.
            - `default_value` (Optional[Any], optional): Default value if the key is not found. Defaults to None.

        - **Returns**:
            - `Any`: The retrieved value or the default value if the key is not found.

        - **Raises**:
            - `ValueError`: If an invalid mode is provided.
            - `KeyError`: If the key is not found in any of the memory sections and no default value is provided.
        """

        if key in self._data:
            return deepcopy(self._data[key])
        else:
            if default_value is None:
                raise KeyError(f"No attribute `{key}` in memories!")
            else:
                return default_value

    @lock_decorator
    async def update(
        self,
        key: Any,
        value: Any,
        mode: Union[Literal["replace"], Literal["merge"]] = "replace",
        protect_llm_read_only_fields: bool = True,
    ) -> None:
        """
        Update a value in the memory and refresh embeddings if necessary.

        - **Args**:
            - `key` (Any): The key to update.
            - `value` (Any): The new value to set.
            - `mode` (Union[Literal["replace"], Literal["merge"]], optional): Update mode. Defaults to "replace".
            - `protect_llm_read_only_fields` (bool, optional): Whether to protect certain fields from being updated. Defaults to True.

        - **Raises**:
            - `ValueError`: If an invalid update mode is provided.
            - `KeyError`: If the key is not found in any of the memory sections.
        """
        # Check if the key is in protected fields
        if protect_llm_read_only_fields:
            if any(key in _attrs for _attrs in [STATE_ATTRIBUTES]):
                get_logger().warning(f"Trying to write protected key `{key}`!")
                return

        # If key doesn't exist, add it directly
        if key not in self._data:
            self._data[key] = value
            # Check if we should embed this field
            if self.should_embed(key):
                semantic_text = self._generate_semantic_text(key, value)
                # Add embedding for new key
                doc_ids = await self._vectorstore.add_documents(
                    documents=[semantic_text],
                    extra_tags={
                        "key": key,
                    },
                )
                self._key_to_doc_id[key] = doc_ids[0]
            return

        # Update existing key
        if mode == "replace":
            # Replace the value directly
            self._data[key] = value

            # Update embeddings if needed
            if self.should_embed(key):
                semantic_text = self._generate_semantic_text(key, value)

                # Delete old embedding if it exists
                if key in self._key_to_doc_id and self._key_to_doc_id[key]:
                    await self._vectorstore.delete_documents(
                        to_delete_ids=[self._key_to_doc_id[key]],
                    )

                # Add new embedding
                doc_ids = await self._vectorstore.add_documents(
                    documents=[semantic_text],
                    extra_tags={
                        "key": key,
                    },
                )
                self._key_to_doc_id[key] = doc_ids[0]

        elif mode == "merge":
            # Get current value
            original_value = self._data[key]

            # Merge based on the type of original value
            if isinstance(original_value, set):
                original_value.update(set(value))
            elif isinstance(original_value, dict):
                original_value.update(dict(value))
            elif isinstance(original_value, list):
                original_value.extend(list(value))
            elif isinstance(original_value, deque):
                original_value.extend(deque(value))
            else:
                # Fall back to replace if merge is not supported
                get_logger().debug(
                    f"Type of {type(original_value)} does not support mode `merge`, using `replace` instead!"
                )
                self._data[key] = value

            # Update embeddings if needed
            if self.should_embed(key):
                semantic_text = self._generate_semantic_text(key, self._data[key])

                # Delete old embedding if it exists
                if key in self._key_to_doc_id and self._key_to_doc_id[key]:
                    await self._vectorstore.delete_documents(
                        to_delete_ids=[self._key_to_doc_id[key]],
                    )

                # Add new embedding
                doc_ids = await self._vectorstore.add_documents(
                    documents=[semantic_text],
                    extra_tags={
                        "key": key,
                    },
                )
                self._key_to_doc_id[key] = doc_ids[0]
        else:
            # Invalid mode
            raise ValueError(f"Invalid update mode `{mode}`!")

    @lock_decorator
    async def export_topic(self, topic: str) -> dict[str, Any]:
        """
        Export the memory of a given topic.
        """
        result = {}
        keys = [k for k, t in self._key2topic.items() if t == topic]
        for k in keys:
            result[k] = deepcopy(self._data[k])
        return result

@dataclass
class MemoryNode:
    """
    A data class representing a memory node.

    - **Attributes**:
        - `tag`: The tag associated with the memory node.
        - `day`: Day of the event or memory.
        - `t`: Time stamp or order.
        - `location`: Location where the event occurred.
        - `description`: Description of the memory.
        - `cognition_id`: ID related to cognitive memory (optional).
        - `id`: Unique ID for this memory node (optional).
    """

    topic: str
    day: int
    t: int
    location: str
    description: str
    cognition_id: Optional[int] = None  # ID related to cognitive memory
    id: Optional[int] = None  # Unique ID for the memory node


class StreamMemory:
    """
    A class used to store and manage time-ordered stream information.

    - **Attributes**:
        - `_memories`: A deque to store memory nodes with a maximum length limit.
        - `_memory_id_counter`: An internal counter to generate unique IDs for each new memory node.
        - `_vectorstore`: The Faiss query object for search functionality.
        - `_agent_id`: Identifier for the agent owning these memories.
        - `_status_memory`: The status memory object.
        - `_simulator`: The simulator object.
    """

    def __init__(
        self,
        environment: Environment,
        status_memory: KVMemory,
        embedding: SparseTextEmbedding,
        max_len: int = 1000,
    ):
        """
        Initialize an instance of StreamMemory.

        - **Args**:
            - `environment` (Environment): The environment object.
            - `vectorstore` (VectorStore): The Faiss query object.
            - `max_len` (int): Maximum length of the deque. Default is 1000.
        """
        self._memories: deque = deque(maxlen=max_len)  # Limit the maximum storage
        self._memory_id_counter: int = 0  # Used for generating unique IDs
        self._status_memory = status_memory
        self._environment = environment
        self._vectorstore = VectorStore(embedding)

    async def add(self, topic: str, description: str) -> int:
        """
        A generic method for adding a memory node and returning the memory node ID.

        - **Args**:
            - `tag` (MemoryTag): The tag associated with the memory node.
            - `description` (str): Description of the memory.

        - **Returns**:
            - `int`: The unique ID of the newly added memory node.
        """
        day, t = self._environment.get_datetime()
        position = await self._status_memory.get("position")
        if "aoi_position" in position:
            location = position["aoi_position"]["aoi_id"]
        elif "lane_position" in position:
            location = position["lane_position"]["lane_id"]
        else:
            location = "unknown"

        current_id = self._memory_id_counter
        self._memory_id_counter += 1
        memory_node = MemoryNode(
            topic=topic,
            day=day,
            t=t,
            location=location,
            description=description,
            id=current_id,
        )
        self._memories.append(memory_node)

        # create embedding for new memories
        await self._vectorstore.add_documents(
            documents=[description],
            extra_tags={
                "topic": topic,
                "day": day,
                "time": t,
            },
        )

        return current_id

    async def get_related_cognition(self, memory_id: int) -> Union[MemoryNode, None]:
        """
        Retrieve the related cognition memory node by its ID.

        - **Args**:
            - `memory_id` (int): The ID of the memory to find related cognition for.

        - **Returns**:
            - `Optional[MemoryNode]`: The related cognition memory node, if found; otherwise, None.
        """
        for m in self._memories:
            if m.topic == "cognition" and m.id == memory_id:
                return m
        return None

    async def format_memory(self, memories: list[MemoryNode]) -> str:
        """
        Format a list of memory nodes into a readable string representation.

        - **Args**:
            - `memories` (list[MemoryNode]): List of MemoryNode objects to format.

        - **Returns**:
            - `str`: A formatted string containing the details of each memory node.
        """
        formatted_results = []
        for memory in memories:
            memory_topic = memory.topic
            memory_day = memory.day
            memory_time_seconds = memory.t
            cognition_id = memory.cognition_id

            # Format time
            if memory_time_seconds != "unknown":
                hours = memory_time_seconds // 3600
                minutes = (memory_time_seconds % 3600) // 60
                seconds = memory_time_seconds % 60
                memory_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                memory_time = "unknown"

            memory_location = memory.location

            # Add cognition information (if exists)
            cognition_info = ""
            if cognition_id is not None:
                cognition_memory = await self.get_related_cognition(cognition_id)
                if cognition_memory:
                    cognition_info = (
                        f"\n  Related cognition: {cognition_memory.description}"
                    )

            formatted_results.append(
                f"- [{memory_topic}]: {memory.description} [day: {memory_day}, time: {memory_time}, "
                f"location: {memory_location}]{cognition_info}"
            )
        return "\n".join(formatted_results)

    async def get_by_ids(self, memory_ids: list[int]) -> str:
        """Retrieve memories by specified IDs"""
        memories = [memory for memory in self._memories if memory.id in memory_ids]
        sorted_results = sorted(memories, key=lambda x: (x.day, x.t), reverse=True)
        return await self.format_memory(sorted_results)

    async def search(
        self,
        query: str,
        topic: Optional[str] = None,
        top_k: int = 3,
        day_range: Optional[tuple[int, int]] = None,
        time_range: Optional[tuple[int, int]] = None,
    ) -> str:
        """
        Search stream memory with optional filters and return formatted results.

        - **Args**:
            - `query` (str): The text to use for searching.
            - `tag` (Optional[MemoryTag], optional): Filter memories by this tag. Defaults to None.
            - `top_k` (int, optional): Number of top relevant memories to return. Defaults to 3.
            - `day_range` (Optional[tuple[int, int]], optional): Tuple of start and end days for filtering. Defaults to None.
            - `time_range` (Optional[tuple[int, int]], optional): Tuple of start and end times for filtering. Defaults to None.

        - **Returns**:
            - `str`: Formatted string of the search results.
        """
        filter_dict: dict[str, Any] = {"type": "stream"}

        if topic:
            filter_dict["topic"] = topic

        # Add time range filter
        if day_range:
            start_day, end_day = day_range
            filter_dict["day"] = lambda x: start_day <= x <= end_day

        if time_range:
            start_time, end_time = time_range
            filter_dict["time"] = lambda x: start_time <= x <= end_time

        top_results = await self._vectorstore.similarity_search(
            query=query,
            k=top_k,
            filter=filter_dict,
        )

        # Sort results by time (first by day, then by time)
        sorted_results = sorted(
            top_results,
            key=lambda x: (x[2].get("day", 0), x[2].get("time", 0)),
            reverse=True,
        )

        formatted_results = []
        for content, score, metadata in sorted_results:
            memory_topic = metadata.get("topic", "unknown")
            memory_day = metadata.get("day", "unknown")
            memory_time_seconds = metadata.get("time", "unknown")
            cognition_id = metadata.get("cognition_id", None)

            # Format time
            if memory_time_seconds != "unknown":
                hours = memory_time_seconds // 3600
                minutes = (memory_time_seconds % 3600) // 60
                seconds = memory_time_seconds % 60
                memory_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                memory_time = "unknown"

            memory_location = metadata.get("location", "unknown")

            # Add cognition information (if exists)
            cognition_info = ""
            if cognition_id is not None:
                cognition_memory = await self.get_related_cognition(cognition_id)
                if cognition_memory:
                    cognition_info = (
                        f"\n  Related cognition: {cognition_memory.description}"
                    )

            formatted_results.append(
                f"- [{memory_topic}]: {content} [day: {memory_day}, time: {memory_time}, "
                f"location: {memory_location}]{cognition_info}"
            )
        return "\n".join(formatted_results)

    async def search_today(
        self,
        query: str = "",  # Optional query text
        topic: Optional[str] = None,
        top_k: int = 100,  # Default to a larger number to ensure all memories of the day are retrieved
    ) -> str:
        """Search all memory events from today

        - **Args**:
            query: Optional query text, returns all memories of the day if empty
            tag: Optional memory tag for filtering specific types of memories
            top_k: Number of most relevant memories to return, defaults to 100

        - **Returns**:
            str: Formatted text of today's memories
        """
        current_day, _ = self._environment.get_datetime()
        # Use the search method, setting day_range to today
        return await self.search(
            query=query, topic=topic, top_k=top_k, day_range=(current_day, current_day)
        )

    async def add_cognition_to_memory(
        self, memory_ids: list[int], cognition: str
    ) -> None:
        """
        Add cognition to existing memory nodes.

        - **Args**:
            - `memory_ids` (Union[int, list[int]]): ID or list of IDs of the memories to which cognition will be added.
            - `cognition` (str): Description of the cognition to add.
        """
        # Find all corresponding memories
        target_memories = []
        for memory in self._memories:
            if memory.id in memory_ids:
                target_memories.append(memory)

        if not target_memories:
            raise ValueError(f"No memories found with ids {memory_ids}")

        # Add cognitive memory
        cognition_id = await self.add(topic="cognition", description=cognition)

        # Update the cognition_id of all original memories
        for target_memory in target_memories:
            target_memory.cognition_id = cognition_id

    async def get_all(self) -> list[dict]:
        """
        Retrieve all stream memory nodes as dictionaries.

        - **Returns**:
            - `list[dict]`: List of all memory nodes as dictionaries.
        """
        return [
            {
                "id": memory.id,
                "cognition_id": memory.cognition_id,
                "tag": memory.tag.value,
                "location": memory.location,
                "description": memory.description,
                "day": memory.day,
                "t": memory.t,
            }
            for memory in self._memories
        ]


class Memory:
    """
    A class to manage different types of memory (state, profile, dynamic).

    - **Attributes**:
        - `_state` (`StateMemory`): Stores state-related data.
        - `_profile` (`ProfileMemory`): Stores profile-related data.
        - `_dynamic` (`DynamicMemory`): Stores dynamically configured data.

    - **Methods**:
        - `set_search_components`: Sets the search components for stream and status memory.

    """

    def __init__(
        self,
        environment: Environment,
        embedding: SparseTextEmbedding,
        config: Optional[dict[Any, Any]] = None,
        profile: Optional[dict[Any, Any]] = None,
        base: Optional[dict[Any, Any]] = None,
    ) -> None:
        """
        Initializes the Memory with optional configuration.

        - **Description**:
            Sets up the memory management system by initializing different memory types (state, profile, dynamic)
            and configuring them based on provided parameters. Also initializes watchers and locks for thread-safe operations.

        - **Args**:
            - `environment` (Environment): The environment object.
            - `vectorstore` (VectorStore): The Faiss query object.
            - `config` (Optional[dict[Any, Any]], optional):
                Configuration dictionary for dynamic memory, where keys are field names and values can be tuples or callables.
                Defaults to None.
            - `profile` (Optional[dict[Any, Any]], optional): Dictionary for profile attributes.
                Defaults to None.
            - `base` (Optional[dict[Any, Any]], optional): Dictionary for base attributes from City Simulator.
                Defaults to None.

        - **Returns**:
            - `None`
        """
        self._lock = asyncio.Lock()
        self._environment = environment
        self._embedding = embedding
        self._semantic_templates: dict[str, str] = {}
        self._should_embed_fields: set[str] = set()

        init_data = {}
        key2topic = {}
        if config is not None:
            for k, v in config.items():
                try:
                    # Handle configurations of different lengths
                    if isinstance(v, tuple):
                        if len(v) == 4:  # (_type, _value, enable_embedding, template)
                            _type, _value, enable_embedding, template = v
                            if enable_embedding:
                                self._should_embed_fields.add(k)
                            self._semantic_templates[k] = template
                        elif len(v) == 3:  # (_type, _value, enable_embedding)
                            _type, _value, enable_embedding = v
                            if enable_embedding:
                                self._should_embed_fields.add(k)
                        else:  # (_type, _value)
                            _type, _value = v
                    else:
                        _type = type(v)
                        _value = v

                    # Process type conversion
                    try:
                        if isinstance(_type, type):
                            _value = _type(_value)
                        else:
                            if isinstance(_type, deque):
                                _type.extend(_value)
                                _value = deepcopy(_type)
                            else:
                                get_logger().warning(
                                    f"type `{_type}` is not supported!"
                                )
                    except TypeError as e:
                        get_logger().warning(f"Type conversion failed for key {k}: {e}")
                except TypeError as e:
                    if isinstance(v, type):
                        _value = v()
                    else:
                        _value = v

                if (
                    k in PROFILE_ATTRIBUTES
                    or k in STATE_ATTRIBUTES
                ) and k != "id":
                    get_logger().warning(f"key `{k}` already declared in memory!")
                    continue

                init_data[k] = deepcopy(_value)

        if profile is not None:
            for k, v in profile.items():
                if k not in PROFILE_ATTRIBUTES:
                    get_logger().warning(f"key `{k}` is not a correct `profile` field!")
                    continue
                try:
                    # Handle configuration tuple formats
                    if isinstance(v, tuple):
                        if len(v) == 4:  # (_type, _value, enable_embedding, template)
                            _type, _value, enable_embedding, template = v
                            if enable_embedding:
                                self._should_embed_fields.add(k)
                            self._semantic_templates[k] = template
                        elif len(v) == 3:  # (_type, _value, enable_embedding)
                            _type, _value, enable_embedding = v
                            if enable_embedding:
                                self._should_embed_fields.add(k)
                        else:  # (_type, _value)
                            _type, _value = v

                        # Process type conversion
                        try:
                            if isinstance(_type, type):
                                _value = _type(_value)
                            else:
                                if k == "social_network":
                                    _value = [SocialRelation(**_v) for _v in _value]
                                elif isinstance(_type, deque):
                                    _type.extend(_value)
                                    _value = deepcopy(_type)
                                else:
                                    get_logger().warning(
                                        f"[Profile] type `{_type}` is not supported!"
                                    )
                        except TypeError as e:
                            get_logger().warning(
                                f"Type conversion failed for key {k}: {e}"
                            )
                    else:
                        # Maintain compatibility with simple key-value pairs
                        if k == "social_network":
                            _value = [SocialRelation(**_v) for _v in v]
                        else:
                            _value = v
                except TypeError as e:
                    if isinstance(v, type):
                        _value = v()
                    else:
                        _value = v
                init_data[k] = deepcopy(_value)
                key2topic[k] = "profile"

        if base is not None:
            for k, v in base.items():
                if k not in STATE_ATTRIBUTES:
                    get_logger().warning(f"key `{k}` is not a correct `base` field!")
                    continue
                init_data[k] = deepcopy(v)

        # Combine StatusMemory and pass embedding_fields information
        self._status = KVMemory(
            init_data=init_data,
            embedding=self._embedding,
            should_embed_fields=self._should_embed_fields,
            semantic_templates=self._semantic_templates,
            key2topic=key2topic,
        )

        # Add StreamMemory
        self._stream = StreamMemory(
            environment=self._environment,
            embedding=self._embedding,
            status_memory=self._status,
        )

    @property
    def status(self) -> KVMemory:
        return self._status

    @property
    def stream(self) -> StreamMemory:
        return self._stream

    async def initialize_embeddings(self):
        """
        Initialize embeddings within the status memory.

        - **Description**:
            - Asynchronously initializes embeddings for the status memory component, which prepares the system for performing searches.

        - **Returns**:
        """
        await self._status.initialize_embeddings()
