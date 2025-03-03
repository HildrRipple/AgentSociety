# SocialCity Web API

这是SocialCity Web的FastAPI后端实现，用于提供Agent Society的Web API服务。

## 功能特性

- 实验管理：创建、查询、删除实验
- 代理资料：查询代理的基本信息
- 代理状态：查询代理在不同时间点的状态
- 代理对话：查询和添加代理之间的对话
- 代理调查：查询和添加代理的调查回答
- 调查管理：创建、查询、更新和删除调查问卷

## 安装

### 依赖项

- Python 3.8+
- PostgreSQL
- MQTT Broker (可选)

### 安装步骤

1. 安装依赖项：

```bash
pip install -r requirements.txt
```

2. 配置环境变量（或创建.env文件）：

```
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/socialcity
MQTT_BROKER=localhost
MQTT_USERNAME=username
MQTT_PASSWORD=password
MLFLOW_URL=http://localhost:5000
HOST=0.0.0.0
PORT=8000
READ_ONLY=false
```

## 使用方法

### 启动服务器

```bash
python -m agentsociety.webapi.main
```

或者使用命令行参数：

```bash
python -m agentsociety.webapi.cli --host 0.0.0.0 --port 8000 --pg-dsn "postgresql://postgres:postgres@localhost:5432/socialcity"
```

### API文档

启动服务器后，可以访问以下URL查看API文档：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Docker部署

1. 构建Docker镜像：

```bash
docker build -t socialcity-api -f webapi/Dockerfile .
```

2. 运行Docker容器：

```bash
docker run -p 8000:8000 \
  -e DATABASE_URL=postgresql://postgres:postgres@host.docker.internal:5432/socialcity \
  -e MQTT_BROKER=host.docker.internal \
  socialcity-api
```

## 开发

### 项目结构

```
webapi/
├── api/                # API路由
├── config/             # 配置
├── database/           # 数据库连接
├── models/             # 数据模型
├── utils/              # 工具函数
├── main.py             # 主入口
├── cli.py              # 命令行入口
└── requirements.txt    # 依赖项
```

### 添加新API

1. 在`models/`目录中定义数据模型
2. 在`api/`目录中创建路由处理函数
3. 在`api/__init__.py`中注册路由 