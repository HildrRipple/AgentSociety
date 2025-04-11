import asyncio
import base64
import json
import logging
import os
import sys
import argparse
from pathlib import Path
from typing import Optional
import datetime
import functools
import yaml
from kubernetes import client, config as k8s_config

logger = logging.getLogger("pod_runner")


async def run_experiment_in_pod(
    config_base64: Optional[str] = None,
    config_path: Optional[str] = None,
) -> str:
    """
    Run experiment in Kubernetes Pod.
    
    Args:
        config_base64: Base64 encoded configuration
        config_path: Path to configuration file
        
    Returns:
        Pod name
    
    Raises:
        Exception: If pod creation fails
    """
    # Load configuration
    config_dict = None
    
    # Load configuration from file
    if config_path and not config_base64:
        if not os.path.exists(config_path):
            raise ValueError(f"Configuration file {config_path} does not exist")
            
        file_ext = Path(config_path).suffix.lower()
        if file_ext == '.json':
            with open(config_path, 'r', encoding='utf-8') as f:
                config_dict = json.load(f)
        elif file_ext in ['.yaml', '.yml']:
            with open(config_path, 'r', encoding='utf-8') as f:
                config_dict = yaml.safe_load(f)
        else:
            raise ValueError(f"Unsupported configuration file format: {file_ext}")
    
    # Load configuration from base64
    elif config_base64:
        try:
            config_dict = json.loads(base64.b64decode(config_base64).decode())
        except Exception as e:
            raise ValueError(f"Failed to decode base64 configuration: {e}")
    
    # Ensure configuration exists
    if not config_dict:
        raise ValueError("No configuration provided")
    
    # 加载 Kubernetes 配置
    try:
        k8s_config.load_kube_config(config_file="examples/k8s-fiblab-kubeconfig.yaml")
    except Exception as e:
        logger.error(f"Failed to load Kubernetes config: {e}")
        raise
    
    v1 = client.CoreV1Api()
    
    # 生成唯一的 Pod 名称
    pod_name = f"agentsociety-{datetime.datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # 如果没有提供 config_base64，则从 config_dict 生成
    if not config_base64 and config_dict:
        container_config_base64 = base64.b64encode(json.dumps(config_dict).encode()).decode()
    else:
        container_config_base64 = config_base64
    
    try:
        # 创建 Pod
        # 使用 Kubernetes 兼容的时间戳格式
        created_at = datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
        
        pod = client.V1Pod(
            metadata=client.V1ObjectMeta(
                name=pod_name,
                namespace="agentsociety",
                labels={
                    "app": "agentsociety",
                    "created_at": created_at,  # 使用兼容的格式
                    "description": config_dict.get("description", ""),
                }
            ),
            spec=client.V1PodSpec(
                containers=[
                    client.V1Container(
                        name="runner",
                        image="swr.cn-north-4.myhuaweicloud.com/tsinghua-fib-lab/agentsociety:latest",
                        command=[
                            "python",
                            "-m",
                            "agentsociety.cli.cli",
                            "run",
                            "--config-base64",
                            container_config_base64,
                        ]
                    )
                ],
                restart_policy="Never",
                host_network=True
            )
        )
        
        # 创建 Pod
        v1.create_namespaced_pod(namespace="agentsociety", body=pod)
        logger.info(f"Created pod: {pod_name}")
        
        return pod_name
    
    except Exception as e:
        logger.error(f"Error running experiment in pod: {str(e)}")
        # 打印详细错误信息
        import traceback
        logger.error(traceback.format_exc())
        raise


def handle_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error: {e}")
            sys.exit(1)
    return wrapper

@handle_errors
def main():
    """Run experiment in Kubernetes Pod."""
    # Create argument parser
    parser = argparse.ArgumentParser(description="Run experiment in Kubernetes Pod")
    
    # Create mutually exclusive group
    group = parser.add_mutually_exclusive_group(required=True)
    
    # Add command line arguments to the group
    group.add_argument("--config", help="Path to configuration file")
    group.add_argument("--config-base64", help="Base64 encoded configuration")
    
    # Parse command line arguments
    args = parser.parse_args()
    
    # Run experiment
    pod_name = asyncio.run(
        run_experiment_in_pod(
            config_base64=args.config_base64,
            config_path=args.config,
        )
    )
    
    print(f"Experiment started in pod: {pod_name}")
    sys.exit(0)


if __name__ == "__main__":
    main()
