#! /usr/bin/python3
"""
Balance Bot Package config.py module.

Loads General Program configuration as cfg, boxed.
Loads logging YMAL config file and configues logger.
Loads BNO055 Sensor configuration if available
"""

import os
import yaml
from box import Box
import logging.config

# env = os.environ['ENVIRONMENT']
env = "dev"

with open(r"./configs/balance_bot_config.yml", "r") as ymlfile:
    full_cfg = yaml.safe_load(ymlfile)

cfg = Box(
    {**full_cfg["base"], **full_cfg[env]}, default_box=True, default_box_attr=None
)

# Set-up and import logging config
os.makedirs(cfg.path.logs, exist_ok=True)

if os.path.exists(cfg.path.log_config):
    with open(cfg.path.log_config, "r") as ymlfile:
        log_config = yaml.safe_load(ymlfile)

    # Set up the logger configuration
    logging.config.dictConfig(log_config)
else:
    raise FileNotFoundError(
        f"Log yaml configuration file not found in {cfg.path.log_config}"
    )

# Import 9DOF Sensor Configuration if available
if os.path.exists(cfg.path.calibration):
    with open(cfg.path.calibration, "r") as sensor_cfg_file:
        sensor_config = Box(yaml.safe_load(sensor_cfg_file))
else:
    sensor_config = None

# Import Simulation Configuration if available
with open(r"./configs/balance_bot_simulator_config.yml", "r") as ymlfile:
    full_sim_cfg = yaml.safe_load(ymlfile)

cfg_sim = Box(
    {**full_sim_cfg["base"], **full_sim_cfg[env]},
    default_box=True,
    default_box_attr=None,
)
