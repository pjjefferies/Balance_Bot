from microbit import *

class chuck:

    def __init__(self):
        self.addr = 0x52
        i2c.write(self.addr, bytes([0x40, 0x00]), repeat=False)
        sleep(1)

    def read(self):
        i2c.write(self.addr, b'\x00', repeat=False)
        sleep(1)
        buf = i2c.read(self.addr, 6, repeat=False)
        data = [(0x17 + (0x17 ^ buf[i])) for i in range(6)]
        return data

    def readall(self):
        data = self.read()
        butc = (data[5] & 0x02)
        butz = (data[5] & 0x01)
        # joyX, joyY, accX, accY, accZ, c, z
        return (data[0], data[1], data[2], data[3],
                data[4], butc == 0, butz == 0)

    def joystick(self):
        data = self.read()
        return data[0], data[1]

    def wii_accelerometer(self):
        data = self.read()
        return data[2], data[3], data[4]

    def buttons(self):
        data = self.read()
        butc = (data[5] & 0x02)
        butz = (data[5] & 0x01)
        return butc == 0, butz == 0

    def button_c(self):
        data = self.read()
        butc = (data[5] & 0x02)
        return butc == 0

    def button_z(self):
        data = self.read()
        butz = (data[5] & 0x01)
        return butz == 0

    def joystick_y(self):
        data = self.read()
        return data[1]

    def accelerometer_x(self):
        data = self.read()
        return data[2]

    def accelerometer_y(self):
        data = self.read()
        return data[3]

    def accelerometer_z(self):
        data = self.read()
        return data[4]


wii = chuck()
def test_func():
    while True:
        data = wii.readall()
        print(data)
        image_1 = Image("00000:"
                        "00000:"
                        "00100:"
                        "00000:"
                        "00000")
        image_2 = Image("00000:"
                        "01110:"
                        "01010:"
                        "01110:"
                        "00000")
        if data[5]:
            display.show(image_1)
        else:
            display.show(image_2)
        sleep(50)