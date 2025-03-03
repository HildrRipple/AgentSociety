from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List

from ..database import get_db
from ..models.experiment import Experiment, ExperimentStatus
from ..models.agent import AgentProfile
from ..models import ApiResponse
from ..utils import validate_uuid

router = APIRouter(tags=["agent_profiles"])


@router.get("/experiments/{exp_id}/agents/{agent_id}/profile", response_model=ApiResponse[AgentProfile])
def get_agent_profile_by_exp_id_and_agent_id(exp_id: str, agent_id: str, db: Session = Depends(get_db)):
    """获取指定实验中指定代理的资料"""
    exp_uuid = validate_uuid(exp_id, "Experiment ID")
    agent_uuid = validate_uuid(agent_id, "Agent ID")
    
    # 验证实验是否存在
    experiment = db.query(Experiment).filter(Experiment.id == exp_uuid).first()
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    
    if experiment.status == ExperimentStatus.NOT_STARTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Experiment has not started yet"
        )
    
    # 获取代理资料表名
    table_name = experiment.get_agent_profile_table_name()
    
    # 查询代理资料
    query = text(f"SELECT * FROM {table_name} WHERE id = :agent_id")
    result = db.execute(query, {"agent_id": agent_uuid}).fetchone()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agent not found"
        )
    
    # 转换为字典
    agent_data = dict(result._mapping)
    
    # 返回代理资料
    return ApiResponse(data=AgentProfile(**agent_data))


@router.get("/experiments/{exp_id}/agents/-/profile", response_model=ApiResponse[List[AgentProfile]])
def list_agent_profile_by_exp_id(exp_id: str, db: Session = Depends(get_db)):
    """获取指定实验中所有代理的资料"""
    try:
        exp_uuid = validate_uuid(exp_id, "Experiment ID")
        
        # 验证实验是否存在
        experiment = db.query(Experiment).filter(Experiment.id == exp_uuid).first()
        if not experiment:
            # 返回空数组而不是404错误
            return ApiResponse(data=[], code=200, message="Experiment not found")
        
        # 如果实验未开始，返回空数组而不是400错误
        if experiment.status == ExperimentStatus.NOT_STARTED:
            return ApiResponse(data=[], code=200, message="Experiment has not started yet")
        
        # 获取代理资料表名
        table_name = experiment.get_agent_profile_table_name()
        
        # 查询所有代理资料
        query = text(f"SELECT * FROM {table_name}")
        results = db.execute(query).fetchall()
        
        # 转换为AgentProfile列表
        agents = []
        for row in results:
            try:
                # 将Row对象转换为字典，确保所有值都是可JSON序列化的
                agent_data = {}
                for key, value in row._mapping.items():
                    if hasattr(value, '__dict__'):  # 如果是复杂对象
                        agent_data[key] = str(value)
                    else:
                        agent_data[key] = value
                
                agents.append(AgentProfile(**agent_data))
            except Exception as e:
                # 如果某个代理数据有问题，跳过它而不是整个失败
                print(f"Error processing agent data: {str(e)}")
                continue
        
        # 返回代理资料列表
        return ApiResponse(data=agents)
    
    except Exception as e:
        import traceback
        print(f"Error in list_agent_profile_by_exp_id: {str(e)}")
        print(traceback.format_exc())
        # 即使出错也返回空数组，而不是500错误
        return ApiResponse(data=[], code=500, message=f"Error: {str(e)}") 