import base64
import importlib.metadata
import json
import os
from pathlib import Path
from typing import Any, Dict, Literal, Optional
from urllib.parse import urlsplit

import click
from fastapi import APIRouter
import yaml
from pydantic import BaseModel, Field, model_validator

version_string_of_agentsociety = importlib.metadata.version("agentsociety")

CONTEXT_SETTINGS = {"help_option_names": ["-h", "--help"]}
PARAM_DECLS_VERSION = ("-V", "--version")


def load_config(
    config_path: Optional[str] = None, config_base64: Optional[str] = None
) -> Dict[Any, Any]:
    """Load configuration file, supports JSON and YAML formats, as well as base64 encoded config"""
    if config_base64:
        # Decode base64 config
        config_str = base64.b64decode(config_base64).decode("utf-8")
        # For base64 encoded config, try both JSON and YAML parsing
        try:
            # Try to parse as JSON
            return json.loads(config_str)
        except json.JSONDecodeError:
            try:
                # Try to parse as YAML
                return yaml.safe_load(config_str)
            except yaml.YAMLError as e:
                raise click.BadParameter(f"Failed to parse base64 config: {e}")
    elif config_path:
        # Determine format based on file extension
        path = Path(config_path)
        if not path.exists():
            raise click.BadParameter(f"Config file {config_path} does not exist")
        file_ext = path.suffix.lower()
        if file_ext in [".json"]:
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError as e:
                raise click.BadParameter(f"Failed to parse JSON config file: {e}")
        elif file_ext in [".yaml", ".yml"]:
            try:
                with open(config_path, "r", encoding="utf-8") as f:
                    return yaml.safe_load(f)
            except yaml.YAMLError as e:
                raise click.BadParameter(f"Failed to parse YAML config file: {e}")
        else:
            raise click.BadParameter(f"Unsupported config file format: {file_ext}")
    else:
        raise click.BadParameter("No config file or base64 encoded config provided")


def common_options(f):
    """Common configuration options decorator"""
    f = click.option("--config", "-c", help="Path to config file (.json, .yml, .yaml)")(
        f
    )
    f = click.option(
        "--config-base64", help="Base64 encoded config with JSON or YAML format"
    )(f)
    return f


@click.group(context_settings=CONTEXT_SETTINGS)
@click.version_option(version=version_string_of_agentsociety, prog_name="AgentSociety")
def cli():
    """AgentSociety CLI tool"""
    pass


@cli.command()
@common_options
def ui(config: str, config_base64: str):
    """Launch AgentSociety GUI"""
    config_data = load_config(config, config_base64)

    import uvicorn

    from ..configs import EnvConfig
    from ..logger import get_logger, set_logger_level
    from ..webapi.app import create_app, empty_get_tenant_id
    from ..casdoor.api import CasdoorConfig, Casdoor, login_router, auth_bearer_token
    from ..executor import KubernetesExecutor, ProcessExecutor

    class WebUIConfig(BaseModel):
        addr: str = Field(default="127.0.0.1:8080")
        casdoor: CasdoorConfig = Field(
            default_factory=lambda: CasdoorConfig.model_validate(
                {
                    "enabled": False,
                    "client_id": "",
                    "client_secret": "",
                    "application_name": "",
                    "endpoint": "",
                    "org_name": "",
                    "certificate": "",
                }
            )
        )
        callback_url: str = "http://web.agentsociety.svc.cluster.local"
        env: EnvConfig
        read_only: bool = Field(default=False)
        debug: bool = Field(default=False)
        logging_level: str = Field(default="INFO")
        executor: Literal["kubernetes", "process"] = Field(default="kubernetes")

        @model_validator(mode="after")
        def validate_executor(self):
            if self.executor == "kubernetes":
                if not self.env.s3.enabled:
                    raise ValueError(
                        "S3 must be enabled when using kubernetes executor"
                    )
            return self

    async def _main():
        c = WebUIConfig.model_validate(config_data)
        set_logger_level(c.logging_level.upper())
        get_logger().info("Launching AgentSociety WebUI")
        get_logger().debug(f"WebUI config: {c}")
        # for compatibility with the old config
        # postgres:// in DSN is not supported by SQLAlchemy
        # replace it with postgresql://

        pg_dsn = c.env.pgsql.dsn
        if pg_dsn.startswith("postgresql://"):
            pg_dsn = pg_dsn.replace("postgresql://", "postgresql+asyncpg://", 1)
        executor = (
            KubernetesExecutor([])
            if c.executor == "kubernetes"
            else ProcessExecutor(c.env.home_dir)
        )
        # ================= 【商业版】 =================
        get_tenant_id = empty_get_tenant_id
        more_state: Dict[str, Any] = {
            "callback_url": c.callback_url,
            "executor": executor,
        }
        more_router = None
        if c.casdoor.enabled:
            casdoor = Casdoor(c.casdoor)
            get_tenant_id = auth_bearer_token
            more_state["casdoor"] = casdoor
            more_router = APIRouter(prefix="/api")
            more_router.include_router(login_router)
        if c.executor == "kubernetes":
            try:
                assert isinstance(executor, KubernetesExecutor)
                await executor.init()
            except Exception as e:
                get_logger().error(f"Failed to load Kubernetes config: {e}")
        # ================= 【商业版】 =================

        app = create_app(
            pg_dsn=pg_dsn,
            mlflow_url="",  # 商业版不暴露mlflow
            read_only=c.read_only,
            env=c.env,
            get_tenant_id=get_tenant_id,
            more_router=more_router,
            more_state=more_state,
        )

        # Start server
        url = urlsplit("//" + c.addr)
        host, port = url.hostname, url.port
        if host is None or host == "" or host == "localhost":
            host = "127.0.0.1"
        if port is None:
            port = 8080
        log_level = "debug" if c.debug else "info"
        get_logger().info("Starting server at %s:%s", host, port)
        config = uvicorn.Config(app, host=host, port=port, log_level=log_level)
        server = uvicorn.Server(config)
        await server.serve()

    import asyncio

    asyncio.run(_main())


