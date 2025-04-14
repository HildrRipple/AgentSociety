import os

from kubernetes_asyncio import config

from .pod import create_pod, delete_pod, get_pod_logs, get_pod_status

__all__ = [
    "load_kube_config",
    "create_pod",
    "delete_pod",
    "get_pod_logs",
    "get_pod_status",
]


async def load_kube_config(search_paths: list[str] = []):
    """
    加载 Kubernetes 配置，按照incluster, ~/.kube/config, 和 search_paths 的顺序搜索。

    Args:
        search_paths (list[str]): 搜索路径列表
    """
    try:
        config.load_incluster_config()
        return
    except config.ConfigException:
        pass

    try:
        await config.load_kube_config()
        return
    except config.ConfigException:
        pass

    for path in search_paths:
        if os.path.exists(path):
            await config.load_kube_config(path)
            return

    raise config.ConfigException("Failed to load Kubernetes config")
