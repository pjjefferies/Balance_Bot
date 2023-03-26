#!/usr/bin/env python3

import datetime as dt
import os
from typing import Any

import numpy as np
import numpy.typing as npt

from src.config.config_logging import log_cfg


# Position History Event Handler
def save_position_history(pos_history: npt.ArrayLike) -> None:
    now = dt.datetime.now()
    log_folder = log_cfg.handler["position_history_file"].folder
    log_filename = (
        f"{now:%Y-%m-%d_%H_%M_%S}_{log_cfg.handler['position_history_file'].filename}"
    )
    log_filename_path = os.path.join(log_folder, log_filename)
    np.savetxt(fname=log_filename_path, X=pos_history, fmt="%.7f", delimiter=",")
