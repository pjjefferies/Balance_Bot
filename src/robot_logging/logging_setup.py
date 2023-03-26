#!/usr/bin/env python3
"""Logging Set-up for For Balance Bot General Reference"""

import logging

from config.config_logging import log_cfg

bb_logger_format = log_cfg.format.simple
# bb_log_format = logging.Formatter("{asctime} {levelname:>8} {pathname[-20]:>20} {lineno:3}:{msg}", datefmt="%Y-%m-%d %H:%M:%S")
logging.basicConfig(format=bb_logger_format)

bb_logger: logging.Logger = logging.getLogger("Balance Bot Logger")
bb_logger.setLevel(level=logging.DEBUG)


# Set-up console logger to sys.err
ch = logging.StreamHandler()
ch.setLevel(level=logging.DEBUG)
ch.setFormatter(fmt=bb_logger_format)
bb_logger.addHandler(hdlr=ch)

# Set-up file logging
fh = logging.FileHandler(filename=log_cfg.handler.log_file.filename)
fh.setLevel(level=logging.DEBUG)
fh.setFormatter(fmt=bb_logger_format)
bb_logger.addHandler(hdlr=fh)
