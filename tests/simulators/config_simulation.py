#!/usr/bin/env python3
"""
Balance Bot Package config.py module.

Loads General Program configuration as cfg, boxed.
Loads logging YMAL config file and configues logger.
Loads BNO055 Sensor configuration if available
"""

from box import Box
import yaml

env = "dev"

# Import Simulation Configuration if available
with open(
    r"/home/pi/Balance_Bot/configs/balance_bot_simulator_config.yml", "r"
) as ymlfile:
    full_sim_cfg: dict[str, dict[str, str]] = yaml.safe_load(ymlfile)

cfg_sim: Box = Box(
    {**full_sim_cfg["base"], **full_sim_cfg[env]},
    default_box=True,
    default_box_attr=None,
)
