import asyncio
from datetime import datetime, timedelta

from fastapi import HTTPException, status
from kubernetes_asyncio import client
from kubernetes_asyncio.client.api_client import ApiClient

from ..logger import get_logger

__all__ = ["create_pod", "delete_pod", "get_pod_logs", "get_pod_status"]


async def create_pod(
    pod_name: str,
    config_base64: str,
    tenant_id: str,
    exp_id: str,
    callback_url: str,
    callback_auth_token: str,
):
    async with ApiClient() as api:
        v1 = client.CoreV1Api(api)

        # 创建 Pod
        pod = client.V1Pod(
            metadata=client.V1ObjectMeta(
                name=pod_name,
                namespace="agentsociety",
                labels={
                    "app": "agentsociety",
                    # for filter when get pod logs or delete pod
                    "agentsociety.fiblab.net/tenant-id": tenant_id,
                    "agentsociety.fiblab.net/exp-id": exp_id,
                    "virtual-kubelet.io/burst-to-cci": "enforce",  # 将 Pod 调度到 CCI
                },
            ),
            spec=client.V1PodSpec(
                containers=[
                    client.V1Container(
                        name="runner",
                        image="swr.cn-north-4.myhuaweicloud.com/tsinghua-fib-lab/agentsociety:commercial",
                        command=[
                            "python",
                            "-m",
                            "agentsociety.cli.cli",
                            "run",
                            "--config-base64",
                            config_base64,
                            "--tenant-id",
                            tenant_id,
                        ],
                        # 添加资源请求和限制
                        resources=client.V1ResourceRequirements(
                            requests={
                                "cpu": "8",
                                "memory": "32Gi",
                            },
                            limits={
                                "cpu": "8",
                                "memory": "32Gi",
                            },
                        ),
                        # 添加生命周期回调（通过POST传输exp_id和callback_auth_token）
                        lifecycle=client.V1Lifecycle(
                            pre_stop=client.V1LifecycleHandler(
                                client.V1ExecAction(
                                    command=[
                                        "/bin/sh",
                                        "-c",
                                        f"curl -X POST {callback_url}/api/run-experiments/{exp_id}/finish?callback_auth_token={callback_auth_token}",
                                    ],
                                )
                            )
                        ),
                    )
                ],
                restart_policy="Never",
                host_network=False,
            ),
        )

        # 创建 Pod
        await v1.create_namespaced_pod(namespace="agentsociety", body=pod)  # type: ignore
        get_logger().info(f"Created pod: {pod_name}")


async def delete_pod(tenant_id: str, exp_id: str) -> None:
    """Delete experiment pod in kubernetes using labels and wait until it's gone

    Args:
        exp_id: Experiment ID
        tenant_id: Tenant ID

    Raises:
        HTTPException: If pod not found or deletion timeout
    """
    async with ApiClient() as api:
        v1 = client.CoreV1Api(api)
        namespace = "agentsociety"

        label_selector = (
            f"agentsociety.fiblab.net/tenant-id={tenant_id},"
            f"agentsociety.fiblab.net/exp-id={exp_id}"
        )

        # 先获取符合条件的pod列表
        pods = await v1.list_namespaced_pod(
            namespace=namespace, label_selector=label_selector
        )

        if not pods.items or len(pods.items) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Experiment is not running",
            )

        # 删除找到的pod
        for pod in pods.items:
            await v1.delete_namespaced_pod(
                name=pod.metadata.name,
                namespace=namespace,
                body=client.V1DeleteOptions(
                    propagation_policy="Foreground", grace_period_seconds=5
                ),
            )

        # 等待pod被完全删除
        timeout = datetime.now() + timedelta(minutes=2)  # 2分钟超时
        while datetime.now() < timeout:
            try:
                pods = await v1.list_namespaced_pod(
                    namespace=namespace, label_selector=label_selector
                )
                if not pods.items:
                    return  # Pod已经被完全删除
                await asyncio.sleep(1)  # 每1秒检查一次
            except Exception as e:
                get_logger().error(f"Error checking pod status: {e}")

        # 如果超时还没删除完成
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Timeout waiting for pod deletion",
        )


async def get_pod_logs(exp_id: str, tenant_id: str) -> str:
    """Get experiment pod logs from kubernetes using labels

    Args:
        exp_id: Experiment ID
        tenant_id: Tenant ID

    Returns:
        str: Pod logs

    Raises:
        Exception: If failed to get pod logs
    """
    async with ApiClient() as api:
        v1 = client.CoreV1Api(api)
        namespace = "agentsociety"  # 修正为正确的namespace

        # 使用label selector过滤pod
        label_selector = (
            f"agentsociety.fiblab.net/tenant-id={tenant_id},"
            f"agentsociety.fiblab.net/exp-id={exp_id}"
        )

        # 先获取符合条件的pod列表
        pods = await v1.list_namespaced_pod(
            namespace=namespace, label_selector=label_selector
        )

        if not pods.items or len(pods.items) == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Experiment is not running",
            )

        # 获取第一个pod的日志（通常只会有一个pod）
        logs = await v1.read_namespaced_pod_log(
            name=pods.items[0].metadata.name,
            namespace=namespace,
            tail_lines=1000,
        )
        return logs


async def get_pod_status(exp_id: str, tenant_id: str) -> str:
    """Get experiment pod status from kubernetes using labels

    Args:
        exp_id: Experiment ID
        tenant_id: Tenant ID

    Returns:
        str: Pod status

    Raises:
        Exception: If failed to get pod status
    """
    async with ApiClient() as api:
        v1 = client.CoreV1Api(api)
        namespace = "agentsociety"

        label_selector = (
            f"agentsociety.fiblab.net/tenant-id={tenant_id},"
            f"agentsociety.fiblab.net/exp-id={exp_id}"
        )

        pods = await v1.list_namespaced_pod(
            namespace=namespace, label_selector=label_selector
        )

        if not pods.items or len(pods.items) == 0:
            return "NotRunning"

        return pods.items[0].status.phase
