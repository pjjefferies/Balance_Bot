#! /usr/bin/python3

import time
from typing import Callable, Tuple, List  # , Protocol - V3.10
import robot_listener

# from config import cfg
from gpiozero import Motor
from motor_battery_relay import MotorBatteryRelay
import bluedot_direction_control
from config import cfg
from event import EventHandler
from encoder_sensor_digital import EncoderDigital

"""
Not needed until Python V3.10 can be implemented on Raspberry Pi. As of Dec. 2022, dbus package does
not work with 32-bit Linux (e.g. Raspberry Pi).

class MotorGeneral:  # (Protocol): - V3.10
    def __init__(
        self,
        forward: Union[int, None] = None,
        backward: Union[int, None] = None,
        enable: Union[int, None] = None,
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


class EncoderGeneral:  # (Protocol): - V3.10
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


class BBAbsoluteSensorGeneral:  # (Protocol): - V3.10
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
    def accel(self) -> Dict[str, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def magnetic_bb(self) -> Dict[str, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def gyro_bb(self) -> Dict[str, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def euler_angles(self) -> Dict[str, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def gravity_dir(self) -> Dict[str, float]:
        raise NotImplementedError

    @property
    @abstractmethod
    def gravity_mag(self) -> float:
        raise NotImplementedError
"""


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
        enc_wheel_left: EncoderDigital,
        enc_wheel_right: EncoderDigital,
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

    def drive_program(self, steps: List[Tuple[int, int, int]]) -> None:
        """
        a step is a tuple of:
            (duration (sec.),
            forward speed or angle (-1 to +1),
            right turn speed or angle (-1 to +1))
        """

        for step in steps:
            if (
                not isinstance(step, tuple)
                or len(step) != 3
                or not (isinstance(step[0], int))
                or not (isinstance(step[1], int))
                or not (isinstance(step[1], int))
            ):
                continue
            duration, fwd_rwd, right_left = step

            left_motor_setting = max(min(fwd_rws - right_left, 1), -1)
            right_motor_setting = max(min(fwd_rws + right_left, 1), -1)

            self._self._motor_wheel_relay.on()
            start_time: int = TIME_S
            self._motor_wheel_left = left_motor_setting
            self._motor_wheel_right = right_motor_setting
            while (TIME_S - start_time) < step[0]:
                time.sleep(1)
            self._motor_wheel_left = 0
            self._motor_wheel_right = 0


def main():
    eh = EventHandler()

    robot_listener.setup_robot_movement_handler()
    robot_listener.setup_robot_encoder_sensor_handler()
    robot_listener.setup_robot_9DOF_sensor_handler()
    robot_listener.setup_general_logging_handler()
    robot_listener.setup_bluedot_handler()
    robot_listener.setup_power_handler()

    print(f"cfg.wheel.left.motor.fwd: {cfg.wheel.left.motor.fwd}")
    print(f"cfg.wheel.left.motor.rwd: {cfg.wheel.left.motor.rwd}")

    # set-up Wheel Motor Power Relay
    motor_wheel_relay: MotorBatteryRelay = MotorBatteryRelay(cfg.wheel.power)

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

    # Set-up Motor Encoders
    enc_wheel_left: EncoderDigital = EncoderDigital(
        signal_pin=cfg.wheel.left.encoder, motor=motor_wheel_left, eh=eh
    )
    enc_wheel_right: EncoderDigital = EncoderDigital(
        signal_pin=cfg.wheel.right.encoder, motor=motor_wheel_left, eh=eh
    )
    # enc_arm_left: EncoderGeneral = EncoderDigital(
    #     signal_pin=cfg.arm.left.encoder
    # )
    # enc_arm_right: EncoderGeneral = EncoderDigital(
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

    robot.drive_two_wheel_robot_by_bd(duration=10)


if __name__ == "__main__":
    main()
