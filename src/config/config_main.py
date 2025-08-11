"""
Balance Bot Package config.py module.

Loads General Program configuration as cfg, boxed.
"""

from typing import Any

import yaml
from box import Box

CONFIG_LOC: str = "configs/balance_bot_config.yaml"
env = "dev"

def load_config() -> Box:
    with open(CONFIG_LOC, "r") as ymlfile:
        full_cfg: dict[str, Any] = yaml.safe_load(ymlfile)

    cfg: Box = Box(
        {**full_cfg["base"], **full_cfg[env]}, default_box=True, default_box_attr=None
    )

    return cfg

cfg:Box = load_config()
