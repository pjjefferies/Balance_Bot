#! /usr/bin/python3
"""
Balance Bot Package config.py module.

Loads General Program configuration as cfg, boxed.
Loads logging YMAL config file and configues logger.
Loads BNO055 Sensor configuration if available
"""

from box import Box
from typing import Dict
import os
import yaml

from .event import EventHandler

eh = EventHandler()


# env = os.environ['ENVIRONMENT']
env = "dev"

with open(r"/home/pi/Balance_Bot/configs/balance_bot_config.yml", "r") as ymlfile:
    full_cfg: Dict[str, Dict[str, str]] = yaml.safe_load(ymlfile)

cfg: Box = Box(
    {**full_cfg["base"], **full_cfg[env]}, default_box=True, default_box_attr=None
)

# Set-up and import logging config
os.makedirs(cfg.path.logs, exist_ok=True)

if os.path.exists(cfg.path.log_config):
    with open(cfg.path.log_config, "r") as ymlfile:
        log_config_dict: Dict[str, Dict[str, str]] = yaml.safe_load(ymlfile)

    # Set up the logger configuration
    log_cfg: Box = Box(
        {**log_config_dict["base"]}, default_box=True, default_box_attr=None
    )
else:
    raise FileNotFoundError(
        f"Log yaml configuration file not found in {cfg.path.log_config}"
    )

# Import Simulation Configuration if available
with open(r"configs/balance_bot_simulator_config.yml", "r") as ymlfile:
    full_sim_cfg: Dict[str, Dict[str, str]] = yaml.safe_load(ymlfile)

cfg_sim: Box = Box(
    {**full_sim_cfg["base"], **full_sim_cfg[env]},
    default_box=True,
    default_box_attr=None,
)
