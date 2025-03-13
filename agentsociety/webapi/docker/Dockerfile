FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12-alpine-linuxarm64
# FROM swr.cn-north-4.myhuaweicloud.com/ddn-k8s/docker.io/python:3.12-slim

WORKDIR /app

# 安装基础依赖
RUN apk add --no-cache \
    build-base \
    git \
    && rm -rf /var/cache/apk/*

# RUN apt-get update && apt-get install -y \
#     build-essential \
#     git \
#     && rm -rf /var/lib/apt/lists/*

# 复制项目代码
# 注意：构建时需要在项目根目录执行docker build命令
COPY agentsociety /app/agentsociety

# 安装agentsociety及其依赖
RUN cd /app && pip install -e ./agentsociety

# 创建配置目录
RUN mkdir -p /config

# 复制入口脚本
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"] 