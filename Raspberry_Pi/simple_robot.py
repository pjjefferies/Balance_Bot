#! /usr/bin/python3

import time
from gpiozero import Motor
import bluedot_direction_control


class Simple_Robot:
    """
    Basic Robot Manual control for 2-Motor Simple Robot
    """
    def __init__(self, left_forward_line, left_backward_line,
                 right_forward_line, right_backward_line):
        """


        Args:
            left_forward_line (TYPE): DESCRIPTION.
            left_backward_line (TYPE): DESCRIPTION.
            right_forward_line (TYPE): DESCRIPTION.
            right_backward_line (TYPE): DESCRIPTION.

        Returns:
            None.

        """
        self.motor_l = Motor(forward=left_forward_line,
                             backward=left_backward_line,
                             pwm=True)
        self.motor_r = Motor(forward=right_forward_line,
                             backward=right_backward_line,
                             pwm=True)
        self.bd_ctl = bluedot_direction_control.bd_drive

    def drive_two_wheel_robot_by_bd(self, interval=500, duration=60):  # ms, s
        start_time = time.time()

        lasttime = 0

        while time.time() - start_time < duration:
            if (time.time()*1000 - lasttime) >= interval:
                lasttime = time.time() * 1000
                direction = self.bd_drive()  # [x, y] eached scaled [-1, 1]
                if direction == [0, 0]:
                    self.motor_l.value = 0
                    self.motor_r.value = 0
                else:
                    fwd_vel = direction[0]
                    right_turn = direction[1]
                    self.motor_l.value = fwd_vel + right_turn
                    self.motor_r.value = fwd_vel - right_turn


if __name__ == "__main__":
    MOTOR_L_FWD = 7
    MOTOR_L_RWD = 11
    # MOTOR_L_ENABLE = 25
    MOTOR_R_FWD = 13
    MOTOR_R_RWD = 15
    # MOTOR_R_ENABLE = ?

    ROBOT_RUN_DURATION = 60  # Seconds
    CONTROL_STEPS = 500  # milliseconds

    two_wheel_robot = Simple_Robot(MOTOR_L_FWD,
                                   MOTOR_L_RWD,
                                   MOTOR_R_FWD,
                                   MOTOR_R_RWD)

    two_wheel_robot.drive_two_wheel_robot_by_bd(interval=CONTROL_STEPS,
                                                duration=ROBOT_RUN_DURATION)
