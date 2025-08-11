#!/usr/bin/env python3

import time
from typing import Callable, Optional, Protocol

from gpiozero import Motor

from bluedot.bluedot_direction_control import BlueDotRobotController
from config.config_main import cfg
from motor.motor_battery_relay import MotorBatteryRelay


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


class SimpleRobot:
    """
    Basic Robot Manual control for 2-Motor Simple Robot
    """

    def __init__(
        self,
        *,
        motor_wheel_left: Motor,
        motor_wheel_right: Motor,
        motor_wheel_relay: MotorBatteryRelay,
        # motor_arm_left: MotorGeneral | None,
        # motor_arm_right: MotorGeneral | None,
        # arm_motor_relay: MotorBatteryRelay,
        # sensor9DOF: BBAbsoluteSensorGeneral,
        # start_prog: tuple[tuple[float, float, float]] | None = None,
        # repeat_prog: tuple[tuple[float, float, float]] | None = None,
        # manual_control_time: int = 0,  # Duration of manual control in seconds
        bluedot_control: BlueDotRobotController,
    ):
        """
        Initialize Simple Robot using values in balance_bot_config

        Args:
            TBD
            a step is a tuple of:
                    (duration (sec.),
                     forward speed or angle (-1 to +1),
                     right turn speed or angle (-1 to +1))

        Returns:
            None.

        """
        self._motor_wheel_left = motor_wheel_left
        self._motor_wheel_right = motor_wheel_right
        self._motor_wheel_relay = motor_wheel_relay
        self._bluedot_control = bluedot_control

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
                # self._eh.post(
                #     event_type="robot moved",
                #     message=f"Direction: x: {direction[0]:.2f}, y: {direction[1]:.2f}",
                # )
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
            # self._eh.post(event_type="robot encoder sensor", message="Left Wheel:")
            # _ = self._enc_wheel_left.distance  # trigger posting of distance
            # _ = self._enc_wheel_left.jerk
            # self._eh.post(event_type="robot encoder sensor", message="Right Wheel:")
            # _ = self._enc_wheel_right.distance  # trigger posting of distance
            # _ = self._enc_wheel_right.jerk
            # time.sleep(interval / 5)

    def drive_program(self, steps: list[tuple[int, int, int]]) -> None:
        """
        a step is a tuple of:
            (duration (sec.),
            forward speed or angle (-1 to +1),
            right turn speed or angle (-1 to +1))
        """

        for step in steps:
            """
            if (
                not isinstance(step, tuple)
                or len(step) != 3
                or not (isinstance(step[0], int))
                or not (isinstance(step[1], int))
                or not (isinstance(step[1], int))
            ):
                continue
            """
            duration, fwd_rwd, right_left = step

            left_motor_setting = max(min(fwd_rwd - right_left, 1), -1)
            right_motor_setting = max(min(fwd_rwd + right_left, 1), -1)

            self._motor_wheel_relay.on()
            start_time: int = TIME_S()
            self._motor_wheel_left = left_motor_setting
            self._motor_wheel_right = right_motor_setting
            while (TIME_S() - start_time) < duration:
                time.sleep(1)
            self._motor_wheel_left = 0
            self._motor_wheel_right = 0


def main():

    # print(f"cfg.wheel.left.motor.fwd: {cfg.wheel.left.motor.fwd}")
    # print(f"cfg.wheel.left.motor.rwd: {cfg.wheel.left.motor.rwd}")

    # set-up Wheel Motor Power Relay
    motor_wheel_relay = MotorBatteryRelay(cfg.wheel.power)

    # Set-up Wheel Motor Control Pins
    motor_wheel_left: Motor = Motor(  # MotorGeneral = Motor(  - V3.10
        forward=cfg.wheel.left.motor.fwd,
        backward=cfg.wheel.left.motor.rwd,
        pwm=True,
    )
    motor_wheel_right: Motor = Motor(  # MotorGeneral = Motor(  - V3.10
        forward=cfg.wheel.right.motor.fwd,
        backward=cfg.wheel.right.motor.rwd,
        pwm=True,
    )

    """
    #set-up Arm Motor Power Relay
    motor_arm_relay:MotorBatteryRelay = MotorBatteryRelay(cfg.arm.power)

    # Set-up Arm Motor Control Pins
    motor_arm_left: Motor = Motor(  # MotorGeneral = Motor(  - V3.10
        forward=cfg.arm.left.motor.fwd,
        backward=cfg.arm.left.motor.rwd,
        pwm=True,
    )
    motor_arm_right: Motor = Motor(  # MotorGeneral = Motor(  - V3.10
        forward=cfg.arm.right.motor.fwd,
        backward=cfg.arm.right.motor.rwd,
        pwm=True,
    )
    """

    bd_ctl = BlueDotRobotController()

    robot = SimpleRobot(
        motor_wheel_left=motor_wheel_left,
        motor_wheel_right=motor_wheel_right,
        motor_wheel_relay=motor_wheel_relay,
        bluedot_control=bd_ctl,
    )

    # robot.drive_two_wheel_robot_by_bd(duration=10)

    steps = [(5, 1, 0), (5, -1, 0), (5, 0, 1), (5, 0, -1)]
    robot.drive_program(steps=steps)


if __name__ == "__main__":
    main()
