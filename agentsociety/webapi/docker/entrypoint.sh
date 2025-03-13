#!/bin/bash
set -e

# 帮助信息
function show_help {
    echo "AgentSociety 实验运行容器"
    echo "用法: docker run [docker参数] agentsociety-runner [脚本参数]"
    echo ""
    echo "参数:"
    echo "  --sim-config-base64 BASE64    使用base64编码的模拟器配置"
    echo "  --exp-config-base64 BASE64    使用base64编码的实验配置"
    echo "  --sim-config-file PATH        使用指定路径的模拟器配置文件"
    echo "  --exp-config-file PATH        使用指定路径的实验配置文件"
    echo "  --log-level LEVEL             设置日志级别 (debug, info, warning, error)"
    echo "  --help                        显示此帮助信息"
    echo ""
    echo "示例:"
    echo "  docker run agentsociety-runner --sim-config-base64 [BASE64] --exp-config-base64 [BASE64]"
    exit 0
}

# 默认参数
SIM_CONFIG_BASE64=""
EXP_CONFIG_BASE64=""
SIM_CONFIG_FILE=""
EXP_CONFIG_FILE=""
LOG_LEVEL="info"

# 解析参数
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        --sim-config-base64)
            SIM_CONFIG_BASE64="$2"
            shift
            shift
            ;;
        --exp-config-base64)
            EXP_CONFIG_BASE64="$2"
            shift
            shift
            ;;
        --sim-config-file)
            SIM_CONFIG_FILE="$2"
            shift
            shift
            ;;
        --exp-config-file)
            EXP_CONFIG_FILE="$2"
            shift
            shift
            ;;
        --log-level)
            LOG_LEVEL="$2"
            shift
            shift
            ;;
        --help)
            show_help
            ;;
        *)
            echo "未知参数: $1"
            show_help
            ;;
    esac
done

# 配置日志级别
export LOG_LEVEL=$LOG_LEVEL

# 处理配置文件
CONFIG_DIR="/config"
mkdir -p $CONFIG_DIR

# 处理模拟器配置
if [ ! -z "$SIM_CONFIG_BASE64" ]; then
    echo "使用base64编码的模拟器配置"
    echo $SIM_CONFIG_BASE64 | base64 -d > $CONFIG_DIR/sim_config.json
elif [ ! -z "$SIM_CONFIG_FILE" ]; then
    echo "使用文件路径的模拟器配置: $SIM_CONFIG_FILE"
    cp $SIM_CONFIG_FILE $CONFIG_DIR/sim_config.json
else
    echo "错误: 未提供模拟器配置"
    exit 1
fi

# 处理实验配置
if [ ! -z "$EXP_CONFIG_BASE64" ]; then
    echo "使用base64编码的实验配置"
    echo $EXP_CONFIG_BASE64 | base64 -d > $CONFIG_DIR/exp_config.json
elif [ ! -z "$EXP_CONFIG_FILE" ]; then
    echo "使用文件路径的实验配置: $EXP_CONFIG_FILE"
    cp $EXP_CONFIG_FILE $CONFIG_DIR/exp_config.json
else
    echo "错误: 未提供实验配置"
    exit 1
fi

# 创建并运行Python脚本
cat > /app/run_experiment.py << 'EOF'
import asyncio
import json
import logging
import os
import sys

# 配置日志
log_level = os.environ.get("LOG_LEVEL", "info").upper()
logging.basicConfig(
    level=getattr(logging, log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("experiment_runner")

async def main():
    try:
        from agentsociety.configs import ExpConfig, SimConfig
        from agentsociety.simulation import AgentSimulation
        
        # 从配置文件加载配置
        with open('/config/sim_config.json', 'r') as f:
            sim_config_dict = json.load(f)
            sim_config = SimConfig.parse_obj(sim_config_dict)
        
        with open('/config/exp_config.json', 'r') as f:
            exp_config_dict = json.load(f)
            exp_config = ExpConfig.parse_obj(exp_config_dict)
        
        logger.info(f"Starting experiment with config: {exp_config}")
        simulation = AgentSimulation.run_from_config(
            config=exp_config,
            sim_config=sim_config,
        )
        await simulation
        logger.info("Experiment completed successfully")
    except Exception as e:
        logger.error(f"Error in experiment: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
EOF

echo "开始运行实验..."
python /app/run_experiment.py

echo "实验运行完成，容器将退出" 