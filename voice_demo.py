#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sttcli
import ConfigParser
from Tkinter import *
from ttk import *
from blelight import *

class VoiceOrganizer(Frame):
    def __init__(self, master=None):
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()

    def stt_done(self):
        self.sttText["text"] = "Voice"

    def blelight_done(self):
        self.bleligthText["text"] = "BLE Light"
        
    def stt_handler(self, msg):
        if msg.has_key('results') and len(msg['results']) > 0:
            transcript = unicode(msg['results'][0]['alternatives'][0]['transcript'])
            self.sttField.insert(END, transcript + '\n')
            self.sttField.see("end")
            
            # ble control
            if u'打开' in transcript:
                blelights.control(1, 1)
                blelights.control(2, 1)
            if u'关闭' in transcript:
                blelights.control(1, 0)
                blelights.control(2, 0)                
 
    def createWidgets(self):
        # Watson STT raw
        self.sttText = Label(self)
        self.sttText["text"] = "*Voice*"
        self.sttText.grid(row=0, column=0)
        self.sttField = Text(self, height=8, width=60)
        self.sttField.grid(row=0, column=1, columnspan=6)

        # health 
        self.healthText = Label(self)
        self.healthText["text"] = "Health"
        self.healthText.grid(row=1, column=0)
        self.healthField = Text(self, height=8, width=60)
        self.healthField.grid(row=1, column=1, columnspan=6)

        # bluetooth
        self.bluetoothText = Label(self)
        self.bluetoothText["text"] = "Bluetooth"
        self.bluetoothText.grid(row=2, column=0)
        self.bluetoothField = Text(self, height=8, width=60)
        self.bluetoothField.grid(row=2, column=1, columnspan=6)

        # bleligth
        self.bleligthText = Label(self)
        self.bleligthText["text"] = "*BLE Light*"
        self.bleligthText.grid(row=3, column=0)
        self.bleligthField = Text(self, height=4, width=60)
        self.bleligthField.grid(row=3, column=1, columnspan=6)

        # buttons
        self.exitBtn = Button(self, text = "Exit", command = lambda:root.destroy())
        self.exitBtn.grid(row=4, column=6)
 
        self.displayText = Label(self)
        self.displayText["text"] = "something happened"
        self.displayText.grid(row=5, column=0, columnspan=7)

if __name__ == '__main__':
    # init TK
    root = Tk()
    root.title("IBM Watson Voice Service Application")
    app = VoiceOrganizer(master = root)
    
    # init watson service
    cfg = ConfigParser.ConfigParser()
    cfg.read("./account.conf")
    username = cfg.get("bluemix", "username")
    password = cfg.get("bluemix", "password")
    keyword_array = ['小白今天血压', '打开', '关闭', '一号', '二号', '灯', '小智', '再见', '你好', '号灯']
    stt_client = sttcli.SpeechToTextClient( username, 
                                            password, 
                                            on_recv_msg = app.stt_handler, 
                                            keywords = keyword_array, 
                                            keywords_threshold = 0.1, 
                                            done_handler = app.stt_done) # block mode
    
    # init ble light
    blelights = BleLight("00:02:5B:00:10:73", done_handler = app.blelight_done) # block mode
    
    # tk main loop
    app.mainloop()
    
    # ending
    blelights.close()
    stt_client.close()
 
