# Stage 1: Compile the frontend code
FROM registry.fiblab.net/general/dev:latest as builder

WORKDIR /app
COPY . .

RUN npm config set registry https://registry.npmmirror.com
RUN ./rebuild_frontend.sh

# Stage 2: Copy the compiled frontend code to the python image
FROM python:3.12-slim

WORKDIR /app
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y
RUN pip config set global.index-url https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
COPY --from=builder /app /app
RUN pip install . --no-cache-dir \
    && rm -rf /app
