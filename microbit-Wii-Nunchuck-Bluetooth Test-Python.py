from microbit import *

class chuck:
    def __init__(self):
        self.addr = 0x52
        bufr = pins.createBuffer(2)
        bufr.setNumber(format=NumberFormat.UINT8_BE,
                       offset=0,
                       value=b'0x40')
        bufr.setNumber(NumberFormat.UINT8_BE,
                       0,
                       b'0x00')
        pins.i2c_write_buffer(address=self.addr,
                              buf=bufr,
                              repeat=False)
        basic.pause (1000)

    def read(self):
        pins.i2c_write_number(address=self.addr,
                              value=b'\x00',
                              format=NumberFormat.INT8_LE)
        basic.pause(1000)
        buf = pins.i2c_read_buffer(address=self.addr,
                                    size=6,
                                    repeat=False)
        data = [(0x17 + (0x17 ^ buf[i])) for i in range(6)]
        return data

    def readall(self):
        data = self.read()
        butc = (data[5] & 0x02)
        butz = (data[5] & 0x01)
        # joyX, joyY, accX, accY, accZ, c, z
        return data[0],data[1], data[2], data[3],data[4],butc==0,butz==0  

def on_bluetooth_connected():
    basic.show_leds("""
        . # # # .
        # . . . .
        # . . . .
        # . . . .
        . # # # .
        """)
bluetooth.on_bluetooth_connected(on_bluetooth_connected)

def on_bluetooth_disconnected():
    basic.show_leds("""
        # # # . .
        # . . # .
        # . . # .
        # . . # .
        # # # . .
        """)
bluetooth.on_bluetooth_disconnected(on_bluetooth_disconnected)


wii = chuck()        

basic.show_leds("""
    # . . # #
    # . . # #
    # # # . .
    # . # . .
    # # # . .
    """)

def on_forever():
    joyX, joyY, accX, accY, accZ, c, z = wii.readall()
    # basic.show_string(' '.join(str(x) for x in (joyX, joyY, accX, accY, accZ, c, z)))
    joystick_str = ' '.join(str(x) for x in (joyX, joyY))
    basic.show_string(joystick_str)
    bluetooth.
    basic.pause(5000)

basic.forever(on_forever)

# bluetooth.start_accelerometer_service()
# bluetooth.start_button_service()
# bluetooth.start_led_service()
# bluetooth.start_temperature_service()

