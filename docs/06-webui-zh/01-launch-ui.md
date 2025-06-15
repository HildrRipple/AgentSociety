# 启动 Web 界面

```{admonition} 提示
:class: hint
如果您想在本地部署服务，可以按照本节说明进行操作。如果您不想自己部署，而是想直接使用我们的在线平台，可以跳过本节。
```

首先需要创建一个包含所需环境信息的配置文件（例如 `config.yaml`）。配置包括：

```{admonition} 提示
:class: hint
配置格式与[配置](../02-configuration/01-configuration.md)章节类似。
如果您不想更改 `addr`、`read_only`、`debug` 和 `logging_level`，可以直接使用模拟的配置文件来启动 Web 界面。
```

- 必填字段：
  ```yaml
  env: EnvConfig  # 环境配置，参见 `agentsociety/configs/env.py` 中的 EnvConfig 定义
  ```

- 可选字段：
  ```yaml
  addr: str            # 服务地址，默认为 "127.0.0.1:8080"
  read_only: bool      # 只读模式，默认为 false
  debug: bool          # 调试模式，默认为 false
  logging_level: str   # 日志级别，默认为 "INFO"
  ```

配置完成后，使用以下命令启动后端服务：

 ```bash
 agentsociety ui -c config.yaml
 ```

- config.yaml 示例
    ```yaml
    addr: 127.0.0.1:8080 # 可选：UI 服务地址
    env: # 必填
      db:
        enabled: true    # 启用数据库存储
        db_type: sqlite | postgresql
        pg_dsn: postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE  # PostgreSQL 连接字符串
    ```

UI 服务将在 `http://localhost:8080` 或您在配置文件中指定的地址上可用。

```{admonition} 提示
:class: hint
默认的 `addr` 是 `127.0.0.1:8080`，这样 WebUI 服务器只能在本地机器上访问。
如果您想从其他机器访问 WebUI，可以将 `addr` 改为 `0.0.0.0:8080`。
请注意，将 `addr` 改为公开访问会带来安全风险。
```