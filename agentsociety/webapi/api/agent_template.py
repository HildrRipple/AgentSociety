import uuid
from typing import Dict, List, cast, Any

from fastapi import APIRouter, Body, HTTPException, Request, status
from sqlalchemy import delete, insert, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import ApiResponseWrapper
from ..models.agent_template import (
    AgentTemplateDB, 
    ApiAgentTemplate,
    TemplateBlock,
    Distribution,
    DistributionConfig,
    ChoiceDistribution,
    UniformIntDistribution,
    NormalDistribution,
    ChoiceDistributionConfig,
    UniformIntDistributionConfig,
    NormalDistributionConfig,
    BaseConfig,
    StatesConfig,
    AgentParams
)
from agentsociety.cityagent.societyagent import SocietyAgent
from agentsociety.cityagent.blocks.economy_block import EconomyBlock, WorkBlock, ConsumptionBlock, EconomyNoneBlock
from agentsociety.cityagent.blocks.mobility_block import MobilityBlock, PlaceSelectionBlock, MoveBlock, MobilityNoneBlock
from agentsociety.cityagent.blocks.other_block import OtherBlock, SleepBlock, OtherNoneBlock
from agentsociety.cityagent.blocks.social_block import SocialBlock, FindPersonBlock, MessageBlock, SocialNoneBlock

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
            
            api_templates = []
            for template in templates:
                # Convert distribution configuration from database to corresponding distribution objects
                memory_distributions_dict = {}
                for key, value in template.profile.items():
                    if isinstance(value, dict):
                        dist_type = value.get('type')
                        if dist_type == 'choice':
                            if 'params' in value:
                                memory_distributions_dict[key] = ChoiceDistribution(
                                    type='choice',
                                    params={
                                        'choices': value['params']['choices'],
                                        'weights': value['params']['weights']
                                    }
                                )
                            else:
                                memory_distributions_dict[key] = ChoiceDistributionConfig(
                                    type='choice',
                                    choices=value['choices'],
                                    weights=value['weights']
                                )
                        elif dist_type == 'uniform_int':
                            if 'params' in value:
                                memory_distributions_dict[key] = UniformIntDistribution(
                                    type='uniform_int',
                                    params={
                                        'min_value': value['params']['min_value'],
                                        'max_value': value['params']['max_value']
                                    }
                                )
                            else:
                                memory_distributions_dict[key] = UniformIntDistributionConfig(
                                    type='uniform_int',
                                    min_value=value['min_value'],
                                    max_value=value['max_value']
                                )
                        elif dist_type == 'normal':
                            if 'params' in value:
                                memory_distributions_dict[key] = NormalDistribution(
                                    type='normal',
                                    params={
                                        'mean': value['params']['mean'],
                                        'std': value['params']['std']
                                    }
                                )
                            else:
                                memory_distributions_dict[key] = NormalDistributionConfig(
                                    type='normal',
                                    mean=value['mean'],
                                    std=value['std']
                                )
                
                api_template = ApiAgentTemplate(
                    tenant_id=template.tenant_id,
                    id=template.id,
                    name=template.name,
                    description=template.description,
                    memory_distributions=memory_distributions_dict,
                    agent_params=AgentParams(**template.agent_params),
                    blocks=template.blocks,
                    created_at=template.created_at.isoformat() if template.created_at else None,
                    updated_at=template.updated_at.isoformat() if template.updated_at else None
                )
                api_templates.append(api_template)
            
            return ApiResponseWrapper(data=api_templates)
            
    except Exception as e:
        print(f"Error in list_agent_templates: {str(e)}")
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
            
            # Convert distribution configuration from database to corresponding distribution objects
            memory_distributions_dict = {}
            for key, value in template.profile.items():
                if isinstance(value, dict):
                    dist_type = value.get('type')
                    if dist_type == 'choice':
                        if 'params' in value:
                            memory_distributions_dict[key] = ChoiceDistribution(
                                type='choice',
                                params={
                                    'choices': value['params']['choices'],
                                    'weights': value['params']['weights']
                                }
                            )
                        else:
                            memory_distributions_dict[key] = ChoiceDistributionConfig(
                                type='choice',
                                choices=value['choices'],
                                weights=value['weights']
                            )
                    elif dist_type == 'uniform_int':
                        if 'params' in value:
                            memory_distributions_dict[key] = UniformIntDistribution(
                                type='uniform_int',
                                params={
                                    'min_value': value['params']['min_value'],
                                    'max_value': value['params']['max_value']
                                }
                            )
                        else:
                            memory_distributions_dict[key] = UniformIntDistributionConfig(
                                type='uniform_int',
                                min_value=value['min_value'],
                                max_value=value['max_value']
                            )
                    elif dist_type == 'normal':
                        if 'params' in value:
                            memory_distributions_dict[key] = NormalDistribution(
                                type='normal',
                                params={
                                    'mean': value['params']['mean'],
                                    'std': value['params']['std']
                                }
                            )
                        else:
                            memory_distributions_dict[key] = NormalDistributionConfig(
                                type='normal',
                                mean=value['mean'],
                                std=value['std']
                            )
            
            api_template = ApiAgentTemplate(
                tenant_id=template.tenant_id,
                id=template.id,
                name=template.name,
                description=template.description,
                memory_distributions=memory_distributions_dict,
                agent_params=AgentParams(**template.agent_params),
                blocks=template.blocks,
                created_at=template.created_at.isoformat() if template.created_at else None,
                updated_at=template.updated_at.isoformat() if template.updated_at else None
            )
            
            return ApiResponseWrapper(data=api_template)
            
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_agent_template: {str(e)}")
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
        
        # Convert memory_distributions to serializable dictionary format
        profile_dict = {}
        for key, value in template.memory_distributions.items():
            if isinstance(value, (ChoiceDistributionConfig, UniformIntDistributionConfig, NormalDistributionConfig)):
                # 如果是Config类型，直接转换为字典
                profile_dict[key] = value.dict()
            elif isinstance(value, (ChoiceDistribution, UniformIntDistribution, NormalDistribution)):
                # 如果是Distribution类型，保持params结构
                profile_dict[key] = value.dict()
            else:
                # 如果已经是字典格式，直接使用
                profile_dict[key] = value
        
        # Create default base configuration
        base_config = {
            "home": {"aoi_position": {"aoi_id": 0}},
            "work": {"aoi_position": {"aoi_id": 0}}
        }
        
        # Create default states configuration
        states_config = {
            "needs": "str",
            "plan": "dict"
        }
        
        async with request.app.state.get_db() as db:
            db = cast(AsyncSession, db)
            
            new_template = AgentTemplateDB(
                tenant_id=tenant_id,
                id=template_id,
                name=template.name,
                description=template.description,
                profile=profile_dict,
                base=base_config,
                states=states_config,
                agent_params=template.agent_params.dict(),
                blocks=template.blocks
            )
            
            db.add(new_template)
            await db.commit()
            await db.refresh(new_template)
            
            # Construct response data
            response_template = ApiAgentTemplate(
                tenant_id=new_template.tenant_id,
                id=new_template.id,
                name=new_template.name,
                description=new_template.description,
                memory_distributions=new_template.profile,
                base=new_template.base,
                states=new_template.states,
                agent_params=AgentParams(**new_template.agent_params),
                blocks=new_template.blocks,
                created_at=new_template.created_at.isoformat(),
                updated_at=new_template.updated_at.isoformat()
            )
            
            return ApiResponseWrapper(data=response_template)
            
    except Exception as e:
        print(f"Error details: {str(e)}")
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
            profile=template.memory_distributions,
            agent_params=template.agent_params.dict(),
            blocks=template.blocks
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

