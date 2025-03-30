import asyncio
import base64
import json
import sys
import yaml
from pathlib import Path
import os
from typing import Optional
import argparse

from agentsociety import AgentSociety
from agentsociety.cityagent import default
from agentsociety.configs import Config


async def run_from_config(
    config_file: Optional[str] = None,
    config_base64: Optional[str] = None,
):
    """
    Run an experiment with the provided configuration.
    
    Args:
        config_file: Path to configuration file (JSON or YAML)
        config_base64: Base64 encoded configuration string
        
    Raises:
        ValueError: If configuration is invalid or missing
        Exception: If simulation fails
    """
    # Load configuration
    config_dict = None
    
    # Load from file if provided
    if config_file:
        if os.path.exists(config_file):
            print(f"Loading configuration from {config_file}...")
            file_ext = Path(config_file).suffix.lower()
            if file_ext == '.json':
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_dict = json.load(f)
            elif file_ext in ['.yaml', '.yml']:
                with open(config_file, 'r', encoding='utf-8') as f:
                    config_dict = yaml.safe_load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {file_ext}")
        else:
            raise ValueError(f"Configuration file {config_file} does not exist")
    
    # Load from base64 if provided
    elif config_base64:
        try:
            config_dict = json.loads(base64.b64decode(config_base64).decode())
        except Exception as e:
            raise ValueError(f"Failed to decode base64 configuration: {e}")
    
    # Ensure we have a configuration
    if not config_dict:
        raise ValueError("No configuration provided")
    
    # Validate and initialize configuration
    config = Config.model_validate(config_dict)
    # Apply default values if needed (similar to test.py)
    config = default(config)
    print("Configuration validated successfully")
    
    # Run the simulation
    print("Initializing AgentSociety...")
    society = AgentSociety(config)
    await society.init()
    await society.run()
    print("Simulation completed successfully")
    await society.close()
    print("AgentSociety closed successfully")


def main():
    """Command-line entry point for running experiments."""
    
    parser = argparse.ArgumentParser(description="AgentSociety Experiment Runner")
    parser.add_argument(
        "--config", type=str, default='config.json', help="Path to configuration file"
    )
    parser.add_argument(
        "--config-base64", help="Configuration in base64 encoding"
    )

    args = parser.parse_args()

    try:
        # Run experiment
        if args.config_base64:
            asyncio.run(run_from_config(config_base64=args.config_base64))
        else:
            asyncio.run(run_from_config(config_file=args.config))
        sys.exit(0)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
