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

echo "Starting experiment..."

# Run the experiment using the CLI tool
if [ ! -z "$SIM_CONFIG_BASE64" ] && [ ! -z "$EXP_CONFIG_BASE64" ]; then
    python -m agentsociety.cli.runner --sim-config-base64 "$SIM_CONFIG_BASE64" --exp-config-base64 "$EXP_CONFIG_BASE64" --log-level "$LOG_LEVEL"
elif [ ! -z "$SIM_CONFIG_FILE" ] && [ ! -z "$EXP_CONFIG_FILE" ]; then
    python -m agentsociety.cli.runner --sim-config-file "$SIM_CONFIG_FILE" --exp-config-file "$EXP_CONFIG_FILE" --log-level "$LOG_LEVEL"
else
    echo "Error: No configuration provided"
    show_help
    exit 1
fi

echo "Experiment completed, container will exit" 