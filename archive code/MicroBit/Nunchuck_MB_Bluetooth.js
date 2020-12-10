// from microbit import *

let addr = 0x52
pins.i2cWriteBuffer(addr, Buffer.fromHex("4000"), false)
basic.pause(1)

function read_wii_chuk() {
    pins.i2cWriteBuffer(addr, Buffer.fromHex("00"), false)
    basic.pause(1)
    let buf = pins.i2cReadBuffer(addr, 6, false)
    let data = [(0x17 + (0x17 ^ buf[0])),
                (0x17 + (0x17 ^ buf[1])),
                (0x17 + (0x17 ^ buf[2])),
                (0x17 + (0x17 ^ buf[3])),
                (0x17 + (0x17 ^ buf[4])),
                (0x17 + (0x17 ^ buf[5]))]
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

basic.forever(() => {
    let result = readall_wii_chuk()

    let joyX = result[0]
    if (joyX < 75) {
        led.plot(0, 2)
        led.unplot(4, 2)
    } else if (joyX > 175) {
        led.unplot(0, 2)
        led.plot(4, 2)
    } else {
        led.unplot(0, 2)
        led.unplot(4, 2)
    }

    let joyY = result[1]
    if (joyY < 75) {
        led.unplot(2, 0)
        led.plot(2, 4)
    } else if (joyY > 175) {
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
