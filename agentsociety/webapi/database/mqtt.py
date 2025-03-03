import paho.mqtt.client as mqtt
import logging
from ..config import settings

# 配置日志
logger = logging.getLogger(__name__)

# MQTT客户端
mqtt_client = None


def init_mqtt_client():
    """初始化MQTT客户端"""
    global mqtt_client
    
    if not settings.MQTT_BROKER:
        logger.warning("MQTT broker not configured, MQTT client will not be initialized")
        return
    
    mqtt_client = mqtt.Client()
    
    # 设置用户名和密码（如果提供）
    if settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
        mqtt_client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
    
    # 连接回调
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            logger.info("Connected to MQTT broker")
        else:
            logger.error(f"Failed to connect to MQTT broker, return code: {rc}")
    
    mqtt_client.on_connect = on_connect
    
    # 连接到MQTT代理
    try:
        # 使用主机名和端口号
        mqtt_client.connect(settings.MQTT_BROKER, settings.MQTT_PORT)
        mqtt_client.loop_start()
        logger.info(f"MQTT client initialized and connected to {settings.MQTT_BROKER}:{settings.MQTT_PORT}")
    except Exception as e:
        logger.error(f"Failed to connect to MQTT broker: {e}")
        mqtt_client = None


def get_mqtt_client():
    """获取MQTT客户端"""
    global mqtt_client
    return mqtt_client 