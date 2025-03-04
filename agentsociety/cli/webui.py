import logging
from pathlib import Path
from typing import Dict
from urllib.parse import urlparse

import click
import uvicorn
import yaml
from dotenv import load_dotenv

from ..webapi.app import create_app

load_dotenv()


def _load_config(ctx: click.Context, param: click.Parameter, value: str) -> Dict:
    """Load config from file"""
    config = {}
    if value:
        config_path = Path(value)
    else:
        config_path = Path("config.yaml")

    if config_path.exists():
        with open(config_path) as f:
            config = yaml.safe_load(f)
    return config


CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option(
    "--config",
    type=click.Path(),
    callback=_load_config,
    is_eager=True,
    help="Config file",
)
@click.option("--pg-dsn", envvar="PG_DSN", help="PostgreSQL DSN")
@click.option("--mqtt-broker", envvar="MQTT_BROKER", help="MQTT Broker Address")
@click.option("--mqtt-username", envvar="MQTT_USERNAME", help="MQTT Username")
@click.option("--mqtt-password", envvar="MQTT_PASSWORD", help="MQTT Password")
@click.option("--addr", envvar="ADDR", default=":8080", help="Server address")
@click.option("--mlflow-url", envvar="MLFLOW_URL", help="MLFlow URL")
@click.option("--read-only", is_flag=True, envvar="READ_ONLY", help="Read-only mode")
@click.option("--debug", is_flag=True, envvar="DEBUG", help="Debug mode")
def cli(
    config,
    pg_dsn,
    mqtt_broker,
    mqtt_username,
    mqtt_password,
    addr,
    mlflow_url,
    read_only,
    debug,
):
    """AgentSociety WebUI"""

    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
    )

    # Config Order: Command Line > Environment Variable > Config File > Default Value
    final_config = {
        "pg_dsn": pg_dsn or config.get("pg_dsn", ""),
        "mqtt_broker": mqtt_broker or config.get("mqtt_broker", ""),
        "mqtt_username": mqtt_username or config.get("mqtt_username", ""),
        "mqtt_password": mqtt_password or config.get("mqtt_password", ""),
        "addr": addr or config.get("addr", ":8080"),
        "mlflow_url": mlflow_url or config.get("mlflow_url", ""),
        "read_only": read_only or config.get("read_only", False),
        "debug": debug or config.get("debug", False),
    }

    # Show final config
    logging.info("PG_DSN: %s", final_config["pg_dsn"])
    logging.info("MQTT_BROKER: %s", final_config["mqtt_broker"])
    logging.info("MQTT_USERNAME: %s", final_config["mqtt_username"])
    logging.info("MQTT_PASSWORD: %s", final_config["mqtt_password"])
    logging.info("ADDR: %s", final_config["addr"])
    logging.info("MLFLOW_URL: %s", final_config["mlflow_url"])
    logging.info("READ_ONLY: %s", final_config["read_only"])
    logging.info("DEBUG: %s", final_config["debug"])

    # for compatibility with the old config
    # postgres:// in DSN is not supported by SQLAlchemy
    # replace it with postgresql://
    if final_config["pg_dsn"].startswith("postgres://"):
        final_config["pg_dsn"] = final_config["pg_dsn"].replace(
            "postgres://", "postgresql+asyncpg://", 1
        )

    app = create_app(
        pg_dsn=final_config["pg_dsn"],
        mqtt_broker=final_config["mqtt_broker"],
        mqtt_username=final_config["mqtt_username"],
        mqtt_password=final_config["mqtt_password"],
        mlflow_url=final_config["mlflow_url"],
        read_only=final_config["read_only"],
    )

    # Start server
    url = urlparse(final_config["addr"])
    host, port = url.hostname, url.port
    if host is None or host == "" or host == "localhost":
        host = "127.0.0.1"
    if port is None:
        port = 8080
    log_level = "debug" if final_config["debug"] else "info"
    logging.info("Starting server at %s:%s", host, port)
    uvicorn.run(app, host=host, port=port, log_level=log_level)


if __name__ == "__main__":
    # Command line for testing: python3 -m agentsociety.cli.webui
    cli()
