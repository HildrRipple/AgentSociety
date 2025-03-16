import asyncio
import base64
import json
import logging
import os
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Optional, List

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from ..models import ApiResponseWrapper

__all__ = ["router"]

router = APIRouter(tags=["experiment_runner"])
logger = logging.getLogger(__name__)

# 存储正在运行的实验容器ID
running_experiments: Dict[str, str] = {}
# 存储临时文件路径
temp_files: Dict[str, List[str]] = {}


class ExperimentConfig(BaseModel):
    """实验配置模型"""

    environment: Dict
    agent: Dict
    workflow: Dict
    map: Dict
    name: str


class ExperimentResponse(BaseModel):
    """实验响应模型"""

    id: str
    name: str
    status: str


@router.post("/run-experiment", status_code=status.HTTP_200_OK)
async def run_experiment(
    request: Request,
    config: ExperimentConfig,
) -> ApiResponseWrapper[ExperimentResponse]:
    """启动一个新的实验"""

    if request.app.state.read_only:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Server is in read-only mode"
        )

    # 生成唯一的实验ID
    experiment_id = str(uuid.uuid4())

    try:
        # 将配置转换为 base64
        sim_config_base64 = base64.b64encode(
            json.dumps(config.environment).encode()
        ).decode()

        # 合并 agent, workflow 和 map 配置
        exp_config = {
            **config.workflow,
            "agent_config": config.agent,
            "map_config": config.map,
        }
        exp_config_base64 = base64.b64encode(json.dumps(exp_config).encode()).decode()

        # 启动 Docker 容器
        cmd = [
            "docker",
            "run",
            "--detach",  # 后台运行
            "--name",
            f"experiment_{experiment_id}",
            "--network",
            "host",  # 使用主机网络，以便访问 Redis 等服务
            "agentsociety-runner",
            "--sim-config-base64",
            sim_config_base64,
            "--exp-config-base64",
            exp_config_base64,
            "--log-level",
            "info",
        ]

        # 执行命令启动容器
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            error_msg = stderr.decode().strip()
            logger.error(f"Failed to start Docker container: {error_msg}")
            raise Exception(f"Failed to start Docker container: {error_msg}")

        # 获取容器ID
        container_id = stdout.decode().strip()

        # 存储容器ID
        running_experiments[experiment_id] = container_id

        # 启动异步任务来监控容器
        asyncio.create_task(monitor_experiment_container(experiment_id))

        return ApiResponseWrapper(
            data=ExperimentResponse(
                id=experiment_id, name=config.name, status="running"
            )
        )

    except Exception as e:
        logger.error(f"Failed to start experiment: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start experiment: {str(e)}",
        )


@router.get("/experiments/{experiment_id}/status")
async def get_experiment_status(
    request: Request,
    experiment_id: str,
) -> ApiResponseWrapper[Dict]:
    """获取实验状态"""

    if experiment_id not in running_experiments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found"
        )

    container_id = running_experiments[experiment_id]

    # 检查容器是否仍在运行
    cmd = ["docker", "inspect", "--format={{.State.Status}}", container_id]

    try:
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            # 容器可能已经被移除
            status_info = "unknown"
            returncode = None
        else:
            container_status = stdout.decode().strip()

            if container_status == "running":
                status_info = "running"
                returncode = None
            elif container_status == "exited":
                # 获取退出码
                exit_code_cmd = [
                    "docker",
                    "inspect",
                    "--format={{.State.ExitCode}}",
                    container_id,
                ]
                exit_code_process = await asyncio.create_subprocess_exec(
                    *exit_code_cmd,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                )

                exit_code_stdout, _ = await exit_code_process.communicate()
                exit_code = int(exit_code_stdout.decode().strip())

                status_info = "completed" if exit_code == 0 else "failed"
                returncode = exit_code
            else:
                status_info = container_status
                returncode = None
    except Exception as e:
        logger.error(f"Error checking container status: {str(e)}")
        status_info = "unknown"
        returncode = None

    return ApiResponseWrapper(
        data={"id": experiment_id, "status": status_info, "returncode": returncode}
    )


@router.delete("/experiments/{experiment_id}/stop", status_code=status.HTTP_200_OK)
async def stop_experiment(
    request: Request,
    experiment_id: str,
) -> ApiResponseWrapper[Dict]:
    """停止实验"""

    if request.app.state.read_only:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Server is in read-only mode"
        )

    if experiment_id not in running_experiments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found"
        )

    container_id = running_experiments[experiment_id]

    # 停止并移除容器
    try:
        # 先尝试优雅停止
        stop_cmd = ["docker", "stop", container_id]
        stop_process = await asyncio.create_subprocess_exec(
            *stop_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        await stop_process.communicate()

        # 然后移除容器
        rm_cmd = ["docker", "rm", container_id]
        rm_process = await asyncio.create_subprocess_exec(
            *rm_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        await rm_process.communicate()
    except Exception as e:
        logger.error(f"Error stopping container: {str(e)}")

    # 从字典中移除容器ID
    del running_experiments[experiment_id]

    return ApiResponseWrapper(data={"id": experiment_id, "status": "stopped"})


async def monitor_experiment_container(experiment_id: str):
    """监控实验容器的日志输出"""

    if experiment_id not in running_experiments:
        logger.error(f"No container found for experiment {experiment_id}")
        return

    container_id = running_experiments[experiment_id]

    try:
        # 启动日志监控进程
        cmd = ["docker", "logs", "-f", container_id]

        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        # 异步读取标准输出
        async def read_stdout():
            while True:
                line = await process.stdout.readline()
                if not line:
                    break
                logger.info(f"Experiment {experiment_id}: {line.decode().strip()}")

        # 异步读取标准错误
        async def read_stderr():
            while True:
                line = await process.stderr.readline()
                if not line:
                    break
                logger.error(f"Experiment {experiment_id}: {line.decode().strip()}")

        # 创建两个任务来读取输出
        stdout_task = asyncio.create_task(read_stdout())
        stderr_task = asyncio.create_task(read_stderr())

        # 等待进程结束
        await process.wait()

        # 等待读取任务完成
        await stdout_task
        await stderr_task

        # 检查容器状态
        status_cmd = ["docker", "inspect", "--format={{.State.ExitCode}}", container_id]
        status_process = await asyncio.create_subprocess_exec(
            *status_cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, _ = await status_process.communicate()

        if status_process.returncode == 0:
            exit_code = int(stdout.decode().strip())
            if exit_code == 0:
                logger.info(f"Experiment {experiment_id} completed successfully")
            else:
                logger.error(
                    f"Experiment {experiment_id} failed with exit code {exit_code}"
                )

    except Exception as e:
        logger.error(f"Error monitoring container: {str(e)}")
