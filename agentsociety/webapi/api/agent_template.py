import uuid
from typing import Dict, List, cast

from fastapi import APIRouter, Body, HTTPException, Request, status
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ApiResponseWrapper
from ..models.agent_template import (
    AgentTemplateDB, 
    ApiAgentTemplate, 
    TemplateBlock,
    ProfileConfig,
    BaseConfig,
    StatesConfig,
    AgentParams
)

__all__ = ["router"]

router = APIRouter(tags=["agent_templates"])

@router.get("/agent-templates")
async def list_agent_templates(
    request: Request,
) -> ApiResponseWrapper[List[ApiAgentTemplate]]:
    """List all agent templates"""
    try:
        tenant_id = await request.app.state.get_tenant_id(request)
        
        async with request.app.state.get_db() as db:
            db = cast(AsyncSession, db)
            stmt = select(AgentTemplateDB).where(
                AgentTemplateDB.tenant_id.in_([tenant_id, ""])
            ).order_by(AgentTemplateDB.created_at.desc())
            
            result = await db.execute(stmt)
            templates = result.scalars().all()
            
            # 转换数据库模型到 API 模型
            api_templates = []
            for template in templates:
                api_template = ApiAgentTemplate(
                    tenant_id=template.tenant_id,
                    id=template.id,
                    name=template.name,
                    description=template.description,
                    profile=ProfileConfig(fields=template.profile.get('fields', {})),
                    base=BaseConfig(fields=template.base.get('fields', {})),
                    states=StatesConfig(
                        fields=template.states.get('fields', {}),
                        selfDefine=template.states.get('selfDefine', '')
                    ),
                    agent_params=AgentParams(**template.agent_params),
                    blocks=[TemplateBlock(**block) for block in template.blocks],
                    created_at=template.created_at.isoformat() if template.created_at else None,
                    updated_at=template.updated_at.isoformat() if template.updated_at else None
                )
                api_templates.append(api_template)
            
            return ApiResponseWrapper(data=api_templates)
            
    except Exception as e:
        print(f"Error in list_agent_templates: {str(e)}")  # 添加调试日志
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}"
        )

@router.get("/agent-templates/{template_id}")
async def get_agent_template(
    request: Request,
    template_id: str,
) -> ApiResponseWrapper[ApiAgentTemplate]:
    """Get agent template by ID"""
    try:
        tenant_id = await request.app.state.get_tenant_id(request)
        
        async with request.app.state.get_db() as db:
            db = cast(AsyncSession, db)
            stmt = select(AgentTemplateDB).where(
                AgentTemplateDB.tenant_id.in_([tenant_id, ""]),
                AgentTemplateDB.id == template_id
            )
            
            result = await db.execute(stmt)
            template = result.scalar_one_or_none()
            
            if not template:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Template not found"
                )
            
            # 转换为 API 模型
            api_template = ApiAgentTemplate(
                tenant_id=template.tenant_id,
                id=template.id,
                name=template.name,
                description=template.description,
                profile=ProfileConfig(fields=template.profile.get('fields', {})),
                base=BaseConfig(fields=template.base.get('fields', {})),
                states=StatesConfig(
                    fields=template.states.get('fields', {}),
                    selfDefine=template.states.get('selfDefine', '')
                ),
                agent_params=AgentParams(**template.agent_params),
                blocks=[TemplateBlock(**block) for block in template.blocks],
                created_at=template.created_at.isoformat() if template.created_at else None,
                updated_at=template.updated_at.isoformat() if template.updated_at else None
            )
            
            return ApiResponseWrapper(data=api_template)
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_agent_template: {str(e)}")  # 添加调试日志
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get template: {str(e)}"
        )

@router.post("/agent-templates")
async def create_agent_template(
    request: Request,
    template: ApiAgentTemplate = Body(...),
) -> ApiResponseWrapper[ApiAgentTemplate]:
    """Create a new agent template"""
    if request.app.state.read_only:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Server is in read-only mode"
        )
    
    try:
        tenant_id = await request.app.state.get_tenant_id(request)
        template_id = str(uuid.uuid4())
        
        async with request.app.state.get_db() as db:
            db = cast(AsyncSession, db)
            
            # 创建新模板
            new_template = AgentTemplateDB(
                tenant_id=tenant_id,
                id=template_id,
                name=template.name,
                description=template.description,
                profile=template.profile.dict() if template.profile else {},
                base=template.base.dict() if template.base else {},
                states=template.states.dict() if template.states else {},
                agent_params=template.agent_params.dict() if template.agent_params else {},
                blocks=[block.dict() for block in template.blocks] if template.blocks else []
            )
            
            db.add(new_template)
            await db.commit()
            await db.refresh(new_template)
            
            # 构造返回数据
            response_template = ApiAgentTemplate(
                tenant_id=new_template.tenant_id,
                id=new_template.id,
                name=new_template.name,
                description=new_template.description,
                profile=new_template.profile,
                base=new_template.base,
                states=new_template.states,
                agent_params=new_template.agent_params,
                blocks=[TemplateBlock(**block) for block in new_template.blocks],
                created_at=new_template.created_at.isoformat(),
                updated_at=new_template.updated_at.isoformat()
            )
            
            return ApiResponseWrapper(data=response_template)
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create template: {str(e)}"
        )

@router.put("/agent-templates/{template_id}")
async def update_agent_template(
    request: Request,
    template_id: str,
    template: ApiAgentTemplate = Body(...),
) -> ApiResponseWrapper[ApiAgentTemplate]:
    """Update an existing agent template"""
    if request.app.state.read_only:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Server is in read-only mode"
        )
    
    tenant_id = await request.app.state.get_tenant_id(request)
    
    async with request.app.state.get_db() as db:
        db = cast(AsyncSession, db)
        stmt = update(AgentTemplateDB).where(
            AgentTemplateDB.tenant_id == tenant_id,
            AgentTemplateDB.id == template_id
        ).values(
            name=template.name,
            description=template.description,
            profile=template.profile,
            base=template.base,
            states=template.states,
            agent_params=template.agent_params,
            blocks=[block.dict() for block in template.blocks]
        )
        
        result = await db.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        await db.commit()
        return ApiResponseWrapper(data=template)

@router.delete("/agent-templates/{template_id}")
async def delete_agent_template(
    request: Request,
    template_id: str,
) -> ApiResponseWrapper[Dict[str, str]]:
    """Delete an agent template"""
    if request.app.state.read_only:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Server is in read-only mode"
        )
    
    tenant_id = await request.app.state.get_tenant_id(request)
    
    async with request.app.state.get_db() as db:
        db = cast(AsyncSession, db)
        stmt = delete(AgentTemplateDB).where(
            AgentTemplateDB.tenant_id == tenant_id,
            AgentTemplateDB.id == template_id
        )
        
        result = await db.execute(stmt)
        if result.rowcount == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Template not found"
            )
        
        await db.commit()
        return ApiResponseWrapper(data={"message": "Template deleted successfully"})