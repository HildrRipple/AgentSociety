import csv
import io
import json
import uuid
import os
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

from ...configs import EnvConfig
from ...s3 import S3Client
from ..models import ApiResponseWrapper
from ..models.agent_profiles import AgentProfile
from .const import DEMO_USER_ID

__all__ = ["router"]

router = APIRouter(tags=["agent_profiles"])


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
            select(AgentProfile)
            .where(AgentProfile.tenant_id == tenant_id)
            .order_by(AgentProfile.created_at.desc())
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
        stmt = select(AgentProfile).where(
            AgentProfile.tenant_id == tenant_id, AgentProfile.id == profile_id
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
        stmt = select(AgentProfile).where(
            AgentProfile.tenant_id == tenant_id, AgentProfile.id == profile_id
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
        stmt = delete(AgentProfile).where(
            AgentProfile.tenant_id == tenant_id, AgentProfile.id == profile_id
        )
        await db.execute(stmt)
        await db.commit()

        return ApiResponseWrapper(data={"message": "Profile deleted successfully"})


@router.post("/agent-profiles/upload")
async def upload_agent_profile(
    request: Request,
    file: UploadFile = File(...),
    name: Optional[str] = Form(None),
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
            new_profile = AgentProfile(
                tenant_id=tenant_id,
                id=profile_id,
                name=profile_name,
                description=profile_description,
                agent_type="citizen",  # 设置默认值
                file_path=s3_path,
                record_count=record_count,
            )

            db.add(new_profile)
            await db.commit()
            await db.refresh(new_profile)  # 刷新对象以获取数据库生成的值

            # 创建一个新的字典来存储响应数据
            response_data = {
                "id": str(profile_id),
                "name": profile_name,
                "description": profile_description,
                "count": record_count,
                "created_at": new_profile.created_at.isoformat() if new_profile.created_at else None,
                "file_path": s3_path,
            }
            return ApiResponseWrapper(data=response_data)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid JSON format"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing file: {str(e)}",
        )
