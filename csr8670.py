#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os, time, threading

# APQ | LSC | CSR8670
# 12  |  24 | ANS/REJ(ORANGE)
# 69  |  26 | V+/FW  (RED)
# 25  |  30 | P/P    (BLUE)
# 33  |  34 | V-/BW  (BROWN)

function_parameters = [
    #PIN#, value, time, value, function         CSR8670 GPIO
    [12,        1,  0.3,    0, "answer call"], # PIO13 ORANGE
    [12,        1,  1.1,    0, "reject call"], # PIO13 ORANGE
    [69,        1,  0.3,    0, "volume up"  ], # PIO12 RED
    [33,        1,  0.3,    0, "volume down"], # PIO11 BROWN
    [25,        1,  0.3,    0, "play/pause" ], # PIO10 BLUE
    [33,        1,  1.1,    0, "foward"     ], # PIO11 BROWN
    [69,        1,  1.1,    0, "backward"   ], # PIO12 RED
]

class GpioDB410():
    '''
    this class controlls these pins:
    J8 PIN24 -- APQ_GPIO_12 -- SW PIN 0
    J8 PIN26 -- APQ_GPIO_69 -- SW PIN 1
    J8 PIN30 -- APQ_GPIO_25 -- SW PIN 2
    J8 PIN34 -- APQ_GPIO_33 -- SW PIN 3
    '''
    def __init__(self):
        self.pin_nums = [12, 69, 25, 33]
        cmd =   'sudo bash -c "' \
                'echo %d > /sys/class/gpio/export;' \
                'echo %d > /sys/class/gpio/export;' \
                'echo %d > /sys/class/gpio/export;' \
                'echo %d > /sys/class/gpio/export;' \
                '"' % (self.pin_nums[0], self.pin_nums[1], self.pin_nums[2], self.pin_nums[3])
        os.system(cmd)
        cmd =   'sudo bash -c "' \
                'echo out > /sys/class/gpio/gpio%d/direction;' \
                'echo out > /sys/class/gpio/gpio%d/direction;' \
                'echo out > /sys/class/gpio/gpio%d/direction;' \
                'echo out > /sys/class/gpio/gpio%d/direction;' \
                '"' % (self.pin_nums[0], self.pin_nums[1], self.pin_nums[2], self.pin_nums[3])
        os.system(cmd)

    def set_val(self, pin, val):
        cmd =   'sudo bash -c "' \
                'echo %d > /sys/class/gpio/gpio%d/value;' \
                '"' % (val, pin)
        os.system(cmd)

    def close(self):
        cmd =   'sudo bash -c "' \
                'echo %d > /sys/class/gpio/unexport;' \
                'echo %d > /sys/class/gpio/unexport;' \
                'echo %d > /sys/class/gpio/unexport;' \
                'echo %d > /sys/class/gpio/unexport;' \
                '"' % (self.pin_nums[0], self.pin_nums[1], self.pin_nums[2], self.pin_nums[3])
        os.system(cmd)


class CSR8670():
    def __init__(self):
        self.gpio = GpioDB410()
        self.thread = None

    def do_func(self, func_id):
        self.thread = threading.Thread(target=self.toggle_gpio, args=(func_id,))
        self.thread.start()

    def toggle_gpio(self, func_id):
        pin     = function_parameters[func_id][0]
        val1    = function_parameters[func_id][1]
        time_ms = function_parameters[func_id][2]
        val2    = function_parameters[func_id][3]
        func    = function_parameters[func_id][4]

        print pin, val1, time_ms, val2, func
        self.gpio.set_val(pin, val1)
        time.sleep(time_ms)
        self.gpio.set_val(pin, val2)

    def close(self):
        self.gpio.close()

if __name__ == "__main__":
    # test module
    csr8670 = CSR8670()
    csr8670.do_func(2)
    csr8670.close()

