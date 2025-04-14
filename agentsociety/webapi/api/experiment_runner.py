import asyncio
import base64
import json
import logging
import uuid
from typing import Any, Dict, cast

from fastapi import APIRouter, Body, HTTPException, Request, status
from pydantic import BaseModel, ValidationError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from agentsociety.configs.env import EnvConfig

from ...cli.pod_runner import run_experiment_in_pod
from ...configs import Config
from ..models import ApiResponseWrapper
from ..models.config import AgentConfig, LLMConfig, MapConfig, WorkflowConfig
from .const import DEMO_USER_ID

__all__ = ["router"]

router = APIRouter(tags=["experiment_runner"])
logger = logging.getLogger(__name__)


class ConfigPrimaryKey(BaseModel):
    """Config primary key model"""

    tenant_id: str
    id: str


class ExperimentRequest(BaseModel):
    """Experiment request model"""

    llm: ConfigPrimaryKey
    agents: ConfigPrimaryKey
    map: ConfigPrimaryKey
    workflow: ConfigPrimaryKey
    exp_name: str


class ExperimentResponse(BaseModel):
    """Experiment response model"""

    id: str


@router.post("/run-experiments")
async def run_experiment(
    request: Request, config: ExperimentRequest = Body(...)
) -> ApiResponseWrapper[ExperimentResponse]:
    """Start a new experiment"""
    if request.app.state.read_only:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Server is in read-only mode",
        )
    tenant_id = await request.app.state.get_tenant_id(request)
    if tenant_id == DEMO_USER_ID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo user is not allowed to run experiments",
        )
    # if the tenant_id in config is not "" or tenant_id, 403
    if config.llm.tenant_id not in [tenant_id, ""]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    if config.agents.tenant_id not in [tenant_id, ""]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    if config.map.tenant_id not in [tenant_id, ""]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    if config.workflow.tenant_id not in [tenant_id, ""]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Permission denied",
        )
    # get config from db
    async with request.app.state.get_db() as db:
        db = cast(AsyncSession, db)
        stmt = select(LLMConfig.config).where(
            LLMConfig.tenant_id == config.llm.tenant_id,
            LLMConfig.id == config.llm.id,
        )
        llm_config = (await db.execute(stmt)).scalar_one_or_none()
        if llm_config is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="LLM config not found"
            )
        stmt = select(AgentConfig.config).where(
            AgentConfig.tenant_id == config.agents.tenant_id,
            AgentConfig.id == config.agents.id,
        )
        agent_config = (await db.execute(stmt)).scalar_one_or_none()
        if agent_config is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Agent config not found"
            )
        stmt = select(MapConfig.config).where(
            MapConfig.tenant_id == config.map.tenant_id,
            MapConfig.id == config.map.id,
        )
        map_config = (await db.execute(stmt)).scalar_one_or_none()
        if map_config is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Map config not found"
            )
        stmt = select(WorkflowConfig.config).where(
            WorkflowConfig.tenant_id == config.workflow.tenant_id,
            WorkflowConfig.id == config.workflow.id,
        )
        workflow_config = (await db.execute(stmt)).scalar_one_or_none()
        if workflow_config is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Workflow config not found",
            )
    # Generate unique experiment ID
    experiment_id = str(uuid.uuid4())
    c = {
        "llm": llm_config,
        "env": cast(EnvConfig, request.app.state.env).model_dump(),
        "map": map_config,
        "agents": agent_config,
        "exp": {
            "id": experiment_id,
            "name": config.exp_name,
            "workflow": workflow_config,
            "environment": {
                "start_tick": 28800,
            },
        },
    }
    logger.debug(f"Received experiment config: {json.dumps(c, indent=2)}")

    # Config model validate
    try:
        Config.model_validate(c)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )

    # Convert config to base64
    config_base64 = base64.b64encode(json.dumps(c).encode()).decode()

    # Start experiment container
    # Create an async task and get its result
    task = asyncio.create_task(
        run_experiment_in_pod(
            config_base64=config_base64,
            tenant_id=tenant_id,
        )
    )

    # Set up a callback function to handle task completion
    def container_started(future):
        try:
            container_id = future.result()
            logger.info(f"Container started with ID: {container_id}")
        except Exception as e:
            logger.error(f"Error starting container: {e}")

    # Add callback
    task.add_done_callback(container_started)

    logger.info("Successfully created experiment container task")

    return ApiResponseWrapper(
        data=ExperimentResponse(id=experiment_id),
    )