@router.get("/agent-functions")
async def get_agent_functions(
    request: Request,
) -> ApiResponseWrapper[List[Dict[str, str]]]:
    """Get available functions for agent"""
    try:
        functions_map = SocietyAgent.get_functions
        functions = [
            {
                "function_name": func_info["function_name"],
                "description": func_info["description"]
            }
            for func_info in functions_map.values()
        ]
        return ApiResponseWrapper(data=functions)
    except Exception as e:
        print(f"Error in get_agent_functions: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent functions: {str(e)}"
        )

@router.get("/agent-blocks")
async def get_agent_blocks(
    request: Request,
) -> ApiResponseWrapper[List[Dict[str, Any]]]:
    """Get available blocks and their functions for agent"""
    try:
        block_classes = [
            # CognitionBlock,
            EconomyBlock,
            MobilityBlock,
            OtherBlock,
            SocialBlock
        ]

        blocks = []
        for block_class in block_classes:
            # 获取参数类的字段信息
            params = {}
            if hasattr(block_class, 'ParamsType'):
                for field_name, field in block_class.ParamsType.__fields__.items():
                    if field_name == 'block_memory':
                        continue
                    type_name = field.annotation.__name__ if hasattr(field.annotation, '__name__') else str(field.annotation)
                    params[field_name] = {
                        "description": field.description if hasattr(field, 'description') else None,
                        "default": field.default,
                        "type": type_name
                    }

            block_info = {
                "block_name": block_class.name,
                "description": block_class.description,
                "functions": [
                    {
                        "function_name": func_info["function_name"],
                        "description": func_info["description"]
                    }
                    for func_info in block_class.get_functions.values()
                ],
                "params": params
            }
            blocks.append(block_info)

        return ApiResponseWrapper(data=blocks)
    except Exception as e:
        print(f"Error in get_agent_blocks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get agent blocks: {str(e)}"
        )