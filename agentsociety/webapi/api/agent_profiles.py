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
        if not env.s3.enabled:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="S3 is not enabled"
            )

        client = S3Client(env.s3)
        try:
            content = client.download(profile.file_path)
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

        # Delete the file from S3
        env: EnvConfig = request.app.state.env
        if env.s3.enabled:
            client = S3Client(env.s3)
            try:
                client.delete(profile.file_path)
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

    if not env.s3.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="S3 is not enabled"
        )

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
        client = S3Client(env.s3)
        data_json = json.dumps(data)
        client.upload(data_json.encode("utf-8"), s3_path)

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

    if env.s3.enabled:
        client = S3Client(env.s3)
        s3_path = f"agent_profiles_temp/{tenant_id}/{preview_id}.json"

        # Convert to JSON and upload to S3
        data_json = json.dumps(preview_data)
        client.upload(data_json.encode("utf-8"), s3_path)

        return ApiResponseWrapper(
            data={
                "preview_id": preview_id,
                "file_path": s3_path,
                "count": len(preview_data),
                "data": preview_data[
                    :10
                ],  # Return first 10 items for immediate preview
            }
        )
    else:
        return ApiResponseWrapper(
            data={
                "preview_id": preview_id,
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

    if not env.s3.enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="S3 is not enabled"
        )

    # Security check: ensure the file path belongs to the tenant
    expected_prefix = f"agent_profiles_temp/{tenant_id}/"
    if not profile_req.file_path.startswith(expected_prefix):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Access denied to this file"
        )

    # Download the temporary file from S3
    client = S3Client(env.s3)
    try:
        content = client.download(profile_req.file_path)
        data = json.loads(content)
        record_count = len(data)

        # Generate a permanent file path
        file_id = str(uuid.uuid4())
        permanent_path = f"agent_profiles/{tenant_id}/{file_id}.json"

        # Upload to permanent location
        client.upload(content, permanent_path)

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
                client.delete(profile_req.file_path)
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


# @router.get("/agent-profiles/file/{file_path:path}")
# async def get_agent_profiles(
#     request: Request,
#     file_path: str,
#     offset: int = Query(0, description="Pagination offset"),
#     limit: int = Query(100, description="Pagination limit")
# ):
#     """Get agent profiles from a file with pagination"""
#     tenant_id = await request.app.state.get_tenant_id(request)
#     env: EnvConfig = request.app.state.env

#     # Security check: ensure the file path belongs to the tenant
#     valid_prefixes = [
#         f"agent_profiles_temp/{tenant_id}/",
#         f"agent_profiles/{tenant_id}/"
#     ]

#     if not any(file_path.startswith(prefix) for prefix in valid_prefixes):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Access denied to this file"
#         )

#     if not env.s3.enabled:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="S3 is not enabled"
#         )

#     # Download from S3
#     client = S3Client(env.s3)
#     try:
#         content = client.download(file_path)
#         data = json.loads(content)

#         # Get total count
#         total_count = len(data)

#         # Apply pagination
#         paginated_data = data[offset:offset+limit]

#         return ApiResponseWrapper(data={
#             "profiles": paginated_data,
#             "total": total_count,
#             "offset": offset,
#             "limit": limit
#         })
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"File not found or error reading file: {str(e)}"
#         )


# @router.put("/agent-profiles/file/{file_path:path}")
# async def update_agent_profiles(
#     request: Request,
#     file_path: str,
#     edit_req: EditProfileRequest = Body(...),
# ):
#     """Update agent profiles in a file"""
#     if request.app.state.read_only:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Server is in read-only mode"
#         )

#     tenant_id = await request.app.state.get_tenant_id(request)
#     env: EnvConfig = request.app.state.env

#     # Security check: ensure the file path belongs to the tenant
#     valid_prefixes = [
#         f"agent_profiles_temp/{tenant_id}/",
#         f"agent_profiles/{tenant_id}/"
#     ]

#     if not any(file_path.startswith(prefix) for prefix in valid_prefixes):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Access denied to this file"
#         )

#     if not env.s3.enabled:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="S3 is not enabled"
#         )

#     # Ensure the file path in the request matches the URL
#     if edit_req.file_path != file_path:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="File path in request body does not match URL"
#         )

#     # Upload updated data to S3
#     client = S3Client(env.s3)
#     try:
#         data_json = json.dumps(edit_req.agents)
#         client.upload(data_json.encode("utf-8"), file_path)

#         return ApiResponseWrapper(data={
#             "message": "Profiles updated successfully",
#             "file_path": file_path,
#             "record_count": len(edit_req.agents)
#         })
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error updating profiles: {str(e)}"
#         )


# @router.post("/agent-profiles/upload-file")
# async def upload_agent_profile_file(
#     request: Request,
#     file: UploadFile = File(...),
# ):
#     """Upload an agent profile file to S3"""
#     if request.app.state.read_only:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, detail="Server is in read-only mode"
#         )

#     tenant_id = await request.app.state.get_tenant_id(request)
#     env: EnvConfig = request.app.state.env

#     # Validate file extension
#     if not file.filename or not (file.filename.endswith('.json') or file.filename.endswith('.jsonl')):
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Only .json or .jsonl files are allowed"
#         )

#     # Generate a unique profile ID
#     profile_id = str(uuid.uuid4())