@cli.command()
@common_options
def check(config: str, config_base64: str):
    import os

    """Pre-check the config"""
    config_dict = load_config(config, config_base64)

    from ..configs import Config

    c = Config.model_validate(config_dict)
    click.echo(f"Config format check. {click.style('Passed.', fg='green')}")

    # =================
    # check the connection to the redis server
    # =================
    from redis import Redis
    from redis.exceptions import AuthenticationError, ConnectionError

    try:
        redis = Redis(
            host=c.env.redis.server,
            port=c.env.redis.port,
            db=c.env.redis.db,
            password=c.env.redis.password,
        )
        redis.ping()
        click.echo(f"Redis connection check. {click.style('Passed.', fg='green')}")
    except AuthenticationError as e:
        click.echo(f"Redis connection check. {click.style('Failed:', fg='red')} {e}")
        click.echo(
            f"Explanation: Please check the password of the redis server. Current password: {c.env.redis.password}"
        )
    except ConnectionError as e:
        click.echo(f"Redis connection check. {click.style('Failed:', fg='red')} {e}")
        error_msg = str(e)
        if (
            "Temporary failure in name resolution" in error_msg
            or "Name or service not known" in error_msg
        ):
            click.echo(
                f"Explanation: The `server` (value={c.env.redis.server}) in the config is an invalid hostname. Please check the config. Maybe you should use `localhost` or `127.0.0.1` instead if you are running the simulation on a single machine (used to run docker compose)."
            )
        else:
            click.echo(
                f"Explanation: Please check the `server` (value={c.env.redis.server}) and `port` (value={c.env.redis.port}) of the redis server."
            )
    except Exception as e:
        click.echo(f"Redis connection check. {click.style('Failed:', fg='red')} {e}")

    # =================
    # check the connection to the pgsql server
    # =================
    from psycopg import connect
    from psycopg.errors import OperationalError

    try:
        conn = connect(
            conninfo=c.env.pgsql.dsn,
            autocommit=True,
        )
        conn.execute("SELECT 1")
        click.echo(f"Pgsql connection check. {click.style('Passed.', fg='green')}")
    except OperationalError as e:
        click.echo(f"Pgsql connection check. {click.style('Failed:', fg='red')} {e}")
        click.echo(
            f"Explanation: Please check the `dsn` (value={c.env.pgsql.dsn}) of the pgsql server. The format of `dsn` is `postgresql://<username>:<password>@<host>:<port>/<database_name>`. The item wrapped in `<>` should be replaced with the actual values."
        )
        error_msg = str(e)
        if "password authentication failed" in error_msg:
            click.echo(
                f"Explanation: The username or password of the pgsql server is incorrect."
            )
        elif "Temporary failure in name resolution" in error_msg:
            click.echo(
                f"Explanation: The host of the pgsql server is invalid. Maybe you should use `localhost` or `127.0.0.1` instead if you are running the simulation on a single machine (used to run docker compose)."
            )
        elif "Connection refused" in error_msg:
            click.echo(
                f"Explanation: The host or port of the pgsql server is incorrect."
            )
    except Exception as e:
        click.echo(f"Pgsql connection check. {click.style('Failed:', fg='red')} {e}")

    # =================
    # check the connection to the mlflow server
    # =================
    from mlflow import MlflowClient
    from mlflow.exceptions import MlflowException

    if c.env.mlflow.enabled:
        try:
            if c.env.mlflow.username is not None:
                os.environ["MLFLOW_TRACKING_USERNAME"] = c.env.mlflow.username
            if c.env.mlflow.password is not None:
                os.environ["MLFLOW_TRACKING_PASSWORD"] = c.env.mlflow.password
            os.environ["MLFLOW_HTTP_REQUEST_MAX_RETRIES"] = "1"
            os.environ["MLFLOW_HTTP_REQUEST_TIMEOUT"] = "5"
            client = MlflowClient(c.env.mlflow.mlflow_uri)
            client.get_experiment_by_name(c.exp.name)
            click.echo(f"Mlflow connection check. {click.style('Passed.', fg='green')}")
        except MlflowException as e:
            click.echo(
                f"Mlflow connection check. {click.style('Failed:', fg='red')} {e}"
            )
            error_msg = str(e)
            if e.get_http_status_code() == 401:
                click.echo(
                    f"Explanation: The `username` (value={c.env.mlflow.username}) or `password` (value={c.env.mlflow.password}) of the mlflow server is incorrect."
                )
            else:
                click.echo(
                    f"Explanation: Please check the `mlflow_uri` (value={c.env.mlflow.mlflow_uri}) of the mlflow server. The format of `mlflow_uri` is `http://<host>:<port>` or `https://<host>:<port>`. The item wrapped in `<>` should be replaced with the actual values."
                )
                if "Temporary failure in name resolution" in error_msg:
                    click.echo(
                        f"Explanation: The host of the mlflow server is invalid. Maybe you should use `localhost` or `127.0.0.1` instead if you are running the simulation on a single machine (used to run docker compose)."
                    )
                elif "Connection refused" in error_msg:
                    click.echo(
                        f"Explanation: The host or port of the mlflow server is incorrect."
                    )
                else:
                    click.echo(
                        f"Explanation: Please check the `mlflow_uri` (value={c.env.mlflow.mlflow_uri}) of the mlflow server."
                    )
        except Exception as e:
            click.echo(
                f"Mlflow connection check. {click.style('Failed:', fg='red')} {e}"
            )

    # =================
    # check whether the map file exists
    # =================
    if not os.path.exists(c.map.file_path):
        click.echo(
            f"Map file {c.map.file_path} does not exist. {click.style('Failed.', fg='red')}"
        )
        return
    click.echo(f"Map file. {click.style('Passed.', fg='green')}")


