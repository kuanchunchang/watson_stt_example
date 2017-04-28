#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pexpect

class BleLight():
    def __init__(self, mac, done_handler = None):
        # block mode
        self.child = pexpect.spawn("gatttool -I -b {0}".format(mac))
        self.child.expect("LE", timeout = 10)
        self.child.sendline("connect") 
        self.child.expect("CON", timeout = 10)
        
        if done_handler != None: done_handler()

    def control(self, num, onoff):
        command = 'char-write-req 0x0B FA%02X%02XFE' % (num, onoff)
        #print command
        self.child.sendline(command)
        self.child.expect("successfully", timeout = 10)

    def close(self):
        self.child.close()

if __name__ == "__main__":
    # example
    # 00:02:5B:00:10:73
    # 00:02:5B:00:10:74
    blelights = BleLight("00:02:5B:00:10:73")
    blelights.control(1, 0)
    blelights.control(2, 0)
    