#     # Construct S3 path
#     s3_path = f"agent_profiles/{tenant_id}/{profile_id}{file.filename[file.filename.rfind('.'):]}"

#     if not env.s3.enabled:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="S3 is not enabled"
#         )

#     # Upload to S3
#     client = S3Client(env.s3)
#     content = await file.read()

#     # Validate JSON format
#     try:
#         if file.filename.endswith('.json'):
#             data = json.loads(content)
#             record_count = len(data) if isinstance(data, list) else 1
#         elif file.filename.endswith('.jsonl'):
#             lines = [line for line in content.decode('utf-8').splitlines() if line.strip()]
#             for line in lines:
#                 json.loads(line)
#             record_count = len(lines)
#     except json.JSONDecodeError:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="Invalid JSON format"
#         )

#     client.upload(content, s3_path)

#     # Extract filename without extension
#     filename = os.path.splitext(file.filename)[0]

#     # Save metadata to database
#     async with request.app.state.get_db() as db:
#         db = cast(AsyncSession, db)

#         # Create new profile data entry
#         new_profile = AgentProfileData(
#             tenant_id=tenant_id,
#             id=uuid.uuid4(),
#             name=filename,
#             description=f"Uploaded file: {file.filename}",
#             agent_type="unknown",  # Default type, can be updated later
#             file_path=s3_path,
#             record_count=record_count
#         )

#         db.add(new_profile)
#         await db.commit()

#         return ApiResponseWrapper(data={
#             "file_path": s3_path,
#             "profile_id": str(new_profile.id),
#             "record_count": record_count
#         })


# @router.get("/agent-profiles/file/{file_path:path}")
# async def get_agent_profile_file(
#     request: Request,
#     file_path: str,
# ):
#     """Get agent profile file content from S3"""
#     tenant_id = await request.app.state.get_tenant_id(request)
#     env: EnvConfig = request.app.state.env

#     # Security check: ensure the file path belongs to the tenant
#     expected_prefix = f"agent_profiles/{tenant_id}/"
#     if not file_path.startswith(expected_prefix):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Access denied to this file"
#         )

#     if not env.s3.enabled:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="S3 is not enabled"
#         )

#     # Download from S3
#     client = S3Client(env.s3)
#     try:
#         content = client.download(file_path)

#         # Parse the content based on file extension
#         if file_path.endswith('.json'):
#             data = json.loads(content)
#         elif file_path.endswith('.jsonl'):
#             data = [json.loads(line) for line in content.decode('utf-8').splitlines() if line.strip()]
#         else:
#             raise HTTPException(
#                 status_code=status.HTTP_400_BAD_REQUEST,
#                 detail="Unsupported file format"
#             )

#         return ApiResponseWrapper(data=data)
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"File not found or error reading file: {str(e)}"
#         )


# @router.delete("/agent-profiles/file/{file_path:path}")
# async def delete_agent_profile_file(
#     request: Request,
#     file_path: str,
# ):
#     """Delete agent profile file from S3 without removing database entry"""
#     if request.app.state.read_only:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN, detail="Server is in read-only mode"
#         )

#     tenant_id = await request.app.state.get_tenant_id(request)

#     if tenant_id == DEMO_USER_ID:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Demo user is not allowed to delete files"
#         )

#     env: EnvConfig = request.app.state.env

#     # Security check: ensure the file path belongs to the tenant
#     expected_prefix = f"agent_profiles/{tenant_id}/"
#     if not file_path.startswith(expected_prefix):
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Access denied to this file"
#         )

#     if not env.s3.enabled:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="S3 is not enabled"
#         )

#     # Delete from S3
#     client = S3Client(env.s3)
#     try:
#         client.delete(file_path)

#         # Also delete any database entries that reference this file
#         async with request.app.state.get_db() as db:
#             db = cast(AsyncSession, db)

#             stmt = delete(AgentProfileData).where(
#                 AgentProfileData.tenant_id == tenant_id,
#                 AgentProfileData.file_path == file_path
#             )
#             await db.execute(stmt)
#             await db.commit()

#         return ApiResponseWrapper(data={"message": "File deleted successfully"})
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail=f"File not found or error deleting file: {str(e)}"
#         )


# @router.get("/agent-profiles/files")
# async def list_agent_profile_files(
#     request: Request,
# ):
#     """List all agent profile files for the tenant (raw files, not database entries)"""
#     tenant_id = await request.app.state.get_tenant_id(request)
#     env: EnvConfig = request.app.state.env

#     if not env.s3.enabled:
#         raise HTTPException(
#             status_code=status.HTTP_400_BAD_REQUEST,
#             detail="S3 is not enabled"
#         )

#     # List files from S3
#     client = S3Client(env.s3)
#     prefix = f"agent_profiles/{tenant_id}/"

#     try:
#         files = client.list_objects(prefix)

#         # Format the response
#         file_list = []
#         for file_path in files:
#             # Extract filename from path
#             filename = file_path.split('/')[-1]
#             file_list.append({
#                 "file_path": file_path,
#                 "filename": filename,
#                 "url": f"/api/agent-profiles/file/{file_path}"
#             })

#         return ApiResponseWrapper(data=file_list)
#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Error listing files: {str(e)}"
#         )
