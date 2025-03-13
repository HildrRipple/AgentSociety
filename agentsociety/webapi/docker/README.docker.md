# AgentSociety Docker 容器使用说明

本文档介绍如何构建和使用 AgentSociety 的 Docker 容器来运行实验。

## 构建 Docker 镜像

在webapi/docker目录下执行以下命令构建 Docker 镜像：

```bash
cd agentsociety/agentsociety/webapi/docker
./build_docker.sh
```

或者指定自定义标签：

```bash
./build_docker.sh -t custom-tag-name
```

## 使用 Docker 容器运行实验

### 基本用法

容器支持以下参数：

- `--sim-config-base64`: 使用 base64 编码的模拟器配置
- `--exp-config-base64`: 使用 base64 编码的实验配置
- `--sim-config-file`: 使用指定路径的模拟器配置文件
- `--exp-config-file`: 使用指定路径的实验配置文件
- `--log-level`: 设置日志级别 (debug, info, warning, error)
- `--help`: 显示帮助信息

### 使用 base64 编码的配置

1. 首先，将配置文件转换为 base64 编码：

```bash
# 转换模拟器配置
SIM_CONFIG_BASE64=$(cat sim_config.json | base64)

# 转换实验配置
EXP_CONFIG_BASE64=$(cat exp_config.json | base64)
```

2. 使用 base64 编码的配置运行容器：

```bash
docker run --rm agentsociety-runner \
  --sim-config-base64 "$SIM_CONFIG_BASE64" \
  --exp-config-base64 "$EXP_CONFIG_BASE64" \
  --log-level info
```

### 使用配置文件

1. 挂载包含配置文件的目录：

```bash
docker run --rm \
  -v /path/to/configs:/external-config \
  agentsociety-runner \
  --sim-config-file /external-config/sim_config.json \
  --exp-config-file /external-config/exp_config.json
```

## 在 experiment_runner.py 中使用

`experiment_runner.py` API已经集成了Docker容器的使用，您可以直接通过API调用来运行实验。详情请参考`agentsociety/webapi/api/experiment_runner.py`文件。

## 注意事项

1. 容器运行完成后会自动退出
2. 如果需要保存实验结果，请确保在配置中指定了正确的数据库连接信息
3. 如果实验需要访问外部服务（如 Redis、数据库等），请确保使用 `--network host` 参数或配置适当的网络设置 