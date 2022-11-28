#! /usr/bin/python3
"""
Balance Bot Main Routine.

Classes:
    BalanceBot

Misc variables:
    TBD
"""

import time
from typing import Callable, Protocol
from abc import abstractmethod
import robot_listener

# from importlib import reload
import asyncio
from config import cfg
from event import EventHandler


class EventHandlerTemplate(Protocol):
    def post(self, *, event_type: str, message: str) -> None:
        raise NotImplementedError


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


class DirectionController(Protocol):
    def __init__(self, eh: EventHandlerTemplate) -> None:
        raise NotImplementedError

    def bd_drive(self) -> tuple[float, float]:
        raise NotImplementedError

    def start(self) -> None:
        raise NotImplementedError

    def stop(self) -> None:
        raise NotImplementedError


class BalanceBot:
    """
    A class to represent the Balance Bot Robot

    Attributes:
        X

    Methods:
        X
    """

    def __init__(
        self,
        *,
        motor_wheel_left: MotorGeneral,
        motor_wheel_right: MotorGeneral,
        motor_arm_left: MotorGeneral | None,
        motor_arm_right: MotorGeneral | None,
        enc_wheel_left: EncoderGeneral,
        enc_wheel_right: EncoderGeneral,
        enc_arm_left: EncoderGeneral | None,
        enc_arm_right: EncoderGeneral | None,
        sensor9DOF: BBAbsoluteSensorGeneral,
        start_prog: tuple[tuple[float, float, float]] | None = None,
        repeat_prog: tuple[tuple[float, float, float]] | None = None,
        manual_control_time: int = 0,  # Duration of manual control in seconds
        bluedot_control: DirectionController | None = None,
        eh: EventHandler,
    ):
        """
        Create Balance Bat Robot Object, initiating all start-up functions

        Args:
            start_prog (list): Sequence of steps to run once.
            repeat_prog (list): Sequence of steps to run repeatedly
                a step is a tuple of:
                    (duration (sec.),
                     forward speed or angle (-1 to +1),
                     right turn speed or angle (-1 to +1))
        Returns:
            Result: True if successful, False if not
        """

        # Set-up Evenet Handler
        self._eh = eh

        # Set-up Motor Control Pins
        self._motor_wheel_left: MotorGeneral = motor_wheel_left
        self._motor_wheel_right: MotorGeneral = motor_wheel_right
        self._motor_arm_left: MotorGeneral | None = motor_arm_left
        self._motor_arm_right: MotorGeneral | None = motor_arm_right
        # Set-up Motor_General Encoders
        self._enc_wheel_left: EncoderGeneral = enc_wheel_left
        self._enc_wheel_right: EncoderGeneral = enc_wheel_right
        self._enc_arm_left: EncoderGeneral | None = enc_arm_left
        self._enc_arm_right: EncoderGeneral | None = enc_arm_right
        # Initialize i2C Connection to sensor- need check/try?
        self._sensor: BBAbsoluteSensorGeneral = sensor9DOF
        # Initialize BlueDot Controller if using
        if bluedot_control is not None and manual_control_time > 0:
            self._bluedot_control: DirectionController | None = bluedot_control
        else:
            self._bluedot_control: DirectionController | None = None

        # Get Initial Values for PID Filter Initialization
        temp_euler: dict[str, float] = self._sensor.euler_angles
        self._roll_last: float = temp_euler["x"]
        self._pitch_last: float = temp_euler["y"]
        self._yaw_last: float = temp_euler["z"]

        # Set initial instructions to stand still
        self.pitch_setpoint_angle: float = 0
        self.yaw_setpoint_angle: float = 0
        self.previous_fore_aft_motor_input: float = 0

        # Set initial integral sum for PID control to zero
        self._integral_term: float = 0

        # Start Balance Loop
        self._eh.post(event_type="log", message="about to start Balance Loop")
        main_control_loop = asyncio.get_event_loop()
        tasks = [main_control_loop.create_task(self._primary_balance_loop())]
        main_control_loop.run_until_complete(asyncio.wait(tasks))

        # Start start_prog if we have one
        self._eh.post(event_type="log", message="Starting Single Run Programs if any")
        if start_prog is not None:
            self._run_repeat_program(a_prog=start_prog)

        # Start repeat_prog if we have one
        self._eh.post(event_type="log", message="Starting Multiple Run Programs if any")
        if repeat_prog is not None:
            while True:
                self._run_repeat_program(a_prog=repeat_prog)

        # Set-up BlueDot Remote Control for manual control
        if self._bluedot_control is not None:
            start_time: float = TIME_S()
            right: float
            fwd: float
            while (TIME_S() - start_time) < manual_control_time:
                right, fwd = self._bluedot_control.bd_drive()
                self.pitch_setpoint_angle = max(-1, min(1, fwd))
                self.yaw_setpoint_angle = max(-1, min(1, right))
            self._bluedot_control.stop()

        main_control_loop.close()

    def _run_repeat_program(self, a_prog: tuple[tuple[float, float, float]]):
        for a_command in a_prog:
            if not isinstance(a_command, list) or len(a_command) != 3:
                self._eh.post(
                    event_type="log",
                    message=f"WARNING: Invalid repeat_prog step, skipping ({a_command})",
                )
                continue
            duration, fwd_rwd, right_left = a_command
            if (
                (duration < 0 or duration > cfg.duration.max_time_step)
                or (fwd_rwd < -1 or fwd_rwd > 1)
                or (right_left < -1 or right_left > 1)
            ):
                self._eh.post(
                    event_type="log",
                    message=f"WARNING: Invalid repeat_prog step, skipping ({a_command})",
                )
                continue
            self.pitch_setpoint_angle = fwd_rwd
            self.yaw_setpoint_angle = right_left
            time.sleep(duration)

    async def _primary_balance_loop(self) -> None:
        self._eh.post(event_type="log", message="Main loop started")
        lasttime_control = 0
        lasttime_params_updated = TIMER_S()
        while True:
            if (time.time() * 1000 - lasttime_control) >= cfg.duration.control_update:
                # exec every CONTROL_UPDATE_INTERVAL msec.
                lasttime_control = TIMER_S()
                temp_euler: dict[str, float] = self._sensor.euler_angles
                self._roll: float = temp_euler["x"]
                self._pitch: float = temp_euler["y"]
                self._yaw: float = temp_euler["z"]
                fore_aft_error = self.pitch_setpoint_angle - self._pitch
                self._integral_term += cfg.pid_param.k_integral * fore_aft_error
                # self._integral_term = max(self._integral_term, bbc.MOTOR_MIN)
                # self._integral_term = min(self._integral_term, bbc.MOTOR_MAX)
                derivative_term = cfg.pid_param.k_derivative * (
                    self._pitch - self._pitch_last
                )
                proportional_term = cfg.pid_param.k_proportional * fore_aft_error
                motor_output = proportional_term + self._integral_term + derivative_term

                motor_left_output = motor_output
                motor_left_output = max(motor_left_output, cfg.wheel.left.motor.min)
                motor_left_output = min(motor_left_output, cfg.wheel.left.motor.max)
                motor_right_output = motor_output
                motor_right_output = max(motor_right_output, cfg.wheel.right.motor.min)
                motor_right_output = min(motor_right_output, cfg.wheel.right.motor.max)

                self._motor_wheel_left.value = motor_left_output
                self._motor_wheel_right.value = motor_right_output

                self._roll_last, self._pitch_last, self._yaw_last = (
                    self._roll,
                    self._pitch,
                    self._yaw,
                )
                self._eh.post(event_type="log", message="Main loop ended")
            if (TIMER_S() - lasttime_params_updated) >= cfg.duration.params_update:
                # exec every PARAMS_UPDATE_INTERVAL msec.
                lasttime_params_updated = TIMER_S()
                self._eh.post(event_type="log", message="Updating parameters?")
                # reload(bbc)


