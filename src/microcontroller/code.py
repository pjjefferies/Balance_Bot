
import board
import busio
import digitalio
import adafruit_bno055
import time

# Attach BNO055 Absolute Sensor
# i2c = busio.I2C(board.SCL, board.SDA)
# sensor = adafruit_bno055.BNO055_I2C(i2c)

led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT
print("Hello World!")

def main():
    while True:
        led.value = True
        time.sleep(2)
        led.value = False
        time.sleep(2)
        print(f"Temperature: {sensor.temperature} degrees C")
        """
        print(
            "Temperature: {} degrees C".format(temperature())
        )  # Uncomment if using a Raspberry Pi
        """
        print(f"Accelerometer (m/s^2): {sensor.acceleration}")
        print(f"Magnetometer (microteslas): {sensor.magnetic}")
        print(f"Gyroscope (rad/sec): {sensor.gyro}")
        print(f"Euler angle: {sensor.euler}")
        print(f"Quaternion: {sensor.quaternion}")
        print(f"Linear acceleration (m/s^2): {sensor.linear_acceleration}")
        print(f"Gravity (m/s^2): {sensor.gravity}")
        print()

if __name__ == "__main__":
    main()
