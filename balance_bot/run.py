#! /usr/bin/python3
"""
run.py
"""

import click
import logging

from balance_bot.balance_bot import main as balance_bot_main
from balance_bot.simple_robot import main as simple_robot_main
from tests.function.test_encoder_sensor_with_motor import main as test_enc_mot_main
from tests.function.test_py_motor import main as test_py_motor_main
from tests.function.test_BNO055_sensor import main as test_BNO055_sensor_main

logger = logging.getLogger(__name__)

tasks = {
    'balance_bot': balance_bot_main,
    'simple_robot': simple_robot_main,
    'test_encoder_with_motor': test_enc_mot_main,
    'motor_test': test_py_motor_main,
    'sensor_test': test_BNO055_sensor_main
}


def main(task):
    try:
        tasks[task]()
    except:
        logger.error(f"Task {task} failed")
        raise


@click.command()
@click.option(
    "--task",
    type=click.Choice(tasks.keys()),
    required=True,
    help="Name of task to execute",
)
def main_cli(task):
    main(task)