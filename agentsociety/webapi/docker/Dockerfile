# 提供两个基础镜像选项，默认使用amd64架构
# ARM64架构镜像
# FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12-alpine-linuxarm64

# AMD64架构镜像（默认使用）
FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12-slim

WORKDIR /app

# 安装基础依赖
# RUN apk add --no-cache \
#     build-base \
#     git \
#     && rm -rf /var/cache/apk/*

RUN apt-get update && apt-get install -y \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制项目代码
# 注意：构建时需要在项目根目录执行docker build命令
COPY pycityagent /app/pycityagent

# 安装agentsociety及其依赖
RUN cd /app && pip install -e ./pycityagent/agentsociety

# 创建配置目录
RUN mkdir -p /config

# 复制入口脚本
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"] 