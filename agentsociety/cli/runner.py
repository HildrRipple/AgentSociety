import argparse
import asyncio
import base64
import json
import logging
import sys
from typing import Optional

from ..configs import ExpConfig, SimConfig
from ..simulation import AgentSimulation


def setup_logging(log_level: str = "info"):
    """Configure logging with specified level."""
    log_level = log_level.upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    return logging.getLogger("experiment_runner")


async def run_experiment(
    sim_config_file: Optional[str] = None,
    exp_config_file: Optional[str] = None,
    sim_config_base64: Optional[str] = None,
    exp_config_base64: Optional[str] = None,
    log_level: str = "info",
):
    """Run an experiment with the provided configuration."""
    logger = setup_logging(log_level)

    # 处理配置文件
    if sim_config_file and not sim_config_base64:
        with open(sim_config_file, "r") as f:
            sim_config_dict = json.load(f)
            sim_config_base64 = base64.b64encode(
                json.dumps(sim_config_dict).encode()
            ).decode()

    if exp_config_file and not exp_config_base64:
        with open(exp_config_file, "r") as f:
            exp_config_dict = json.load(f)
            exp_config_base64 = base64.b64encode(
                json.dumps(exp_config_dict).encode()
            ).decode()

    if not sim_config_base64 or not exp_config_base64:
        logger.error("Both simulator and experiment configurations are required")
        return 1

    # 解码配置
    sim_config_dict = json.loads(base64.b64decode(sim_config_base64).decode())
    exp_config_dict = json.loads(base64.b64decode(exp_config_base64).decode())

    # 验证配置
    sim_config = SimConfig.model_validate(sim_config_dict)
    exp_config = ExpConfig.model_validate(exp_config_dict)

    # 运行实验
    logger.info(f"Starting experiment with config: {exp_config}")
    simulation = AgentSimulation.run_from_config(
        config=exp_config,
        sim_config=sim_config,
    )
    await simulation
    logger.info("Experiment completed successfully")


def main():
    """Command-line entry point for running experiments."""
    parser = argparse.ArgumentParser(description="AgentSociety Experiment Runner")
    parser.add_argument(
        "--sim-config-base64", help="Simulator configuration in base64 encoding"
    )
    parser.add_argument(
        "--exp-config-base64", help="Experiment configuration in base64 encoding"
    )
    parser.add_argument(
        "--sim-config-file", help="Path to simulator configuration file"
    )
    parser.add_argument(
        "--exp-config-file", help="Path to experiment configuration file"
    )
    parser.add_argument(
        "--log-level",
        default="info",
        choices=["debug", "info", "warning", "error"],
        help="Set log level (default: info)",
    )

    args = parser.parse_args()

    # 运行实验
    exit_code = asyncio.run(
        run_experiment(
            sim_config_base64=args.sim_config_base64,
            exp_config_base64=args.exp_config_base64,
            sim_config_file=args.sim_config_file,
            exp_config_file=args.exp_config_file,
            log_level=args.log_level,
        )
    )

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
