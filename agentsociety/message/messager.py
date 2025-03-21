import asyncio
import logging
import os
import time
from typing import Any, List, Optional, Union

import jsonc
import ray
import redis.asyncio as aioredis
from redis.asyncio.client import PubSub

from ..logger import get_logger
from ..utils.decorators import lock_decorator

__all__ = [
    "Messager",
]


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
        db: Union[str, int] = "0",
        password: Optional[str] = None,
        timeout: float = 60,
        message_interceptor: Optional[ray.ObjectRef] = None,
    ):
        """
        Initialize the Messager with Redis connection parameters.

        - **Args**:
            - `hostname` (str): The hostname or IP address of the Redis server.
            - `port` (int, optional): Port number of the Redis server. Defaults to 6379.
            - `db` (str, int): Database number, defaults to 0.
            - `password` (str, optional): Password for Redis authentication.
            - `timeout` (int, optional): Connection timeout in seconds. Defaults to 60.
            - `message_interceptor` (Optional[ray.ObjectRef], optional): Reference to a message interceptor object.
        """
        get_logger().info(f"Connecting to Redis at {hostname}:{port}")
        self.client = aioredis.Redis(
            host=hostname,
            port=port,
            db=db,
            password=password,
            socket_timeout=timeout,
            socket_keepalive=True,
            health_check_interval=5,
            single_connection_client=True,
        )
        self.connected = False  # whether is messager connected
        self.message_queue = asyncio.Queue()  # store received messages
        self.receive_messages_task = None
        self._message_interceptor = message_interceptor
        self._log_list = []
        self._lock = asyncio.Lock()
        get_logger().info("Messager initialized")

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

    async def connect(self):
        """
        Attempt to connect to the Redis server up to three times.

        - **Description**:
            - Tries to establish a connection to Redis. Retries up to three times with delays between attempts.
            - Logs success or failure accordingly.
        """
        await self.client.__aenter__()
        self.connected = True
        get_logger().info("Connected to Redis")

    async def disconnect(self):
        """
        Disconnect from the Redis server.

        - **Description**:
            - Closes the connection to Redis and logs the disconnection.
        """
        await self.client.__aexit__(None, None, None)
        self.connected = False
        get_logger().info("Disconnected from Redis")

    def is_connected(self):
        """
        Check if the connection to Redis is established.

        - **Returns**:
            - `bool`: True if connected, otherwise False.
        """
        return self.connected

    @lock_decorator
    async def subscribe_and_start_listening(self, channels: List[str]):
        """
        Subscribe to one or more Redis channels.

        - **Args**:
            - `channels` (Union[str, list[str]]): Channel or list of channels to subscribe to.

        """
        if not self.is_connected():
            raise Exception(
                "Cannot subscribe to channels because not connected to Redis."
            )
        # Create a new pubsub connection
        pubsub = self.client.pubsub()

        # Create task to monitor messages
        self.receive_messages_task = asyncio.create_task(
            self._listen_for_messages(pubsub, channels)
        )
        get_logger().info("Started message listening")

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
        message = jsonc.dumps(payload, default=str)
        interceptor = self.message_interceptor
        is_valid: bool = True
        if interceptor is not None and (from_id is not None and to_id is not None):
            is_valid = await interceptor.forward.remote(  # type:ignore
                from_id, to_id, message
            )
        if is_valid:
            await self.client.publish(channel, message)
            get_logger().info(f"Message sent to {channel}: {message}")
        else:
            get_logger().info(
                f"Message not sent to {channel}: {message} due to interceptor"
            )
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

    async def _listen_for_messages(self, pubsub: PubSub, channels: List[str]):
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
            await pubsub.psubscribe(*channels)
            get_logger().info(
                f"Subscribed to new channels: len(channels)={len(channels)}"
            )
            while True:
                message = await pubsub.get_message(
                    ignore_subscribe_messages=True, timeout=1
                )
                if message and message["type"] in ("pmessage",):
                    await self.message_queue.put(message)
                    get_logger().debug(f"Received message: {message}")

        except asyncio.CancelledError:
            await pubsub.punsubscribe()
            await pubsub.aclose()
            get_logger().info("Message listening stopped")
        except Exception as e:
            get_logger().error(f"Error in message listening: {e}")
            await pubsub.unsubscribe()
            await pubsub.aclose()
            raise e
