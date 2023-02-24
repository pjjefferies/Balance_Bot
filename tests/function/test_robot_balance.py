#!/usr/bin/env python3

from abc import abstractmethod
import time
from typing import Awaitable, Callable, Optional, Protocol

import board
from box import Box
import busio


from balance_bot import bb_bno055_sensor as bno055
from balance_bot.config_main import load_config
from balance_bot.event import EventHandler
from balance_bot.motor_battery_relay import MotorBatteryRelay
from balance_bot.rpi_motor import RPI_Motor
from balance_bot import robot_listener


class MotorGeneral(Protocol):
    def __init__(
        self,
        forward: Optional[int] = None,
        backward: Optional[int] = None,
        enable: Optional[int] = None,
        pwm: bool = True,
        pin_factory: None = None,
    ):
        raise NotImplementedError

    @property
    def value(self) -> float:
        raise NotImplementedError

    @value.setter
    def value(self, value: float) -> None:
        raise NotImplementedError


class BBAbsoluteSensorGeneral(Protocol):
    def __init__(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def calibrate_sensor(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def temperature(self, units: str) -> float:
        raise NotImplementedError

    @property
    @abstractmethod
    def accel(self) -> dict[str, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def magnetic_bb(self) -> dict[str, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def gyro_bb(self) -> dict[str, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def euler_angles(self) -> dict[str, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def gravity_dir(self) -> dict[str, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def gravity_mag(self) -> float:
        raise NotImplementedError


TIME_MS: Callable[[], int] = lambda: int(time.time() * 1000)
TIME_S: Callable[[], int] = lambda: int(time.time())


def test_robot_balance():
    """
    Basic Robot Balance Test
    """
    cfg: Box = load_config()
    eh = EventHandler()

    robot_listener.setup_robot_movement_handler(eh=eh)
    robot_listener.setup_robot_9DOF_sensor_handler_logfile(eh=eh)
    robot_listener.setup_general_logging_handler(eh=eh)
    robot_listener.setup_power_handler(eh=eh)

    # set-up Wheel Motor Power Relay
    motor_power_relay = MotorBatteryRelay(gpio_pin_no=cfg.wheel.power, eh=eh)

    # Set-up Wheel Motor Control Pins
    motor_wheel_left: RPI_Motor = RPI_Motor(
        forward=cfg.wheel.left.motor.fwd,
        backward=cfg.wheel.left.motor.rwd,
        pwm=True,
        eh=eh,
    )
    motor_wheel_right: RPI_Motor = RPI_Motor(
        forward=cfg.wheel.right.motor.fwd,
        backward=cfg.wheel.right.motor.rwd,
        pwm=True,
        eh=eh,
    )

    # Initialize i2C Connection to sensor
    # TODO: need check/try?
    i2c = busio.I2C(board.SCL, board.SDA)
    sensor: bno055.BB_BNO055Sensor_I2C = bno055.BB_BNO055Sensor_I2C(i2c=i2c, eh=eh)

    # Read Sensor Mode to verify connected
    sensor.mode

    # Calibrate Sensor
    sensor.calibrate_sensor()

    # Start Balance Loop
    eh.post(event_type="log", message="about to start Balance Loop")
    main_control_loop: Callable[[int], Awaitable[None]] = asyncio.get_event_loop()
    tasks = [main_control_loop.create_task(primary_balance_loop())]
    main_control_loop.run_until_complete(asyncio.wait(tasks))

    main_control_loop.close()
    motor_wheel_left.value = 0
    motor_wheel_right.value = 0
    motor_wheel_left.close()
    motor_wheel_right.close()
    motor_power_relay.off()
    motor_power_relay.close()

    async def primary_balance_loop() -> None:
        cfg: Box = load_config()
        motor_power_relay.on()
        eh.post(event_type="log", message="Main loop started")
        # Get Initial Values for PID Filter Initialization
        temp_euler: dict[str, float] = sensor.euler_angles
        roll_last: float = temp_euler["x"]
        pitch_last: float = temp_euler["y"]
        yaw_last: float = temp_euler["z"]

        # Set initial instructions to stand still
        pitch_setpoint_angle: float = 0
        # yaw_setpoint_angle: float = 0
        # previous_fore_aft_motor_input: float = 0

        # Set initial integral sum for PID control to zero
        integral_term: float = 0
        lasttime_control = 0
        lasttime_params_updated = TIME_S()
        roll: float
        pitch: float
        yaw: float
        while True:
            if (TIME_MS() - lasttime_control) >= cfg.duration.control_update:
                # exec every CONTROL_UPDATE_INTERVAL msec.
                lasttime_control = TIME_S()
                temp_euler = sensor.euler_angles
                roll = temp_euler["x"]
                pitch = temp_euler["y"]
                yaw = temp_euler["z"]
                fore_aft_error = pitch_setpoint_angle - pitch
                integral_term += cfg.pid_param.k_integral * fore_aft_error
                # self._integral_term = max(self._integral_term, bbc.MOTOR_MIN)
                # self._integral_term = min(self._integral_term, bbc.MOTOR_MAX)
                derivative_term = cfg.pid_param.k_derivative * (pitch - pitch_last)
                proportional_term = cfg.pid_param.k_proportional * fore_aft_error
                motor_output = proportional_term + integral_term + derivative_term

                motor_left_output = motor_output
                motor_left_output = max(motor_left_output, cfg.wheel.left.motor.min)
                motor_left_output = min(motor_left_output, cfg.wheel.left.motor.max)
                motor_right_output = motor_output
                motor_right_output = max(motor_right_output, cfg.wheel.right.motor.min)
                motor_right_output = min(motor_right_output, cfg.wheel.right.motor.max)

                motor_wheel_left.value = motor_left_output
                motor_wheel_right.value = motor_right_output

                roll_last, pitch_last, yaw_last = (roll, pitch, yaw)
                eh.post(event_type="log", message="Main loop ended")
            if (TIME_S() - lasttime_params_updated) >= cfg.duration.params_update:
                # exec every PARAMS_UPDATE_INTERVAL msec.
                lasttime_params_updated = TIME_S()
                eh.post(event_type="log", message="Updating parameters?")
                cfg = load_config()


if __name__ == "__main__":
    test_robot_balance()