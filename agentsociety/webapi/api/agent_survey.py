from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid

from ..database import get_db
from ..models.experiment import Experiment, ExperimentStatus
from ..models.agent import AgentSurvey, AgentSurveyCreate
from ..utils import validate_uuid
from ..config import settings

router = APIRouter(tags=["agent_survey"])


@router.get("/experiments/{exp_id}/agents/{agent_id}/survey")
def get_agent_survey_by_exp_id_and_agent_id(
    exp_id: str, 
    agent_id: str, 
    db: Session = Depends(get_db)
):
    """获取指定实验中指定代理的调查"""
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
    table_name = experiment.get_agent_survey_table_name()
    
    # 使用原生SQL查询
    query = text(f"""
        SELECT * FROM {table_name} 
        WHERE id = :agent_id
        ORDER BY created_at DESC
    """)
    result = db.execute(query, {"agent_id": agent_uuid}).fetchall()
    
    # 将结果转换为字典列表
    surveys = [dict(row._mapping) for row in result]
    
    return {"data": surveys}


@router.post("/experiments/{exp_id}/agents/{agent_id}/survey", status_code=status.HTTP_201_CREATED)
def send_agent_survey_by_exp_id_and_agent_id(
    exp_id: str,
    agent_id: str,
    survey: AgentSurveyCreate,
    db: Session = Depends(get_db)
):
    """为指定实验中的指定代理添加调查"""
    if settings.READ_ONLY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Server is in read-only mode"
        )
    
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
    
    # 验证调查是否存在
    survey_query = text("SELECT id FROM sc_survey WHERE id = :survey_id")
    survey_result = db.execute(survey_query, {"survey_id": survey.survey_id}).fetchone()
    if not survey_result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )
    
    # 动态生成表名
    table_name = experiment.get_agent_survey_table_name()
    
    # 创建新调查回答
    query = text(f"""
        INSERT INTO {table_name} (
            id, survey_id, answers, extra, created_at
        ) VALUES (
            :id, :survey_id, :answers, :extra, NOW()
        )
    """)
    
    db.execute(query, {
        "id": agent_uuid,
        "survey_id": survey.survey_id,
        "answers": survey.answers,
        "extra": survey.extra
    })
    
    db.commit()
    
    return {"id": agent_uuid} 