@cli.command()
@common_options
@click.option("--tenant-id", default="default", help="Specify tenant ID")
@click.option("--callback-url", help="Specify callback URL (POST)")
def run(
    config: str,
    config_base64: str,
    tenant_id: str,
    callback_url: str = "",
):
    """Run the simulation"""
    config_dict = load_config(config, config_base64)

    import requests
    from ..configs import Config
    from ..simulation import AgentSociety
    from ..cityagent import default

    c = Config.model_validate(config_dict)
    c = default(c)

    # Check if we need to import community modules
    need_community = False
    if c.agents.citizens:
        for citizen in c.agents.citizens:
            if isinstance(citizen.agent_class, str):
                need_community = True
                break

    if c.agents.supervisor is not None and isinstance(
        c.agents.supervisor.agent_class, str
    ):
        need_community = True

    if c.exp.workflow:
        for step in c.exp.workflow:
            if step.func is not None and isinstance(step.func, str):
                need_community = True
                break

    if need_community:
        try:
            from agentsociety_community.agents import citizens, supervisors
            from agentsociety_community.workflows import functions as workflow_functions

            # 获取映射字典
            workflow_function_map = workflow_functions.get_type_to_cls_dict()
            citizens_class_map = citizens.get_type_to_cls_dict()
            supervisors_class_map = supervisors.get_type_to_cls_dict()

            # 处理citizens中的agent_class
            for citizen in c.agents.citizens:
                if isinstance(citizen.agent_class, str):
                    citizen.agent_class = citizens_class_map[citizen.agent_class]()

            # 处理supervisor中的agent_class
            if c.agents.supervisor is not None and isinstance(
                c.agents.supervisor.agent_class, str
            ):
                c.agents.supervisor.agent_class = supervisors_class_map[
                    c.agents.supervisor.agent_class
                ]()

            # 遍历workflow中的每个步骤
            for step in c.exp.workflow:
                if step.func is not None and isinstance(step.func, str):
                    # 如果func是字符串，尝试从function_map中获取对应的函数
                    imported_func = workflow_function_map[step.func]()  # 获取实际函数
                    step.func = imported_func  # 替换为导入的函数
        except ImportError as e:
            import traceback

            print(traceback.format_exc())
            print(
                "agentsociety_community is not installed. Please install it with `pip install agentsociety-community`"
            )
            raise e

    society = AgentSociety(c, tenant_id)

    async def _run():
        try:
            await society.init()
            await society.run()
        finally:
            await society.close()
            if callback_url:
                requests.post(callback_url)

    import asyncio

    asyncio.run(_run())


if __name__ == "__main__":
    cli()
