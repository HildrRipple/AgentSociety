from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List, Optional

from ..database import get_db
from ..models.experiment import Experiment, ExperimentStatus
from ..models.agent import AgentStatus
from ..utils import validate_uuid

router = APIRouter(tags=["agent_status"])


@router.get("/experiments/{exp_id}/agents/{agent_id}/status")
def get_agent_status_by_exp_id_and_agent_id(
    exp_id: str, 
    agent_id: str, 
    db: Session = Depends(get_db)
):
    """获取指定实验中指定代理的状态"""
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
            detail="Experiment not started"
        )
    
    # 动态生成表名
    table_name = experiment.get_agent_status_table_name()
    
    # 使用原生SQL查询
    query = text(f"SELECT * FROM {table_name} WHERE id = :agent_id ORDER BY day DESC, t DESC")
    result = db.execute(query, {"agent_id": agent_uuid}).fetchall()
    
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Status not found"
        )
    
    # 将结果转换为字典列表
    statuses = [dict(row._mapping) for row in result]
    
    return {"data": statuses}


@router.get("/experiments/{exp_id}/agents/-/status")
def list_agent_status_by_day_and_t(
    exp_id: str, 
    day: Optional[int] = Query(None, description="指定天数"),
    t: Optional[float] = Query(None, description="指定时间点"),
    db: Session = Depends(get_db)
):
    """获取指定实验中所有代理在指定时间点的状态"""
    try:
        exp_uuid = validate_uuid(exp_id, "Experiment ID")
        
        # 验证实验是否存在
        experiment = db.query(Experiment).filter(Experiment.id == exp_uuid).first()
        if not experiment:
            return {"data": [], "message": "Experiment not found", "code": 404}
        
        # 如果实验未开始，返回空数组而不是错误
        if experiment.status == ExperimentStatus.NOT_STARTED:
            return {"data": [], "message": "Experiment not started", "code": 200}
        
        # 动态生成表名
        table_name = experiment.get_agent_status_table_name()
        
        # 构建查询条件
        conditions = []
        params = {}
        
        if day is not None:
            conditions.append("day = :day")
            params["day"] = day
        
        if t is not None:
            conditions.append("t = :t")
            params["t"] = t
        
        # 如果没有指定条件，使用最新的状态
        if not conditions:
            # 获取最新的day和t
            latest_query = text(f"""
                SELECT day, t FROM {table_name} 
                ORDER BY day DESC, t DESC 
                LIMIT 1
            """)
            latest = db.execute(latest_query).fetchone()
            
            if not latest:
                return {"data": []}
            
            conditions.append("day = :day")
            conditions.append("t = :t")
            params["day"] = latest.day
            params["t"] = latest.t
        
        # 构建完整查询
        where_clause = " AND ".join(conditions)
        query = text(f"SELECT * FROM {table_name} WHERE {where_clause}")
        
        # 执行查询
        result = db.execute(query, params).fetchall()
        
        # 将结果转换为字典列表
        statuses = []
        for row in result:
            # 使用dict()将Row对象转换为字典
            status_dict = {}
            for key, value in row._mapping.items():
                # 确保所有值都是可JSON序列化的
                if hasattr(value, '__dict__'):  # 如果是复杂对象
                    status_dict[key] = str(value)
                else:
                    status_dict[key] = value
            statuses.append(status_dict)
        
        return {"data": statuses}
    
    except Exception as e:
        import traceback
        print(f"Error in list_agent_status_by_day_and_t: {str(e)}")
        print(traceback.format_exc())
        # 即使出错也返回空数组，而不是500错误
        return {"data": [], "message": f"Error: {str(e)}", "code": 500} 