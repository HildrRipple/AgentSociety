from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.orm import Session
from sqlalchemy import text
import uuid

from ..database import get_db
from ..models.experiment import Experiment, ExperimentStatus
from ..models.agent import AgentDialog, AgentDialogCreate
from ..utils import validate_uuid
from ..config import settings

router = APIRouter(tags=["agent_dialog"])


@router.get("/experiments/{exp_id}/agents/{agent_id}/dialog")
def get_agent_dialog_by_exp_id_and_agent_id(
    exp_id: str, 
    agent_id: str, 
    db: Session = Depends(get_db)
):
    """获取指定实验中指定代理的对话"""
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
    table_name = experiment.get_agent_dialog_table_name()
    
    # 使用原生SQL查询
    query = text(f"""
        SELECT * FROM {table_name} 
        WHERE speaker_id = :agent_id OR listener_id = :agent_id
        ORDER BY day ASC, t ASC
    """)
    result = db.execute(query, {"agent_id": agent_uuid}).fetchall()
    
    # 将结果转换为字典列表
    dialogs = [dict(row._mapping) for row in result]
    
    return {"data": dialogs}


@router.post("/experiments/{exp_id}/agents/{agent_id}/dialog", status_code=status.HTTP_201_CREATED)
def send_agent_dialog_by_exp_id_and_agent_id(
    exp_id: str,
    agent_id: str,
    dialog: AgentDialogCreate,
    db: Session = Depends(get_db)
):
    """为指定实验中的指定代理添加对话"""
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
    
    # 验证代理ID是否匹配
    if str(dialog.speaker_id) != str(agent_uuid) and str(dialog.listener_id) != str(agent_uuid):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agent ID must match either speaker_id or listener_id"
        )
    
    # 动态生成表名
    table_name = experiment.get_agent_dialog_table_name()
    
    # 创建新对话
    dialog_id = uuid.uuid4()
    query = text(f"""
        INSERT INTO {table_name} (
            id, day, t, speaker_id, speaker_name, listener_id, listener_name, content, location, extra, created_at
        ) VALUES (
            :id, :day, :t, :speaker_id, :speaker_name, :listener_id, :listener_name, :content, :location, :extra, NOW()
        )
    """)
    
    db.execute(query, {
        "id": dialog_id,
        "day": dialog.day,
        "t": dialog.t,
        "speaker_id": dialog.speaker_id,
        "speaker_name": dialog.speaker_name,
        "listener_id": dialog.listener_id,
        "listener_name": dialog.listener_name,
        "content": dialog.content,
        "location": dialog.location,
        "extra": dialog.extra
    })
    
    db.commit()
    
    return {"id": dialog_id} 