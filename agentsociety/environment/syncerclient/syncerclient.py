import logging
import ray

from pycityproto.city.sync.v2 import sync_service_pb2 as sync_service
from pycityproto.city.sync.v2 import sync_service_pb2_grpc as sync_grpc

from ..utils.grpc import create_channel

__all__ = ["SyncerClient"]


@ray.remote
class SyncerClient:
    """
    Sidecar框架服务（仅支持作为客户端，不支持对外提供gRPC服务）
    Sidecar framework service (only supported as a client, does not support external gRPC services)
    """

    def __init__(
        self, syncer_address: str, name: str = "within-syncer", secure: bool = False
    ):
        """
        Args:
        - name (str): 本服务在etcd上的注册名。The registered name of this service on etcd.
        - server_address (str): syncer地址。syncer address.
        - listen_address (str): sidecar监听地址。sidecar listening address.
        - secure (bool, optional): 是否使用安全连接. Defaults to False. Whether to use a secure connection. Defaults to False.
        """
        self._name = name
        channel = create_channel(syncer_address, secure)
        self._sync_stub = sync_grpc.SyncServiceStub(channel)

    def step(self, close: bool = False) -> bool:
        """
        同步器步进
        synchronizer step up

        Args:
        - close (bool): 是否退出模拟。Whether the simulation exited.

        Returns:
        - close (bool): 是否退出模拟。Whether the simulation exited.
        """
        self._sync_stub.EnterStepSync(
            sync_service.EnterStepSyncRequest(name=self._name)
        )
        response = self._sync_stub.ExitStepSync(
            sync_service.ExitStepSyncRequest(name=self._name, close=close)
        )
        return response.close

    def init(self) -> bool:
        """
        同步器初始化
        Synchronizer initialization

        Returns:
        - close (bool): 是否退出模拟。Whether the simulation exited.

        Examples:
        ```python
        close = client.init()
        print(close)
        # > False
        ```
        """
        return self.step()

    def close(self) -> bool:
        """
        同步器关闭
        Synchronizer close

        Returns:
        - close (bool): 是否退出模拟。Whether the simulation exited.
        """
        return self.step(True)

    def notify_step_ready(self):
        """
        通知prepare阶段已完成
        Notify that the prepare phase is completed
        """
        ...
