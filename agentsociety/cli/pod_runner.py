import asyncio
import logging
import sys
import argparse
import functools
from ..executor import KubernetesExecutor

logger = logging.getLogger("pod_runner")


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
    executor = KubernetesExecutor([])
    pod_name = asyncio.run(
        executor.create(
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
