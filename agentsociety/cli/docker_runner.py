import argparse
import asyncio
import base64
import json
import logging
import os
import sys
from typing import Optional

import aiodocker  # 需要添加这个依赖


def setup_logging(log_level: str = "info"):
    """Configure logging with specified level."""
    log_level = log_level.upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    return logging.getLogger("experiment_runner")


async def run_experiment_in_container(
    sim_config_file: Optional[str] = None,
    exp_config_file: Optional[str] = None,
    sim_config_base64: Optional[str] = None,
    exp_config_base64: Optional[str] = None,
    log_level: str = "info"
):
    """Run an experiment in a Docker container."""
    logger = setup_logging(log_level)
    
    try:
        # 处理配置文件
        if sim_config_file and not sim_config_base64:
            with open(sim_config_file, 'r') as f:
                sim_config_dict = json.load(f)
                sim_config_base64 = base64.b64encode(json.dumps(sim_config_dict).encode()).decode()
        
        if exp_config_file and not exp_config_base64:
            with open(exp_config_file, 'r') as f:
                exp_config_dict = json.load(f)
                exp_config_base64 = base64.b64encode(json.dumps(exp_config_dict).encode()).decode()
        
        if not sim_config_base64 or not exp_config_base64:
            logger.error("Both simulator and experiment configurations are required")
            return 1
        
        # 创建Docker客户端
        docker = aiodocker.Docker()
        
        # 配置容器
        container_config = {
            "Image": "agentsociety-runner",
            "Cmd": [
                "--sim-config-base64", sim_config_base64,
                "--exp-config-base64", exp_config_base64,
                "--log-level", log_level
            ],
            "Entrypoint": ["/bin/bash", "-c"],
            "HostConfig": {
                "NetworkMode": "host",  # 使用主机网络访问Redis等服务
                "Binds": [
                    f"{os.path.abspath(os.path.dirname(__file__))}/../../webapi/docker/entrypoint.sh:/entrypoint.sh:ro"
                ]
            },
            "AttachStdout": True,
            "AttachStderr": True,
            "Tty": True
        }
        
        # 将 entrypoint.sh 设置为可执行
        os.chmod(f"{os.path.abspath(os.path.dirname(__file__))}/../../webapi/docker/entrypoint.sh", 0o755)
        
        # 修改命令为执行 entrypoint.sh
        container_config["Cmd"] = [
            "/entrypoint.sh",
            "--sim-config-base64", sim_config_base64,
            "--exp-config-base64", exp_config_base64,
            "--log-level", log_level
        ]
        
        # 创建并启动容器
        logger.info("Creating and starting Docker container...")
        container = await docker.containers.create(config=container_config)
        await container.start()
        
        # 获取容器ID
        container_info = await container.show()
        container_id = container_info["Id"]
        logger.info(f"Container started with ID: {container_id}")
        
        # 附加到容器日志
        logger.info("Attaching to container logs...")
        log_stream = await container.log(stdout=True, stderr=True, follow=True)
        async for log_line in log_stream:
            print(log_line, end="")
        
        # 等待容器完成
        logger.info("Waiting for container to complete...")
        wait_result = await container.wait()
        exit_code = wait_result["StatusCode"]
        
        # 清理容器
        logger.info("Cleaning up container...")
        await container.delete()
        await docker.close()
        
        if exit_code == 0:
            logger.info("Experiment completed successfully")
        else:
            logger.error(f"Experiment failed with exit code: {exit_code}")
        
        return exit_code
    
    except Exception as e:
        logger.error(f"Error running experiment in container: {str(e)}")
        return 1


def experiment_runner():
    """Command-line entry point for running experiments in Docker."""
    parser = argparse.ArgumentParser(description="AgentSociety Experiment Runner (Docker)")
    parser.add_argument("--sim-config-base64", help="Simulator configuration in base64 encoding")
    parser.add_argument("--exp-config-base64", help="Experiment configuration in base64 encoding")
    parser.add_argument("--sim-config-file", help="Path to simulator configuration file")
    parser.add_argument("--exp-config-file", help="Path to experiment configuration file")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"],
                        help="Set log level (default: info)")
    
    args = parser.parse_args()
    
    # 运行实验
    exit_code = asyncio.run(run_experiment_in_container(
        sim_config_file=args.sim_config_file,
        exp_config_file=args.exp_config_file,
        sim_config_base64=args.sim_config_base64,
        exp_config_base64=args.exp_config_base64,
        log_level=args.log_level
    ))
    
    sys.exit(exit_code)


if __name__ == "__main__":
    experiment_runner() 