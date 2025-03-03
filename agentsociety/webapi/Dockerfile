FROM python:3.10-slim

WORKDIR /app

# 安装依赖
COPY webapi/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 设置环境变量
ENV PYTHONPATH=/app
ENV HOST=0.0.0.0
ENV PORT=8000

# 暴露端口
EXPOSE 8000

# 启动应用
CMD ["python", "-m", "agentsociety.webapi.main"] 