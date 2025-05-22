import csv
import io
import json
import uuid
import os
import numpy as np
from typing import Any, Dict, List, Optional, cast

from fastapi import (
    APIRouter,
    Body,
    File,
    Form,
    HTTPException,
    Query,
    Request,
    UploadFile,
    status,
)
from pydantic import BaseModel, Field
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ...agent.distribution import (
    ChoiceDistribution,
    ConstantDistribution,
    NormalDistribution,
    UniformFloatDistribution,
    UniformIntDistribution,
)
from ...configs import EnvConfig
from ...s3 import S3Client
from ..models import ApiResponseWrapper
from ..models.agent_profiles import (
    AgentProfileData,
    ApiMemoryDistribution,
)
from .const import DEMO_USER_ID

__all__ = ["router"]

router = APIRouter(tags=["agent_profiles"])


class Distribution(BaseModel):
    """Distribution model for generating agent attributes"""

    type: str
    params: Dict[str, Any]


class MemoryDistribution(BaseModel):
    """Memory distribution model for agent attributes"""

    name: str
    distribution: Distribution


class PreviewRequest(BaseModel):
    """Request model for preview generation"""

    agent_type: str = Field(..., description="Type of agent (citizen, firm, etc.)")
    number: int = Field(..., description="Number of agents to generate")
    memory_distributions: List[ApiMemoryDistribution] = Field(
        default=[], description="List of attribute distributions"
    )


class EditProfileRequest(BaseModel):
    """Request model for editing agent profiles"""

    file_path: str = Field(..., description="Path to the profile file in S3")
    agents: List[Dict[str, Any]] = Field(..., description="Updated agent profiles")


class SaveProfileRequest(BaseModel):
    """Request model for saving agent profiles"""

    name: str = Field(..., description="Name for the saved profile")
    description: Optional[str] = Field(
        None, description="Description for the saved profile"
    )
    agent_type: str = Field(..., description="Type of agent (citizen, firm, etc.)")
    file_path: str = Field(..., description="Path to the temporary profile file in S3")


@router.get("/agent-profiles")
async def list_agent_profiles(
    request: Request,
) -> ApiResponseWrapper[List[Dict[str, Any]]]:
    """List all agent profiles for the current tenant"""

    tenant_id = await request.app.state.get_tenant_id(request)

    async with request.app.state.get_db() as db:
        db = cast(AsyncSession, db)

        # Query profiles from database
        stmt = (
            select(AgentProfileData)
            .where(AgentProfileData.tenant_id == tenant_id)
            .order_by(AgentProfileData.created_at.desc())
        )

        result = await db.execute(stmt)
        profiles = result.scalars().all()

        # Convert to list of dictionaries
        profile_list = []
        for profile in profiles:
            profile_list.append(
                {
                    "id": str(profile.id),
                    "name": profile.name,
                    "description": profile.description,
                    "agent_type": profile.agent_type,
                    "count": profile.record_count,
                    "created_at": profile.created_at.isoformat(),
                    "file_path": profile.file_path,
                }
            )

        return ApiResponseWrapper(data=profile_list)


@router.get("/agent-profiles/{profile_id}")
async def get_agent_profile(
    request: Request,
    profile_id: uuid.UUID,
) -> ApiResponseWrapper[List[Dict[str, Any]]]:
    """Get agent profile data by profile ID"""

    tenant_id = await request.app.state.get_tenant_id(request)

    async with request.app.state.get_db() as db:
        db = cast(AsyncSession, db)

        # Find the profile
        stmt = select(AgentProfileData).where(
            AgentProfileData.tenant_id == tenant_id, AgentProfileData.id == profile_id
        )
        result = await db.execute(stmt)
        profile = result.scalar_one_or_none()

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
            )

        # Get the file from S3
        env: EnvConfig = request.app.state.env
        fs_client = env.webui_fs_client
        try:
            content = fs_client.download(profile.file_path)
            data = json.loads(content)
            return ApiResponseWrapper(data=data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error retrieving profile data: {str(e)}",
            )


