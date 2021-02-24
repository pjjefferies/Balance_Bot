import click
import logging

from balance_bot.balance_bot import main as balance_bot_main
from balance_bot.simple_robot import main as simple_robot_main
from tests.function.encoder_sensor_with_motor_test import main as enc_mot_main
from tests.function.py_motor_test import main as motor_test_main
from tests.function.py_motor_test_auto import main as motor_test_auto_main
from tests.function.sensor_test import main as sensor_test_main


tasks = {
    "balance_bot": balance_bot_main,
    "simple_robot": simple_robot_main,
    "encoder_motor_test": enc_mot_main,
    "motor_test": motor_test_main,
    "motor_test_auto": motor_test_auto,
    "sensor_test": sensor_test_main
}
logger = logging.getLogger(__name__)


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