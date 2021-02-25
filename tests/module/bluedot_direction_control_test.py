#! /usr/bin/python3



prev_position = [101, 101]  # start with impossible position for comp.

while True:
    position = list(bd_drive())
    if position != prev_position:
        print(rf'x:{position[1]}, y:{position[0]}')
    prev_position = position
    sleep(0.2)