@router.delete("/agent-profiles/{profile_id}")
async def delete_agent_profile(
    request: Request,
    profile_id: uuid.UUID,
) -> ApiResponseWrapper[Dict[str, str]]:
    """Delete a saved agent profile"""
    if request.app.state.read_only:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Server is in read-only mode"
        )

    tenant_id = await request.app.state.get_tenant_id(request)

    if tenant_id == DEMO_USER_ID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo user is not allowed to delete profiles",
        )

    async with request.app.state.get_db() as db:
        db = cast(AsyncSession, db)

        # Find the profile
        stmt = select(AgentProfileData).where(
            AgentProfileData.tenant_id == tenant_id, AgentProfileData.id == profile_id
        )
        result = await db.execute(stmt)
        profile = result.scalar_one_or_none()

        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found"
            )

        # Delete the file from webui storage
        env: EnvConfig = request.app.state.env
        fs_client = env.webui_fs_client
        try:
            fs_client.delete(profile.file_path)
        except Exception as e:
            # Log error but continue with database deletion
            print(f"Error deleting file from S3: {str(e)}")

        # Delete from database
        stmt = delete(AgentProfileData).where(
            AgentProfileData.tenant_id == tenant_id, AgentProfileData.id == profile_id
        )
        await db.execute(stmt)
        await db.commit()

        return ApiResponseWrapper(data={"message": "Profile deleted successfully"})


@router.post("/agent-profiles/upload")
async def upload_agent_profile(
    request: Request,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
    agent_type: Optional[str] = Form("citizen"),
    description: Optional[str] = Form(None),
) -> ApiResponseWrapper[Dict[str, Any]]:
    """Upload an agent profile file and save it to the database"""
    if request.app.state.read_only:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Server is in read-only mode"
        )

    tenant_id = await request.app.state.get_tenant_id(request)

    if tenant_id == DEMO_USER_ID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo user is not allowed to upload profiles",
        )

    env: EnvConfig = request.app.state.env
    fs_client = env.webui_fs_client

    # Read file content
    content = await file.read()

    # Parse file based on extension
    filename = file.filename
    if filename is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="File name is required"
        )
    file_ext = filename.split(".")[-1].lower()

    try:
        # Validate and parse the file
        if file_ext == "json":
            data = json.loads(content)
            record_count = len(data)
        elif file_ext == "csv":
            # Parse CSV
            csv_content = content.decode("utf-8")
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            data = list(csv_reader)
            record_count = len(data)
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Unsupported file format. Please upload a CSV or JSON file.",
            )

        # Generate a unique ID for the file
        file_id = str(uuid.uuid4())
        s3_path = f"agent_profiles/{tenant_id}/{file_id}.json"

        # Convert to JSON and upload to S3
        data_json = json.dumps(data)
        fs_client.upload(data_json.encode("utf-8"), s3_path)

        # Use provided name or filename
        profile_name = name if name else os.path.splitext(filename)[0]
        profile_description = (
            description if description else f"Uploaded file: {filename}"
        )

        # Save metadata to database
        async with request.app.state.get_db() as db:
            db = cast(AsyncSession, db)

            # Create new profile data entry
            profile_id = uuid.uuid4()
            new_profile = AgentProfileData(
                tenant_id=tenant_id,
                id=profile_id,
                name=profile_name,
                description=profile_description,
                agent_type=agent_type,
                file_path=s3_path,
                record_count=record_count,
            )

            db.add(new_profile)
            await db.commit()

            return ApiResponseWrapper(
                data={
                    "id": str(profile_id),
                    "name": profile_name,
                    "agent_type": agent_type,
                    "count": record_count,
                    "created_at": new_profile.created_at.isoformat(),
                    "file_path": s3_path,
                }
            )
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}",
        )


