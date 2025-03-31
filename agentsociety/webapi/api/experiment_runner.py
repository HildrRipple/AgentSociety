import asyncio
import base64
import json
import logging
import os
import uuid
from typing import Dict, Any

from fastapi import APIRouter, HTTPException, Request, status
from pydantic import BaseModel

from ...cli.docker_runner import run_experiment_in_container
from ..models import ApiResponseWrapper

__all__ = ["router"]

router = APIRouter(tags=["experiment_runner"])
logger = logging.getLogger(__name__)


class ExperimentResponse(BaseModel):
    """Experiment response model"""
    id: str
    name: str
    status: str


@router.post("/run-experiments", status_code=status.HTTP_200_OK)
async def run_experiment(
    request: Request,
    config: Dict[str, Any]
) -> ApiResponseWrapper[ExperimentResponse]:
    """Start a new experiment"""

    if request.app.state.read_only:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Server is in read-only mode"
        )

    # Generate unique experiment ID
    experiment_id = str(uuid.uuid4())
    
    env = request.app.state.env
    config["env"] = env
    
    # Convert config to base64
    config_base64 = base64.b64encode(json.dumps(config).encode()).decode()
    
    # Start experiment container
    asyncio.create_task(run_experiment_in_container(
        config_base64=config_base64,
    ))

    return ApiResponseWrapper(
        data=ExperimentResponse(
            id=experiment_id,
            name=config.get("exp", {}).get("name", "Default Experiment"),
            status="running",
        )
    )