import uuid
from fastapi import HTTPException, status


def validate_uuid(id_str: str, param_name: str = "ID") -> uuid.UUID:
    """
    验证并转换UUID字符串
    
    Args:
        id_str: UUID字符串
        param_name: 参数名称，用于错误消息
    
    Returns:
        转换后的UUID对象
    
    Raises:
        HTTPException: 如果UUID格式无效
    """
    try:
        return uuid.UUID(id_str)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid {param_name} format"
        ) 