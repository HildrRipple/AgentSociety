import asyncio
import base64
import json
import logging
import os
import sys
from pathlib import Path
from typing import Optional

import aiodocker
import click

logger = logging.getLogger("experiment_runner")

async def run_experiment_in_container(
    sim_config_base64: Optional[str] = None,
    exp_config_base64: Optional[str] = None,
    sim_config_file: Optional[str] = None,
    exp_config_file: Optional[str] = None,
    log_level: str = "info"
) -> int:
    """Run experiment in Docker container."""
    try:
        # 初始化 Docker 客户端
        docker = aiodocker.Docker(url="unix:///var/run/docker.sock")

        # 如果提供了配置文件，读取并转换为 base64
        if sim_config_file and exp_config_file:
            with open(sim_config_file, 'r') as f:
                sim_config = json.load(f)
                sim_config_base64 = base64.b64encode(json.dumps(sim_config).encode()).decode()
            
            with open(exp_config_file, 'r') as f:
                exp_config = json.load(f)
                exp_config_base64 = base64.b64encode(json.dumps(exp_config).encode()).decode()

        # 配置容器
        container_config = {
            "Image": "agentsociety-runner:latest",
            "Cmd": [
                "python", "-m", "agentsociety.cli.runner",
                "--sim-config-base64", sim_config_base64,
                "--exp-config-base64", exp_config_base64,
                "--log-level", log_level
            ],
            "HostConfig": {
                "NetworkMode": "host"
            }
        }

        # 创建并启动容器
        container = await docker.containers.create(config=container_config)
        await container.start()

        # 等待容器完成
        exit_data = await container.wait()
        exit_code = exit_data.get("StatusCode", 1)

        # 获取容器日志
        logs = await container.log(stdout=True, stderr=True)
        for line in logs:
            logger.info(line.strip())

        # 清理容器
        await container.delete()
        await docker.close()

        return exit_code

    except Exception as e:
        logger.error(f"Error running experiment in container: {str(e)}")
        if 'docker' in locals():
            await docker.close()
        return 1

@click.command()
@click.option('--sim-config-file', help='Path to simulator configuration file')
@click.option('--exp-config-file', help='Path to experiment configuration file')
@click.option('--sim-config-base64', help='Base64 encoded simulator configuration')
@click.option('--exp-config-base64', help='Base64 encoded experiment configuration')
@click.option('--log-level', default='info', help='Logging level')
def experiment_runner(sim_config_file, exp_config_file, sim_config_base64, exp_config_base64, log_level):
    """Run experiment in Docker container."""
    # 配置日志
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 运行实验
    exit_code = asyncio.run(run_experiment_in_container(
        sim_config_base64=sim_config_base64,
        exp_config_base64=exp_config_base64,
        sim_config_file=sim_config_file,
        exp_config_file=exp_config_file,
        log_level=log_level
    ))

    sys.exit(exit_code)

if __name__ == "__main__":
    experiment_runner() 