#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sttcli
import os, ConfigParser, subprocess
from Tkinter import *
from ttk import *
from blelight import *

#### global vars
blelight_patterns = {
    u'全开'    : [(1, 1), (2, 1)],
    u'全关'    : [(1, 0), (2, 0)],
    u'打开一号': [(1, 1)],
    u'打开二号': [(2, 1)],
    u'关闭一号': [(1, 0)],
    u'关闭二号': [(2, 0)],
}

health_patterns = {
    u'小白血压': 0x00,
    u'小白血糖': 0x00,
    u'小白体重': 0x00,
    u'小白记录': 0x80,
    u'小黑血压': 0x01,
    u'小黑血糖': 0x01,
    u'小黑体重': 0x01,
    u'小黑记录': 0x81,
}

health_record = [[], []]

#### calss ####
class VoiceOrganizer(Frame):
    def __init__(self, master=None, audio_output="0,0", do_blelight=False):
        Frame.__init__(self, master)
        self.grid()
        self.createWidgets()
        self.output_fields = [self.sttField, self.healthField, self.bluetoothField, self.bleligthField]
        self.audio_output = audio_output
        self.do_blelight = do_blelight
        self.row = 1

    def stt_done(self):
        self.sttText["text"] = "Voice"

    def blelight_done(self):
        self.bleligthText["text"] = "BLE Light"
        
    def speak(self, spk_str):
        cmd = "/usr/bin/espeak -vzh %s --stdout | aplay -D plughw:%s" % (spk_str, self.audio_output)
        subprocess.Popen(cmd, shell=True)

    def stt_handler(self, msg):
        if msg.has_key('results') and len(msg['results']) > 0:
            # vars
            event_type = 0 # 0: stt, 1: health, 2: bluetooth, 3: blelight
            event_key = None
            event_data = None

            # get transcript
            bFinal = msg['results'][0]['final']
            transcript = unicode(msg['results'][0]['alternatives'][0]['transcript']).replace(u' ', '')

            # test if health (1)
            if bFinal:
                for key in health_patterns.keys():
                    if key in transcript:
                        event_type = 1
                        event_key  = key
                        event_data = transcript
                        break
            # test if bluetooth (2)
            # test if blelight (3)
            if bFinal:
                for key in blelight_patterns.keys():
                    if key in transcript:
                        event_type = 3
                        event_key  = key
                        break

            # show transcript in corresponding field
            self.output_fields[0].delete("%s.0"%(self.row), "%s.99"%(self.row))
            self.output_fields[0].insert("%s.0"%(self.row), transcript)
            if bFinal == True:
                self.output_fields[0].insert(END, '\n')
                if event_type != 0:
                    self.output_fields[event_type].insert(END, transcript + '\n')
                self.row = self.row + 1
            self.output_fields[0].see("end")

            # do health
            if event_type == 1 and bFinal == True:
                val = health_patterns[event_key]
                if (val & 0x80) == 0x80:    # it's show-record command
                    self.healthRecord.delete('1.0', END)
                    idx = val & 0x0F
                    spk_str = ""
                    for hr in health_record[idx]:
                        self.healthRecord.insert(END, hr + '\n')
                        spk_str += hr
                        #health_record.remove(hr)
                    self.speak(spk_str)
                else:                       # it's data, save it to healt_record
                    self.speak(event_data)
                    health_record[val].append(event_data)
                    #print health_record

            # do bluetooth
            elif event_type == 2:
                pass
            # do blelight
            elif event_type == 3 and self.do_blelight == True:
                for val in blelight_patterns[event_key]:
                    blelights.control(val[0], val[1])

    def createWidgets(self):
        # Watson STT
        self.sttText = Label(self)
        self.sttText["text"] = "*Voice*"
        self.sttText.grid(row=0, column=0)
        self.sttField = Text(self, height=6, width=60, font=(None, 16))
        self.sttField.grid(row=0, column=1, columnspan=6)

        # health
        self.healthText = Label(self)
        self.healthText["text"] = "Health"
        self.healthText.grid(row=1, column=0)
        self.healthField = Text(self, height=6, width=30, font=(None, 16))
        self.healthField.grid(row=1, column=1, columnspan=3)
        self.healthRecord = Text(self, height=6, width=30, font=(None, 16))
        self.healthRecord.grid(row=1, column=4, columnspan=3)

        # bluetooth
        self.bluetoothText = Label(self)
        self.bluetoothText["text"] = "Bluetooth"
        self.bluetoothText.grid(row=2, column=0)
        self.bluetoothField = Text(self, height=6, width=60, font=(None, 16))
        self.bluetoothField.grid(row=2, column=1, columnspan=6)

        # bleligth
        self.bleligthText = Label(self)
        self.bleligthText["text"] = "*BLE Light*"
        self.bleligthText.grid(row=3, column=0)
        self.bleligthField = Text(self, height=4, width=60, font=(None, 16))
        self.bleligthField.grid(row=3, column=1, columnspan=6)

        # buttons
        self.exitBtn = Button(self, text = "Exit", command = lambda:root.destroy())
        self.exitBtn.grid(row=4, column=6)


if __name__ == '__main__':
    # vars
    audio_output = "0,0"
    do_blelight = False
    # check system: dragonboard or PC ?
    arch = os.uname()[-1]
    if arch == "aarch64":   # dragonboard
        audio_output = "0,0"
        do_blelight = True

    # init TK
    root = Tk()
    root.title("IBM Watson Voice Service Application")
    app = VoiceOrganizer(root, audio_output, do_blelight)
    
    # init watson service
    cfg = ConfigParser.ConfigParser()
    cfg.read("./account.conf")
    username = cfg.get("bluemix", "username")
    password = cfg.get("bluemix", "password")
    keyword_array = ['全', '打', '开', '关', '闭', '一', '二', '号', '灯', '小白', '小黑', '今天', '血压', '血糖', '体重', '再见', '你好']
    stt_client = sttcli.SpeechToTextClient( username, 
                                            password, 
                                            on_recv_msg = app.stt_handler,
                                            interim = "true",
                                            keywords = keyword_array, 
                                            keywords_threshold = 0.1, 
                                            done_handler = app.stt_done) # block mode

    # init ble light
    if do_blelight:
        blelights = BleLight("00:02:5B:00:10:73", done_handler = app.blelight_done) # block mode

    # tk main loop
    app.mainloop()

    # ending
    if do_blelight and blelights != None: blelights.close()
    stt_client.close()

