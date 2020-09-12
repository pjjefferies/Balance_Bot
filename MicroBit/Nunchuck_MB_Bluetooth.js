// from microbit import *

let addr = 0x52
// basic.showNumber(addr)
pins.i2cWriteBuffer(addr, Buffer.fromHex("4000"), false)
// i2c.write(self.addr, bytes([0x40, 0x00]), repeat=False)
basic.pause(1)

function read_wii_chuk() {
    pins.i2cWriteBuffer(addr, Buffer.fromHex("00"), false)
    basic.pause(1)
    let buf = pins.i2cReadBuffer(addr, 6, false)
    // data = [for (const x of Array(5).keys()) (0x17 + (0x17 ^ buf[i]))]
    // basic.showNumber(buf[5])
    let data = [(0x17 + (0x17 ^ buf[0])),
                (0x17 + (0x17 ^ buf[1])),
                (0x17 + (0x17 ^ buf[2])),
                (0x17 + (0x17 ^ buf[3])),
                (0x17 + (0x17 ^ buf[4])),
                (0x17 + (0x17 ^ buf[5]))]
    // data = [(0x17 + (0x17 ^ buf[i])) for i in range(6)]
    return data
}

function readall_wii_chuk() {
    let data = read_wii_chuk()
    let butc = (data[5] & 0x02)
    let butz = (data[5] & 0x01)
    // joyX, joyY, accX, accY, accZ, c, z
    return [data[0], data[1], data[2], data[3],
            data[4], butc == 0, butz == 0]
}

/*
function joystick() {
    let data = read_wii_chuk()
    return [data[0], data[1]]
}

function wii_accelerometer() {
    let data = read_wii_chuk()
    return [data[2], data[3], data[4]]
}

function buttons() {
    let data = read_wii_chuk()
    let butc = (data[5] & 0x02)
    let butz = (data[5] & 0x01)
    return [butc == 0, butz == 0]
}
*/
function button_c() {
    let data = read_wii_chuk()
    // basic.showNumber(data[5])
    let butc = (data[5] & 0x02)
    return butc == 0
}
//*
function button_z() {
    let data = read_wii_chuk()
    let butz = (data[5] & 0x01)
    return butz == 0
}

function joystick_x() {
    let data = read_wii_chuk()
    return data[0]
}

function joystick_y() {
    let data = read_wii_chuk()
    return data[1]
}

function accelerometer_x() {
    let data = read_wii_chuk()
    basic.showNumber(data[2])
    return data[2]
}

function accelerometer_y() {
    let data = read_wii_chuk()
    return data[3]
}

function accelerometer_z() {
    let data = read_wii_chuk()
    return data[4]
}

basic.forever(() => {
    let result = readall_wii_chuk()

    let joyX = result[0]
    if (joyX < 50) {
        led.plot(0, 2)
        led.unplot(4, 2)
    } else if (joyX > 200) {
        led.unplot(0, 2)
        led.plot(4, 2)
    } else {
        led.unplot(0, 2)
        led.unplot(4, 2)
    }

    let joyY = result[1]
    if (joyY < 50) {
        led.unplot(2, 0)
        led.plot(2, 4)
    } else if (joyY > 200) {
        led.plot(2, 0)
        led.unplot(2, 4)
    } else {
        led.unplot(2, 0)
        led.unplot(2, 4)
    }

    let but_c = result[5]
    if (but_c) {
        led.plot(1, 2)
    } else {
        led.unplot(1, 2)
    }

    let but_z = result[6]
    if (but_z) {
        led.plot(3, 2)
    } else {
        led.unplot(3, 2)
    }

    basic.pause(50)
})