def main():
    import os

    eh = EventHandler()

    robot_listener.setup_robot_movement_handler()
    robot_listener.setup_robot_encoder_sensor_handler()
    robot_listener.setup_robot_9DOF_sensor_handler()
    robot_listener.setup_general_logging_handler()
    robot_listener.setup_bluedot_handler()

    if os.name == "posix" and os.uname()[1] == "raspberrypi":
        # We're running on Raspberry Pi. Start robot.
        logger.info("Starting Balance Bot Robt")
        from gpiozero import Motor
        import board
        import busio
        from bb_bno055_sensor import BB_BNO055Sensor
        from encoder_sensor_digital import EncoderDigital
        import bluedot_direction_control

        motor_wheel_left: Motor_General = Motor(
            forward=cfg.wheel.left.motor.fwd,
            backward=cfg.wheel.left.motor.rwd,
            pwm=True,
        )
        motor_wheel_right: Motor_General = Motor(
            forward=cfg.wheel.right.motor.fwd,
            backward=cfg.wheel.right.motor.rwd,
            pwm=True,
        )
        # motor_arm_left: Motor_General = Motor(
        #     forward=cfg.arm.left.fwd, backward=cfg.arm.left.rwd, pwm=True
        # )
        # motor_arm_right: Motor_General = Motor(
        #     forward=cfg.arm.right.fwd, backward=cfg.arm.right.rwd, pwm=True
        # )

        enc_wheel_left: RotationEncoder = RotationEncoder(
            signal_pin=cfg.wheel.left.encoder
        )
        enc_wheel_right: RotationEncoder = RotationEncoder(
            signal_pin=cfg.wheel.right.encoder
        )
        # enc_arm_left: EncoderGeneral = RotationEncoder(signal_pin=cfg.arm.left.encoder)
        # enc_arm_right: EncoderGeneral = RotationEncoder(
        #     signal_pin=cfg.arm.right.encoder
        # )

        i2c: busio.I2C = busio.I2C(board.SCL, board.SCA)
        sensor9DOF: BBAbsoluteSensor = BB_BNO055Sensor(i2c)

        bluedot_control: DirectionController | None = (
            bluedot_direction_control.BlueDotRobotController(eh=eh)
        )

    elif os.name == "nt":
        # Running on Windows, start robot simulator.
        eh.post(event_type="log", message="INFO: Stating Robot Simulator")
        from motor_simulator import MotorSim
        from encoder_simulator import EncoderSim
        from bb_9dof_sensor_simulator import BB9DOFSensorSimulator

        motor_wheel_left: MotorGeneral = MotorSim()
        motor_wheel_right: MotorGeneral = MotorSim()
        # motor_arm_left: Motor_General = MotorSim()
        # motor_arm_right: Motor_General = MotorSim()

        enc_wheel_left: EncoderGeneral = EncoderSim(motor=motor_wheel_left, eh=eh)
        enc_wheel_left.start()
        enc_wheel_right: EncoderGeneral = EncoderSim(motor=motor_wheel_right, eh=eh)
        enc_wheel_right.start()
        # enc_arm_left: Encoder_General = EncoderSim()
        # enc_arm_right: Encoder_General = EncoderSim()

        sensor9DOF: BB9DOFSensorSimulator = BB9DOFSensorSimulator(eh=eh)

        bluedot_control: DirectionController | None = None

    else:
        post_event(
            "log", "ERROR: Balance Bot - OS not identified. Please try on Raspberry Pi"
        )

    start_prog = [30, 0, 0]  # stand still for 30 seconds

    robot = BalanceBot(  # type: ignore
        motor_wheel_left=motor_wheel_left,
        motor_wheel_right=motor_wheel_right,
        # motor_arm_left=motor_arm_left,
        # motor_arm_right=motor_arm_right,
        enc_wheel_left=enc_wheel_left,
        enc_wheel_right=enc_wheel_right,
        # enc_arm_left=enc_arm_left,
        # enc_arm_right=enc_arm_right,
        sensor9DOF=sensor9DOF,
        start_prog=start_prog,
        repeat_prog=None,
        bluedot_control=bluedot_control,
    )


if __name__ == "__main__":
    main()
