#! /usr/bin/python3

import time
from typing import Protocol, Callable
from abc import abstractmethod
import robot_listener

# from config import cfg
from gpiozero import Motor
import bluedot_direction_control
from config import cfg
from event import EventHandler
from encoder_sensor_digital import RotationEncoder


class MotorGeneral(Protocol):
    def __init__(
        self,
    ):
        raise NotImplementedError

    @property
    def value(self) -> float:
        raise NotImplementedError

    @value.setter
    def value(self, value: float) -> None:
        raise NotImplementedError


class EncoderGeneral(Protocol):
    def __init__(
        self,
        *,
        max_no_position_points: int,
        average_duration: int,
        motor: MotorGeneral,
        eh: EventHandler,
    ):
        raise NotImplementedError

    @property
    def distance(self) -> float:
        raise NotImplementedError

    @property
    def jerk(self) -> float:
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


class SimpleRobot:
    """
    Basic Robot Manual control for 2-Motor Simple Robot
    """

    def __init__(
        self,
        *,
        motor_wheel_left: MotorGeneral,
        motor_wheel_right: MotorGeneral,
        # motor_arm_left: MotorGeneral | None,
        # motor_arm_right: MotorGeneral | None,
        enc_wheel_left: EncoderGeneral,
        enc_wheel_right: EncoderGeneral,
        # enc_arm_left: EncoderGeneral | None,
        # enc_arm_right: EncoderGeneral | None,
        # sensor9DOF: BBAbsoluteSensorGeneral,
        # start_prog: tuple[tuple[float, float, float]] | None = None,
        # repeat_prog: tuple[tuple[float, float, float]] | None = None,
        # manual_control_time: int = 0,  # Duration of manual control in seconds
        bluedot_control: bluedot_direction_control.BlueDotRobotController,
        eh: EventHandler,
    ):
        """
        Initialize Simple Robot using values in balance_bot_config

        Args:
            None

        Returns:
            None.

        """
        self._motor_wheel_left = motor_wheel_left
        self._motor_wheel_right = motor_wheel_right
        self._enc_wheel_left = enc_wheel_left
        self._enc_wheel_right = enc_wheel_right
        self._bluedot_control = bluedot_control
        self._eh = eh

        # self._bd_ctl = bluedot_direction_control.bd_drive

    def drive_two_wheel_robot_by_bd(
        self, interval: int = 500, duration: int = 60
    ) -> None:
        """
        Simple driving method for two wheeled robot

        Args:
            interval: number of milliseconds between checking for BlueDot input
            duration: number of seconds to run robot for, 0 = forever

        Returns:
            None.

        """
        if duration == 0:
            duration = 1_000_000_000
        start_time: int = TIME_S()

        lasttime: int = 0
        self._bluedot_control.start()
        direction: tuple[float, float]

        while TIME_S() - start_time < duration:
            if (TIME_MS() - lasttime) >= interval:
                lasttime = TIME_MS()
                direction = (
                    self._bluedot_control.bd_drive()
                )  # [y, x] eached scaled [-1, 1]
                self._eh.post(
                    event_type="robot moved",
                    message=f"Direction: x: {direction[0]:.2f}, y: {direction[1]:.2f}",
                )
                if direction == (0, 0):
                    self._motor_wheel_left.value = 0
                    self._motor_wheel_right.value = 0
                else:
                    fwd_vel = direction[0]
                    right_turn = direction[1]
                    if abs(right_turn) < 0.2:
                        right_turn = 0
                    self._motor_wheel_left.value = max(min(fwd_vel + right_turn, 1), -1)
                    self._motor_wheel_right.value = max(
                        min(fwd_vel - right_turn, 1), -1
                    )
            self._eh.post(event_type="robot encoder sensor", message="Left Wheel:")
            self._enc_wheel_left.distance  # trigger posting of distance
            self._enc_wheel_left.jerk
            self._eh.post(event_type="robot encoder sensor", message="Right Wheel:")
            self._enc_wheel_right.distance  # trigger posting of distance
            self._enc_wheel_right.jerk
            time.sleep(interval / 5)


def main():
    eh = EventHandler()

    robot_listener.setup_robot_movement_handler()
    robot_listener.setup_robot_encoder_sensor_handler()
    robot_listener.setup_robot_9DOF_sensor_handler()
    robot_listener.setup_general_logging_handler()
    robot_listener.setup_bluedot_handler()

    # Set-up Motor Control Pins
    motor_wheel_left: MotorGeneral = Motor(
        forward=cfg.wheel.left.motor.fwd,
        backward=cfg.wheel.left.motor.rwd,
        pwm=True,
    )
    motor_wheel_right: MotorGeneral = Motor(
        forward=cfg.wheel.right.motor.fwd,
        backward=cfg.wheel.right.motor.rwd,
        pwm=True,
    )

    # Set-up Motor Encoders
    enc_wheel_left: EncoderGeneral = RotationEncoder(signal_pin=cfg.wheel.left.encoder)
    enc_wheel_right: EncoderGeneral = RotationEncoder(
        signal_pin=cfg.wheel.right.encoder
    )
    # enc_arm_left: EncoderGeneral = RotationEncoder(
    #     signal_pin=cfg.arm.left.encoder
    # )
    # enc_arm_right: EncoderGeneral = RotationEncoder(
    #     signal_pin=cfg.arm.right.encoder
    # )

    bd_ctl: bluedot_direction_control.BlueDotRobotController = (
        bluedot_direction_control.BlueDotRobotController(eh=eh)
    )

    robot = SimpleRobot(
        motor_wheel_left=motor_wheel_left,
        motor_wheel_right=motor_wheel_right,
        enc_wheel_left=enc_wheel_left,
        enc_wheel_right=enc_wheel_right,
        bluedot_control=bd_ctl,
        eh=eh,
    )

    robot.drive_two_wheel_robot_by_bd()


if __name__ == "__main__":
    main()
