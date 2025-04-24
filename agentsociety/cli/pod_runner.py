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
from ..kubernetes import create_pod

logger = logging.getLogger("pod_runner")


async def run_experiment_in_pod(
    config_base64: Optional[str] = None,
    config_path: Optional[str] = None,
    callback_url: str = "",
    callback_auth_token: str = "",
    tenant_id: str = "",
) -> str:
    """
    Run experiment in Kubernetes Pod.

    Args:
        config_base64: Base64 encoded configuration
        config_path: Path to configuration file
        callback_url: Callback URL
        callback_auth_token: Callback auth token
        tenant_id: Tenant ID

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
        if file_ext == ".json":
            with open(config_path, "r", encoding="utf-8") as f:
                config_dict = json.load(f)
        elif file_ext in [".yaml", ".yml"]:
            with open(config_path, "r", encoding="utf-8") as f:
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

    exp_id = config_dict["exp"]["id"]
    # 生成唯一的 Pod 名称
    pod_name = (
        f"agentsociety-{exp_id}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    )

    # 如果没有提供 config_base64，则从 config_dict 生成
    if not config_base64 and config_dict:
        container_config_base64 = base64.b64encode(
            json.dumps(config_dict).encode()
        ).decode()
    else:
        container_config_base64 = config_base64
    assert container_config_base64 is not None

    await create_pod(
        pod_name,
        container_config_base64,
        tenant_id,
        exp_id,
        callback_url,
        callback_auth_token,
    )

    return pod_name


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

    # Add tenant_id argument
    parser.add_argument("--tenant-id", help="Tenant ID", default="default")
    parser.add_argument("--callback-url", help="Callback URL", default="")
    parser.add_argument("--callback-auth-token", help="Callback auth token", default="")

    # Parse command line arguments
    args = parser.parse_args()

    # Run experiment
    pod_name = asyncio.run(
        run_experiment_in_pod(
            config_base64=args.config_base64,
            config_path=args.config,
            callback_url=args.callback_url,
            callback_auth_token=args.callback_auth_token,
            tenant_id=args.tenant_id,
        )
    )

    print(f"Experiment started in pod: {pod_name}")
    sys.exit(0)


if __name__ == "__main__":
    main()
