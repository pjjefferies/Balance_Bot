#!/usr/bin/env python3
"""
Balance Bot Package config.py module.

Loads General Program configuration as cfg, boxed.
Loads logging YMAL config file and configues logger.
Loads BNO055 Sensor configuration if available
"""

from box import Box
import os
import yaml

from balance_bot.config_main import cfg
from balance_bot.event import EventHandler

eh = EventHandler()

env = "dev"

# Set-up and import logging config
os.makedirs(cfg.path.logs, exist_ok=True)

if os.path.exists(cfg.path.log_config):
    with open(cfg.path.log_config, "r") as ymlfile:
        log_config_dict: dict[str, dict[str, str]] = yaml.safe_load(ymlfile)

    # Set up the logger configuration
    log_cfg: Box = Box(
        {**log_config_dict["base"]}, default_box=True, default_box_attr=None
    )
else:
    raise FileNotFoundError(
        f"Log yaml configuration file not found in {cfg.path.log_config}"
    )
