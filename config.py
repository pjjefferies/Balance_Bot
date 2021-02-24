#! /usr/bin/python3
"""
Balance Bot Package config.py module.

Loads logging YMAL config file and configues logger for use thoughout
application.
"""

import yaml
import logging.config

with open(r'config\bb_logging.yml', "r") as ymlfile:
    log_config = yaml.safe_load(ymlfile)

# Set up the logger configuration
logging.config.dictConfig(log_config)

with open(r'balance_bot\config\balance_bot_config.yml') as ymlfile:
    cfg = yaml.safe_load(ymlfile)
