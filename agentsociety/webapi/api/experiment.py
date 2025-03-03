from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
from typing import List
import uuid
import logging
from fastapi.responses import JSONResponse
import traceback

from ..database import get_db
from ..models.experiment import Experiment, ExperimentResponse, ExperimentStatus, TimeModel
from ..models import ApiResponse
from ..utils import validate_uuid

router = APIRouter(tags=["experiments"])

logger = logging.getLogger(__name__)


@router.get("/experiments", response_model=ApiResponse[List[ExperimentResponse]])
def list_experiments(db: Session = Depends(get_db)):
    """获取所有实验列表"""
    experiments = db.query(Experiment).all()
    return ApiResponse(data=experiments)


@router.get("/experiments/{exp_id}", response_model=ApiResponse[ExperimentResponse])
def get_experiment_by_id(exp_id: str, db: Session = Depends(get_db)):
    """根据ID获取实验详情"""
    exp_uuid = validate_uuid(exp_id, "Experiment ID")
    
    experiment = db.query(Experiment).filter(Experiment.id == exp_uuid).first()
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    
    return ApiResponse(data=experiment)


@router.get("/experiments/{exp_id}/timeline", response_model=ApiResponse[List[TimeModel]])
def get_experiment_status_timeline_by_id(exp_id: str, db: Session = Depends(get_db)):
    """获取实验状态时间线"""
    # 验证实验ID
    exp_uuid = validate_uuid(exp_id, "Experiment ID")
    
    # 查询实验
    experiment = db.query(Experiment).filter(Experiment.id == exp_uuid).first()
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    
    # 检查实验状态
    if experiment.status == ExperimentStatus.NOT_STARTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Experiment has not started yet"
        )
    
    # 获取代理状态表名
    table_name = experiment.get_agent_status_table_name()
    
    try:
        # 查询所有不同的时间点
        query = text(f"""
            SELECT day, t 
            FROM {table_name} 
            GROUP BY day, t 
            ORDER BY day, t
        """)
        
        results = db.execute(query).fetchall()
        
        # 如果没有数据，至少返回当前时间点
        if not results:
            return ApiResponse(data=[TimeModel(day=experiment.cur_day, t=experiment.cur_t)])
        
        # 将结果转换为TimeModel列表
        timeline = []
        for row in results:
            day_value = int(row[0]) if row[0] is not None else 0
            t_value = float(row[1]) if row[1] is not None else 0.0
            timeline.append(TimeModel(day=day_value, t=t_value))
        
        return ApiResponse(data=timeline)
    
    except Exception as e:
        logger.error(f"获取实验 {exp_id} 时间线时出错: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@router.delete("/experiments/{exp_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_experiment_by_id(exp_id: str, db: Session = Depends(get_db)):
    """删除实验"""
    from ..config import settings
    if settings.READ_ONLY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Server is in read-only mode"
        )
    
    exp_uuid = validate_uuid(exp_id, "Experiment ID")
    
    experiment = db.query(Experiment).filter(Experiment.id == exp_uuid).first()
    if not experiment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Experiment not found"
        )
    
    # 删除实验
    db.delete(experiment)
    db.commit()
    
    return None 