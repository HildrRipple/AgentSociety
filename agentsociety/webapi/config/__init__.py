from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """应用配置"""
    # 数据库配置
    # DATABASE_URL: str = "postgresql://postgres:test@localhost:5432/postgres"
    DATABASE_URL: str = "postgresql://llmsim:udb4lDy6P4yDmkSP@pg.db.fiblab.tech:5432/llmsim"
    
    # MQTT配置
    MQTT_BROKER: Optional[str] = "localhost"  # 只有主机名
    MQTT_PORT: int = 1883  # 端口号
    MQTT_USERNAME: Optional[str] = "emqx_u"
    MQTT_PASSWORD: Optional[str] = "EMQemq@1172"
    
    # MLFlow配置
    MLFLOW_URL: Optional[str] = "http://localhost:59000"
    
    # 服务器配置
    HOST: str = "localhost"
    PORT: int = 8080
    
    # 是否只读模式
    READ_ONLY: bool = False
    
    # 表前缀
    TABLE_PREFIX: str = "socialcity_"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


settings = Settings() 