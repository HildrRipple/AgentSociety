from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models.survey import Survey, SurveyCreate, SurveyUpdate, SurveyResponse
from ..models import ApiResponse
from ..utils import validate_uuid
from ..config import settings

router = APIRouter(tags=["surveys"])


@router.get("/surveys", response_model=ApiResponse[List[SurveyResponse]])
def list_survey(db: Session = Depends(get_db)):
    """获取所有调查列表"""
    surveys = db.query(Survey).all()
    return ApiResponse(data=surveys)


@router.get("/surveys/{id}", response_model=ApiResponse[SurveyResponse])
def get_survey(id: str, db: Session = Depends(get_db)):
    """根据ID获取调查详情"""
    survey_uuid = validate_uuid(id, "Survey ID")
    
    survey = db.query(Survey).filter(Survey.id == survey_uuid).first()
    if not survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )
    
    return ApiResponse(data=survey)


@router.post("/surveys", response_model=ApiResponse[SurveyResponse], status_code=status.HTTP_201_CREATED)
def create_survey(survey: SurveyCreate, db: Session = Depends(get_db)):
    """创建新调查"""
    if settings.READ_ONLY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Server is in read-only mode"
        )
    
    db_survey = Survey(
        title=survey.title,
        description=survey.description,
        questions=survey.questions
    )
    
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    
    return ApiResponse(data=db_survey)


@router.put("/surveys/{id}", response_model=ApiResponse[SurveyResponse])
def update_survey(id: str, survey: SurveyUpdate, db: Session = Depends(get_db)):
    """更新调查"""
    if settings.READ_ONLY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Server is in read-only mode"
        )
    
    survey_uuid = validate_uuid(id, "Survey ID")
    
    db_survey = db.query(Survey).filter(Survey.id == survey_uuid).first()
    if not db_survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )
    
    # 更新字段
    db_survey.title = survey.title
    db_survey.description = survey.description
    db_survey.questions = survey.questions
    
    db.commit()
    db.refresh(db_survey)
    
    return ApiResponse(data=db_survey)


@router.delete("/surveys/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_survey(id: str, db: Session = Depends(get_db)):
    """删除调查"""
    if settings.READ_ONLY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Server is in read-only mode"
        )
    
    survey_uuid = validate_uuid(id, "Survey ID")
    
    db_survey = db.query(Survey).filter(Survey.id == survey_uuid).first()
    if not db_survey:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Survey not found"
        )
    
    db.delete(db_survey)
    db.commit()
    
    return None