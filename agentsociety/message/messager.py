import asyncio
import json
import logging
import os
import time
from typing import Any, Optional, Union

import ray
import redis.asyncio as aioredis

from ..utils.decorators import lock_decorator

__all__ = [
    "Messager",
]

logger = logging.getLogger("agentsociety")


@ray.remote
class Messager:
    """
    A class to manage message sending and receiving using Redis pub/sub.

    - **Attributes**:
        - `client` (aioredis.Redis): An instance of the Redis async client.
        - `connected` (bool): Indicates whether the connection to Redis is established.
        - `message_queue` (asyncio.Queue): Queue for storing received messages.
        - `receive_messages_task` (Optional[Task]): Task for listening to incoming messages.
        - `_message_interceptor` (Optional[ray.ObjectRef]): Reference to a remote message interceptor object.
        - `_log_list` (list): List to store message logs.
        - `_lock` (asyncio.Lock): Lock for thread-safe operations.
        - `_topics` (set[str]): Set of topics the client is subscribed to.
    """

    def __init__(
        self,
        hostname: str,
        port: int = 6379,
        username=None,
        password=None,
        timeout=60,
        message_interceptor: Optional[ray.ObjectRef] = None,
    ):
        """
        Initialize the Messager with Redis connection parameters.

        - **Args**:
            - `hostname` (str): The hostname or IP address of the Redis server.
            - `port` (int, optional): Port number of the Redis server. Defaults to 6379.
            - `username` (str, optional): Username for Redis authentication.
            - `password` (str, optional): Password for Redis authentication.
            - `timeout` (int, optional): Connection timeout in seconds. Defaults to 60.
            - `message_interceptor` (Optional[ray.ObjectRef], optional): Reference to a message interceptor object.
        """
        self.client = aioredis.Redis(
            host=hostname,
            port=port,
            username=username,
            password=password,
            socket_timeout=timeout,
        )
        self.connected = False  # whether is messager connected
        self.message_queue = asyncio.Queue()  # store received messages
        self.receive_messages_task = None
        self._message_interceptor = message_interceptor
        self._log_list = []
        self._lock = asyncio.Lock()
        self._topics: set[str] = set()

    @property
    def message_interceptor(self) -> Union[None, ray.ObjectRef]:
        """
        Access the message interceptor reference.

        - **Returns**:
            - `Union[None, ray.ObjectRef]`: The message interceptor reference.
        """
        return self._message_interceptor

    def get_log_list(self):
        """
        Retrieve the list of message logs.

        - **Returns**:
            - `list`: The list of message logs containing message details and metrics.
        """
        return self._log_list

    def clear_log_list(self):
        """
        Clear all message logs.

        - **Description**:
            - Resets the message log list to an empty list.
        """
        self._log_list = []

    def set_message_interceptor(self, message_interceptor: ray.ObjectRef):
        """
        Set the message interceptor reference.

        - **Args**:
            - `message_interceptor` (ray.ObjectRef): The message interceptor reference to be set.
        """
        self._message_interceptor = message_interceptor

    async def __aexit__(self, exc_type, exc_value, traceback):
        """
        Set the message interceptor reference.

        - **Args**:
            - `message_interceptor` (ray.ObjectRef): The message interceptor reference to be set.
        """
        await self.stop()

    async def ping(self):
        """
        Send a ping message to Redis.

        - **Description**:
            - Publishes a 'ping' message on the 'ping' channel to verify connection to Redis.
        """
        await self.client.publish("ping", "ping")

    async def connect(self):
        """
        Attempt to connect to the Redis server up to three times.

        - **Description**:
            - Tries to establish a connection to Redis. Retries up to three times with delays between attempts.
            - Logs success or failure accordingly.
        """
        for i in range(3):
            try:
                await self.client.__aenter__()
                self.connected = True
                logger.info("Connected to Redis")
                return
            except Exception as e:
                logger.error(f"Attempt {i+1}: Failed to connect to Redis: {e}")
                await asyncio.sleep(10)
        self.connected = False
        logger.error("All connection attempts failed.")

    async def disconnect(self):
        """
        Disconnect from the Redis server.

        - **Description**:
            - Closes the connection to Redis and logs the disconnection.
        """
        await self.client.__aexit__(None, None, None)
        self.connected = False
        logger.info("Disconnected from Redis")

    async def is_connected(self):
        """
        Check if the connection to Redis is established.

        - **Returns**:
            - `bool`: True if connected, otherwise False.
        """
        return self.connected

    @lock_decorator
    async def subscribe(
        self, channels: Union[str, list[str]], agents: Union[Any, list[Any]]
    ):
        """
        Subscribe to one or more Redis channels.

        - **Args**:
            - `channels` (Union[str, list[str]]): Channel or list of channels to subscribe to.
            - `agents` (Union[Any, list[Any]]): Agents or list of agents associated with the subscription.

        - **Description**:
            - Adds the specified channels to the set of topics to monitor.
            - Ensures input parameters are properly formatted as lists.
            - The actual subscription happens dynamically in the _listen_for_messages method.
        """
        if not await self.is_connected():
            logger.error(
                f"Cannot subscribe to {channels} because not connected to the Redis."
            )
            return
        if not isinstance(channels, list):
            channels = [channels]
        if not isinstance(agents, list):
            agents = [agents]
        self._topics.update(channels)

    async def fetch_messages(self):
        """
        Retrieve all messages currently in the queue.

        - **Returns**:
            - `list[Any]`: List of messages retrieved from the queue.
        """
        messages = []
        while not self.message_queue.empty():
            messages.append(await self.message_queue.get())
        return messages

    @lock_decorator
    async def send_message(
        self,
        channel: str,
        payload: dict,
        from_id: Optional[int] = None,
        to_id: Optional[int] = None,
    ):
        """
        Send a message through Redis pub/sub.

        - **Args**:
            - `channel` (str): Channel to which the message should be published.
            - `payload` (dict): Payload of the message to send.
            - `from_id` (Optional[int], optional): ID of the sender. Required for interception.
            - `to_id` (Optional[int], optional): ID of the recipient. Required for interception.

        - **Description**:
            - Serializes the payload to JSON, checks it against the message interceptor (if any),
              and publishes the message to the specified channel if valid.
            - Records message metadata in the log list.
        """
        start_time = time.time()
        log = {
            "channel": channel,
            "payload": payload,
            "from_id": from_id,
            "to_id": to_id,
            "start_time": start_time,
            "consumption": 0,
        }
        self._topics.add(channel)
        message = json.dumps(payload, default=str)
        interceptor = self.message_interceptor
        is_valid: bool = True
        if interceptor is not None and (from_id is not None and to_id is not None):
            is_valid = await interceptor.forward.remote(  # type:ignore
                from_id, to_id, message
            )
        if is_valid:
            await self.client.publish(channel, message)
            logger.info(f"Message sent to {channel}: {message}")
        else:
            logger.info(f"Message not sent to {channel}: {message} due to interceptor")
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)

    async def stop(self):
        """
        Stop the listener and disconnect from Redis.

        - **Description**:
            - Cancels the receive_messages_task if it exists and ensures the Redis connection is closed.
            - Gracefully handles any exceptions during the task cancellation.
        """
        if self.receive_messages_task:
            self.receive_messages_task.cancel()
            await asyncio.gather(self.receive_messages_task, return_exceptions=True)
        await self.disconnect()

    async def start_listening(self):
        """
        Start the task for listening to incoming messages from Redis.

        - **Description**:
            - Creates a new Redis pubsub connection and starts a task that listens for incoming messages.
            - Manages dynamic subscriptions to topics that are added over time.
            - Only starts the task if the connection to Redis is active.
        """
        if not await self.is_connected():
            logger.error("Cannot start listening because not connected to Redis.")
            return

        # Create a new pubsub connection
        pubsub = self.client.pubsub()

        # Create task to monitor messages
        self.receive_messages_task = asyncio.create_task(
            self._listen_for_messages(pubsub)
        )
        logger.info("Started message listening")

    async def _listen_for_messages(self, pubsub):
        """
        Internal method to continuously listen for messages and handle dynamic subscriptions.

        - **Args**:
            - `pubsub` (aioredis.client.PubSub): The Redis pubsub connection to use for subscribing and receiving messages.

        - **Description**:
            - Continuously checks for new topics to subscribe to.
            - Listens for incoming messages and places them in the message queue.
            - Handles cancellation and errors gracefully.
        """
        try:
            current_topics = set()
            while True:
                new_topics = self._topics - current_topics
                if new_topics:
                    await self._update_subscribe(pubsub, new_topics)
                    current_topics.update(new_topics)
                    logger.info(f"Subscribed to new topics: {new_topics}")
                if current_topics:
                    message = await pubsub.get_message(ignore_subscribe_messages=True)
                    if message and message["type"] in ("message", "pmessage"):
                        await self.message_queue.put(message)
                        logger.debug(f"Received message: {message}")
                await asyncio.sleep(0.1)

        except asyncio.CancelledError:
            await pubsub.unsubscribe()
            logger.info("Message listening stopped")
        except Exception as e:
            logger.error(f"Error in message listening: {e}")
            await pubsub.unsubscribe()
            raise

    @lock_decorator
    async def _update_subscribe(self, pubsub, new_topics):
        """
        Subscribe to new topics with the given pubsub connection.

        - **Args**:
            - `pubsub` (aioredis.client.PubSub): The Redis pubsub connection to use for subscribing.
            - `new_topics` (set[str]): Set of new topics to subscribe to.

        - **Description**:
            - Thread-safe method to subscribe the pubsub connection to the specified new topics.
        """
        await pubsub.subscribe(*new_topics)
