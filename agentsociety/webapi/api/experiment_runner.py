import asyncio
import base64
import json
import logging
import os
import tempfile
import uuid
from pathlib import Path
from typing import Dict, Optional, List

import aiodocker
from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from ..models import ApiResponseWrapper

__all__ = ["router"]

router = APIRouter(tags=["experiment_runner"])
logger = logging.getLogger(__name__)

# Store running experiment container IDs
running_experiments: Dict[str, Dict] = {}
# Store temporary file paths
temp_files: Dict[str, List[str]] = {}
# Docker client
docker_client = None


# Initialize Docker client
async def get_docker_client():
    global docker_client
    if docker_client is None:
        docker_client = aiodocker.Docker()
    return docker_client


# Close Docker client
async def close_docker_client():
    global docker_client
    if docker_client is not None:
        await docker_client.close()
        docker_client = None


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
        # Get Docker client
        docker = await get_docker_client()

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

        # Configure container
        container_config = {
            "Image": "agentsociety-runner",
            "Cmd": [
                "--sim-config-base64", sim_config_base64,
                "--exp-config-base64", exp_config_base64,
                "--log-level", "info"
            ],
            "HostConfig": {
                "NetworkMode": "host"  # Use host network to access Redis and other services
            }
        }

        # Create and start container
        container = await docker.containers.create(
            config=container_config,
            name=f"experiment_{experiment_id}"
        )
        await container.start()

        # Get container ID
        container_info = await container.show()
        container_id = container_info["Id"]

        # Store experiment information
        running_experiments[experiment_id] = {
            "container_id": container_id,
            "name": config.name,
            "status": "running",
            "created_at": container_info["Created"]
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
