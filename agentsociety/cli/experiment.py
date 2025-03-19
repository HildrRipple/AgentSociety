import argparse
import asyncio
import base64
import json
import logging
import os
import sys
from typing import Optional


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


async def run_experiment(
    sim_config_file: Optional[str] = None,
    exp_config_file: Optional[str] = None,
    sim_config_base64: Optional[str] = None,
    exp_config_base64: Optional[str] = None,
    log_level: str = "info"
):
    """Run an experiment with the provided configuration."""
    logger = setup_logging(log_level)
    
    try:
        from agentsociety.configs import ExpConfig, SimConfig
        from agentsociety.simulation import AgentSimulation
        
        # Process configuration files
        config_dir = "/config" if os.path.exists("/config") else os.path.join(os.getcwd(), "config")
        os.makedirs(config_dir, exist_ok=True)
        
        # Handle simulator configuration
        sim_config_path = os.path.join(config_dir, "sim_config.json")
        if sim_config_base64:
            logger.info("Using base64 encoded simulator configuration")
            with open(sim_config_path, 'w') as f:
                f.write(base64.b64decode(sim_config_base64).decode('utf-8'))
        elif sim_config_file:
            logger.info(f"Using simulator configuration from file: {sim_config_file}")
            with open(sim_config_file, 'r') as src, open(sim_config_path, 'w') as dst:
                dst.write(src.read())
        else:
            logger.error("No simulator configuration provided")
            return 1
        
        # Handle experiment configuration
        exp_config_path = os.path.join(config_dir, "exp_config.json")
        if exp_config_base64:
            logger.info("Using base64 encoded experiment configuration")
            with open(exp_config_path, 'w') as f:
                f.write(base64.b64decode(exp_config_base64).decode('utf-8'))
        elif exp_config_file:
            logger.info(f"Using experiment configuration from file: {exp_config_file}")
            with open(exp_config_file, 'r') as src, open(exp_config_path, 'w') as dst:
                dst.write(src.read())
        else:
            logger.error("No experiment configuration provided")
            return 1
        
        # Load configurations from files
        with open(sim_config_path, 'r') as f:
            sim_config_dict = json.load(f)
            sim_config = SimConfig.parse_obj(sim_config_dict)
        
        with open(exp_config_path, 'r') as f:
            exp_config_dict = json.load(f)
            exp_config = ExpConfig.parse_obj(exp_config_dict)
        
        logger.info(f"Starting experiment with config: {exp_config}")
        simulation = AgentSimulation.run_from_config(
            config=exp_config,
            sim_config=sim_config,
        )
        await simulation
        logger.info("Experiment completed successfully")
        return 0
    except Exception as e:
        logger.error(f"Error in experiment: {str(e)}")
        return 1


def experiment_runner():
    """Command-line entry point for running experiments."""
    parser = argparse.ArgumentParser(description="AgentSociety Experiment Runner")
    parser.add_argument("--sim-config-base64", help="Simulator configuration in base64 encoding")
    parser.add_argument("--exp-config-base64", help="Experiment configuration in base64 encoding")
    parser.add_argument("--sim-config-file", help="Path to simulator configuration file")
    parser.add_argument("--exp-config-file", help="Path to experiment configuration file")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"],
                        help="Set log level (default: info)")
    
    args = parser.parse_args()
    
    # Run the experiment
    exit_code = asyncio.run(run_experiment(
        sim_config_file=args.sim_config_file,
        exp_config_file=args.exp_config_file,
        sim_config_base64=args.sim_config_base64,
        exp_config_base64=args.exp_config_base64,
        log_level=args.log_level
    ))
    
    sys.exit(exit_code)


if __name__ == "__main__":
    experiment_runner() 