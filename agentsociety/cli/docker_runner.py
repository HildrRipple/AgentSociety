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
    map_dir: str = "./maps",
    output_dir: str = "./output",
    log_level: str = "info"
) -> int:
    """Run experiment in Docker container."""
    try:
        # 确保目录存在
        os.makedirs(map_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(os.path.join(output_dir, "avro"), exist_ok=True)
        os.makedirs(os.path.join(output_dir, "logs"), exist_ok=True)
        
        # 初始化 Docker 客户端
        docker = aiodocker.Docker(url="unix:///var/run/docker.sock")

        # 如果提供了配置文件，读取并转换为 base64
        if sim_config_file and exp_config_file:
            with open(sim_config_file, 'r') as f:
                sim_config = json.load(f)
                # 更新地图文件路径为容器内路径
                if "map_config" in sim_config:
                    map_file = os.path.basename(sim_config["map_config"]["file_path"])
                    sim_config["map_config"]["file_path"] = f"/maps/{map_file}"
                # 更新输出路径
                if "avro" in sim_config:
                    sim_config["avro"]["path"] = "/output/avro"
                if "log_dir" in sim_config:
                    sim_config["log_dir"] = "/output/logs"
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
                "NetworkMode": "host",
                "Binds": [
                    f"{os.path.abspath(map_dir)}:/maps:ro",  # 只读挂载地图目录
                    f"{os.path.abspath(output_dir)}:/output:rw"  # 读写挂载输出目录
                ]
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
@click.option('--map-dir', default='./maps', help='Directory containing map files')
@click.option('--output-dir', default='./output', help='Directory for output files')
@click.option('--log-level', default='info', help='Logging level')
def experiment_runner(
    sim_config_file, 
    exp_config_file, 
    sim_config_base64, 
    exp_config_base64, 
    map_dir,
    output_dir,
    log_level
):
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
        map_dir=map_dir,
        output_dir=output_dir,
        log_level=log_level
    ))

    sys.exit(exit_code)

if __name__ == "__main__":
    experiment_runner() 