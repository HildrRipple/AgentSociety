import asyncio
import base64
import json
import logging
import os
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Optional, List
from datetime import datetime

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from ..models import ApiResponseWrapper
from ...cli.docker_runner import run_experiment_in_container

__all__ = ["router"]

router = APIRouter(tags=["experiment_runner"])
logger = logging.getLogger(__name__)

# Store running experiment container IDs
running_experiments: Dict[str, Dict] = {}


class ExperimentConfig(BaseModel):
    """Experiment configuration model"""
    environment: Dict
    agent: Dict
    workflow: Dict
    map: Dict
    name: str


class ExperimentResponse(BaseModel):
    """Experiment response model"""
    id: str
    name: str
    status: str


@router.post("/run-experiments", status_code=status.HTTP_200_OK)
async def run_experiment(
    request: Request,
    config: ExperimentConfig,
) -> ApiResponseWrapper[ExperimentResponse]:
    """Start a new experiment"""

    if request.app.state.read_only:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Server is in read-only mode"
        )

    # Generate unique experiment ID
    experiment_id = str(uuid.uuid4())

    try:
        # Convert configuration to base64
        sim_config_base64 = base64.b64encode(
            json.dumps(config.environment).encode()
        ).decode()

        # Merge agent, workflow and map configurations
        exp_config = {
            **config.workflow,
            "agent_config": config.agent,
            "map_config": config.map,
        }
        exp_config_base64 = base64.b64encode(json.dumps(exp_config).encode()).decode()

        # 使用 docker_runner 启动容器
        asyncio.create_task(run_experiment_in_container(
            sim_config_base64=sim_config_base64,
            exp_config_base64=exp_config_base64,
            log_level="info"
        ))

        # Store experiment information
        running_experiments[experiment_id] = {
            "name": config.name,
            "status": "running",
            "created_at": datetime.now().isoformat()
        }

        # Asynchronously update container status
        asyncio.create_task(update_experiment_status(experiment_id))

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


@router.get("/run-experiments")
async def get_experiments(
    request: Request,
) -> ApiResponseWrapper[List[Dict]]:
    """Get all experiments"""
    
    experiments = []
    
    for exp_id, exp_info in running_experiments.items():
        # Ensure status is up-to-date
        try:
            await update_experiment_status(exp_id)
        except Exception as e:
            logger.error(f"Error updating experiment status: {str(e)}")
        
        # Add to result list
        experiments.append({
            "id": exp_id,
            "name": exp_info.get("name", "Unknown"),
            "status": exp_info.get("status", "unknown"),
            "created_at": exp_info.get("created_at", "")
        })
    
    return ApiResponseWrapper(data=experiments)


@router.get("/experiments/{experiment_id}/status")
async def get_experiment_status(
    request: Request,
    experiment_id: str,
) -> ApiResponseWrapper[Dict]:
    """Get experiment status"""

    if experiment_id not in running_experiments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found"
        )

    # Update experiment status
    await update_experiment_status(experiment_id)
    
    exp_info = running_experiments[experiment_id]
    
    return ApiResponseWrapper(
        data={
            "id": experiment_id, 
            "status": exp_info.get("status", "unknown"), 
            "returncode": exp_info.get("returncode")
        }
    )


@router.delete("/experiments/{experiment_id}/stop", status_code=status.HTTP_200_OK)
async def stop_experiment(
    request: Request,
    experiment_id: str,
) -> ApiResponseWrapper[Dict]:
    """Stop an experiment"""

    if request.app.state.read_only:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Server is in read-only mode"
        )

    if experiment_id not in running_experiments:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Experiment not found"
        )

    container_id = running_experiments[experiment_id]["container_id"]

    try:
        # Get Docker client
        docker = await get_docker_client()

        # Get container
        container = docker.containers.container(container_id)

        # Stop container
        await container.stop()

        # Delete container
        await container.delete()

        # Update experiment status
        running_experiments[experiment_id]["status"] = "stopped"

    except aiodocker.exceptions.DockerError as e:
        if e.status == 404:
            # Container already doesn't exist, update status
            running_experiments[experiment_id]["status"] = "unknown"
        else:
            logger.error(f"Error stopping container: {str(e)}")
    except Exception as e:
        logger.error(f"Error stopping container: {str(e)}")

    return ApiResponseWrapper(
        data={
            "id": experiment_id, 
            "status": running_experiments[experiment_id]["status"]
        }
    )


async def update_experiment_status(experiment_id: str):
    """Update experiment status"""
    
    if experiment_id not in running_experiments:
        logger.error(f"No experiment found with ID {experiment_id}")
        return
    
    exp_info = running_experiments[experiment_id]
    container_id = exp_info["container_id"]
    
    try:
        # Get Docker client
        docker = await get_docker_client()

        # Get container
        container = docker.containers.container(container_id)

        # Get container information
        container_info = await container.show()
        container_state = container_info["State"]

        if container_state["Running"]:
            exp_info["status"] = "running"
            exp_info["returncode"] = None
        elif container_state["Status"] == "exited":
            exit_code = container_state["ExitCode"]
            exp_info["status"] = "completed" if exit_code == 0 else "failed"
            exp_info["returncode"] = exit_code
        else:
            exp_info["status"] = container_state["Status"]
            exp_info["returncode"] = None

    except aiodocker.exceptions.DockerError as e:
        if e.status == 404:
            # Container doesn't exist
            exp_info["status"] = "unknown"
            exp_info["returncode"] = None
        else:
            logger.error(f"Error checking container status: {str(e)}")
            exp_info["status"] = "error"
            exp_info["returncode"] = None
    except Exception as e:
        logger.error(f"Error checking container status: {str(e)}")
        exp_info["status"] = "unknown"
        exp_info["returncode"] = None


# Initialize Docker client on application startup
@router.on_event("startup")
async def startup_event():
    await get_docker_client()


# Close Docker client on application shutdown
@router.on_event("shutdown")
async def shutdown_event():
    await close_docker_client()


# 添加命令行入口点
async def run_experiment(
    sim_config_base64: Optional[str] = None,
    exp_config_base64: Optional[str] = None,
    log_level: str = "info"
):
    """Run an experiment with the provided configuration."""
    # 设置日志
    log_level = log_level.upper()
    logging.basicConfig(
        level=getattr(logging, log_level),
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    logger = logging.getLogger("experiment_executor")
    
    try:
        # 导入必要的模块
        from agentsociety.configs import ExpConfig, SimConfig
        from agentsociety.simulation import AgentSimulation
        
        # 解码配置
        if not sim_config_base64 or not exp_config_base64:
            logger.error("Both simulator and experiment configurations are required")
            return 1
        
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
        return 0
    except Exception as e:
        logger.error(f"Error in experiment: {str(e)}")
        return 1


def main():
    """Command-line entry point for running experiments directly."""
    parser = argparse.ArgumentParser(description="AgentSociety Experiment Executor")
    parser.add_argument("--sim-config-base64", required=True, help="Simulator configuration in base64 encoding")
    parser.add_argument("--exp-config-base64", required=True, help="Experiment configuration in base64 encoding")
    parser.add_argument("--log-level", default="info", choices=["debug", "info", "warning", "error"],
                        help="Set log level (default: info)")
    
    args = parser.parse_args()
    
    # 运行实验
    exit_code = asyncio.run(run_experiment(
        sim_config_base64=args.sim_config_base64,
        exp_config_base64=args.exp_config_base64,
        log_level=args.log_level
    ))
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
