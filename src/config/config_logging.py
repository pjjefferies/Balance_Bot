"""
Loads logging YMAL config file and configues logger.
"""

import os

import yaml
from box import Box

from src.config.config_main import cfg

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
