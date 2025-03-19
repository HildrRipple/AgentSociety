# AgentSociety Docker Container Usage Guide

This document explains how to build and use the AgentSociety Docker container to run experiments.

## Building the Docker Image

Execute the following command in the webapi/docker directory to build the Docker image:

```bash
cd agentsociety/agentsociety/webapi/docker
./build_docker.sh
```

Or specify a custom tag:

```bash
./build_docker.sh -t custom-tag-name
```

## Running Experiments with Docker Container

### Basic Usage

The container supports the following parameters:

- `--sim-config-base64`: Simulator configuration in base64 encoding
- `--exp-config-base64`: Experiment configuration in base64 encoding
- `--sim-config-file`: Path to simulator configuration file
- `--exp-config-file`: Path to experiment configuration file
- `--log-level`: Set log level (debug, info, warning, error)
- `--help`: Show help information

### Using Base64 Encoded Configuration

1. First, convert configuration files to base64 encoding:

```bash
# Convert simulator configuration
SIM_CONFIG_BASE64=$(cat sim_config.json | base64)

# Convert experiment configuration
EXP_CONFIG_BASE64=$(cat exp_config.json | base64)
```

2. Run the container with base64 encoded configurations:

```bash
docker run --rm agentsociety-runner \
  --sim-config-base64 "$SIM_CONFIG_BASE64" \
  --exp-config-base64 "$EXP_CONFIG_BASE64" \
  --log-level info
```

### Using Configuration Files

1. Mount a directory containing configuration files:

```bash
docker run --rm \
  -v /path/to/configs:/external-config \
  agentsociety-runner \
  --sim-config-file /external-config/sim_config.json \
  --exp-config-file /external-config/exp_config.json
```

## Using in experiment_runner.py

The `experiment_runner.py` API has integrated the use of Docker containers. You can run experiments directly through the API. For details, refer to the `agentsociety/webapi/api/experiment_runner.py` file.

## Notes

1. The container will exit automatically after the experiment completes
2. If you need to save experiment results, make sure to specify the correct database connection information in the configuration
3. If the experiment needs to access external services (such as Redis, database, etc.), make sure to use the `--network host` parameter or configure appropriate network settings 