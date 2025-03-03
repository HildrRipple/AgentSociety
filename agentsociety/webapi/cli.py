import os
import argparse
import uvicorn
from dotenv import load_dotenv

from .config import settings


def main():
    """命令行入口函数"""
    # 加载环境变量
    load_dotenv()
    
    # 创建命令行参数解析器
    parser = argparse.ArgumentParser(description="SocialCity Web API Server")
    parser.add_argument("--host", type=str, help="Host to bind")
    parser.add_argument("--port", type=int, help="Port to bind")
    parser.add_argument("--pg-dsn", type=str, help="PostgreSQL DSN")
    parser.add_argument("--mqtt-broker", type=str, help="MQTT Broker")
    parser.add_argument("--mqtt-username", type=str, help="MQTT Username")
    parser.add_argument("--mqtt-password", type=str, help="MQTT Password")
    parser.add_argument("--mlflow-url", type=str, help="MLFlow URL")
    parser.add_argument("--read-only", action="store_true", help="Read-only mode")
    parser.add_argument("--reload", action="store_true", help="Enable auto-reload")
    
    # 解析命令行参数
    args = parser.parse_args()
    
    # 设置环境变量
    if args.pg_dsn:
        os.environ["DATABASE_URL"] = args.pg_dsn
    if args.mqtt_broker:
        os.environ["MQTT_BROKER"] = args.mqtt_broker
    if args.mqtt_username:
        os.environ["MQTT_USERNAME"] = args.mqtt_username
    if args.mqtt_password:
        os.environ["MQTT_PASSWORD"] = args.mqtt_password
    if args.mlflow_url:
        os.environ["MLFLOW_URL"] = args.mlflow_url
    if args.read_only:
        os.environ["READ_ONLY"] = "true"
    
    # 获取主机和端口
    host = args.host or os.getenv("HOST", settings.HOST)
    port = args.port or int(os.getenv("PORT", settings.PORT))
    
    # 启动服务器
    uvicorn.run(
        "agentsociety.webapi.main:app",
        host=host,
        port=port,
        reload=args.reload,
    )


if __name__ == "__main__":
    main() 