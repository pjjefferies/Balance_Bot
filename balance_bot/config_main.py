#!/usr/bin/env python3
"""
Balance Bot Package config.py module.

Loads General Program configuration as cfg, boxed.
"""

from box import Box
from typing import Any
import yaml

env = "dev"


def load_config() -> Box:
    with open(r"/home/pi/Balance_Bot/configs/balance_bot_config.yml", "r") as ymlfile:
        full_cfg: dict[str, Any] = yaml.safe_load(ymlfile)

    cfg: Box = Box(
        {**full_cfg["base"], **full_cfg[env]}, default_box=True, default_box_attr=None
    )

    return cfg