@router.post("/agent-profiles/generate")
async def generate_agent_profiles(
    request: Request,
    preview_req: PreviewRequest = Body(...),
) -> ApiResponseWrapper[Dict[str, Any]]:
    """Generate agent profiles based on distributions and save to a temporary file"""

    # Limit the number of preview items for performance
    preview_count = min(preview_req.number, 1000)

    # Generate preview data
    preview_data = []

    # Convert API distributions to actual Distribution objects
    distributions = {}
    for mem_dist in preview_req.memory_distributions:
        dist_type = mem_dist.distribution.type
        params = mem_dist.distribution.params

        if dist_type == "choice":
            distributions[mem_dist.name] = ChoiceDistribution(
                choices=params.get("choices", "").split(","),
                weights=params.get("weights"),
            )
        elif dist_type == "uniform_int":
            distributions[mem_dist.name] = UniformIntDistribution(
                low=int(params.get("low", 0)), high=int(params.get("high", 100))
            )
        elif dist_type == "uniform_float":
            distributions[mem_dist.name] = UniformFloatDistribution(
                low=float(params.get("low", 0.0)), high=float(params.get("high", 1.0))
            )
        elif dist_type == "normal":
            distributions[mem_dist.name] = NormalDistribution(
                loc=float(params.get("loc", 0.0)), scale=float(params.get("scale", 1.0))
            )
        elif dist_type == "constant":
            distributions[mem_dist.name] = ConstantDistribution(
                val=params.get("val", "")
            )

    # Generate data using the distributions
    for i in range(preview_count):
        item = {"id": i}

        for field_name, distribution in distributions.items():
            item[field_name] = distribution.sample()

        preview_data.append(item)

    # Generate a unique preview ID
    preview_id = str(uuid.uuid4())

    # Save preview data to a temporary file in S3
    tenant_id = await request.app.state.get_tenant_id(request)
    env: EnvConfig = request.app.state.env

    fs_client = env.webui_fs_client
    path = f"agent_profiles_temp/{tenant_id}/{preview_id}.json"

    # Convert to JSON and upload to S3
    data_json = json.dumps(preview_data)
    fs_client.upload(data_json.encode("utf-8"), path)

    return ApiResponseWrapper(
        data={
            "preview_id": preview_id,
            "file_path": path,
            "count": len(preview_data),
            "data": preview_data[
                :10
            ],  # Return first 10 items for immediate preview
        }
    )


@router.post("/agent-profiles")
async def save_agent_profile(
    request: Request,
    profile_req: SaveProfileRequest = Body(...),
) -> ApiResponseWrapper[Dict[str, Any]]:
    """Save a generated agent profile to the database"""
    if request.app.state.read_only:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Server is in read-only mode"
        )

    tenant_id = await request.app.state.get_tenant_id(request)

    if tenant_id == DEMO_USER_ID:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo user is not allowed to save profiles",
        )

    env: EnvConfig = request.app.state.env

    # Security check: ensure the file path belongs to the tenant
    expected_prefix = f"agent_profiles_temp/{tenant_id}/"
    if not profile_req.file_path.startswith(expected_prefix):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this file"
        )

    # Download the temporary file from S3
    fs_client = env.webui_fs_client
    try:
        content = fs_client.download(profile_req.file_path)
        data = json.loads(content)
        record_count = len(data)

        # Generate a permanent file path
        file_id = str(uuid.uuid4())
        permanent_path = f"agent_profiles/{tenant_id}/{file_id}.json"

        # Upload to permanent location
        fs_client.upload(content, permanent_path)

        # Save metadata to database
        async with request.app.state.get_db() as db:
            db = cast(AsyncSession, db)

            # Create new profile data entry
            profile_id = uuid.uuid4()
            new_profile = AgentProfileData(
                tenant_id=tenant_id,
                id=profile_id,
                name=profile_req.name,
                description=profile_req.description
                or f"Generated profile for {profile_req.agent_type}",
                agent_type=profile_req.agent_type,
                file_path=permanent_path,
                record_count=record_count,
            )

            db.add(new_profile)
            await db.commit()

            # Delete the temporary file
            try:
                fs_client.delete(profile_req.file_path)
            except Exception as e:
                # Log error but continue
                print(f"Error deleting temporary file: {str(e)}")

            return ApiResponseWrapper(
                data={
                    "id": str(profile_id),
                    "name": profile_req.name,
                    "agent_type": profile_req.agent_type,
                    "count": record_count,
                    "created_at": new_profile.created_at.isoformat(),
                    "file_path": permanent_path,
                }
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error saving profile: {str(e)}",
        )
