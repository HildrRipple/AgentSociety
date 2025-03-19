#!/bin/bash
set -e

# Help information
function show_help {
    echo "AgentSociety Experiment Runner Container"
    echo "Usage: docker run [docker options] agentsociety-runner [script options]"
    echo ""
    echo "Options:"
    echo "  --sim-config-base64 BASE64    Simulator configuration in base64 encoding"
    echo "  --exp-config-base64 BASE64    Experiment configuration in base64 encoding"
    echo "  --sim-config-file PATH        Path to simulator configuration file"
    echo "  --exp-config-file PATH        Path to experiment configuration file"
    echo "  --log-level LEVEL             Set log level (debug, info, warning, error)"
    echo "  --help                        Show this help message"
    echo ""
    echo "Example:"
    echo "  docker run agentsociety-runner --sim-config-base64 [BASE64] --exp-config-base64 [BASE64]"
    exit 0
}

# Default parameters
SIM_CONFIG_BASE64=""
EXP_CONFIG_BASE64=""
SIM_CONFIG_FILE=""
EXP_CONFIG_FILE=""
LOG_LEVEL="info"

# Parse arguments
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
            echo "Unknown parameter: $1"
            show_help
            ;;
    esac
done

# Configure log level
export LOG_LEVEL=$LOG_LEVEL

# Process configuration files
CONFIG_DIR="/config"
mkdir -p $CONFIG_DIR

# Process simulator configuration
if [ ! -z "$SIM_CONFIG_BASE64" ]; then
    echo "Using base64 encoded simulator configuration"
    echo $SIM_CONFIG_BASE64 | base64 -d > $CONFIG_DIR/sim_config.json
elif [ ! -z "$SIM_CONFIG_FILE" ]; then
    echo "Using simulator configuration from file: $SIM_CONFIG_FILE"
    cp $SIM_CONFIG_FILE $CONFIG_DIR/sim_config.json
else
    echo "Error: No simulator configuration provided"
    exit 1
fi

# Process experiment configuration
if [ ! -z "$EXP_CONFIG_BASE64" ]; then
    echo "Using base64 encoded experiment configuration"
    echo $EXP_CONFIG_BASE64 | base64 -d > $CONFIG_DIR/exp_config.json
elif [ ! -z "$EXP_CONFIG_FILE" ]; then
    echo "Using experiment configuration from file: $EXP_CONFIG_FILE"
    cp $EXP_CONFIG_FILE $CONFIG_DIR/exp_config.json
else
    echo "Error: No experiment configuration provided"
    exit 1
fi

# Create and run Python script
cat > /app/run_experiment.py << 'EOF'
import asyncio
import json
import logging
import os
import sys

# Configure logging
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
        
        # Load configurations from files
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

echo "Starting experiment..."
python /app/run_experiment.py

echo "Experiment completed, container will exit" 