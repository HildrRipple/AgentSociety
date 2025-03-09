from __future__ import annotations

from typing import TYPE_CHECKING, Any, TypeVar

import yaml

if TYPE_CHECKING:
    from .exp_config import ExpConfig
    from .sim_config import SimConfig
T = TypeVar("T", "SimConfig", "ExpConfig")


def load_config_from_file(filepath: str, config_type: type[T]) -> T:
    print("new function2")
    with open(filepath, "r") as file:
        data = yaml.safe_load(file)
    return config_type(**data)
