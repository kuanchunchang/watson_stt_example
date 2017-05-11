#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sttcli
import os, ConfigParser, subprocess, numpy
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
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

health_record = {
    u'小白血压': 0,
    u'小白血糖': 0,
    u'小白体重': 0,
    u'小白记录': 0,
    u'小黑血压': 0,
    u'小黑血糖': 0,
    u'小黑体重': 0,
    u'小黑记录': 0,
}

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
        self.pltimg = None
        self.health_cfg = ConfigParser.ConfigParser()
        self.health_cfg.read("healthrecord.ini")
        # matplotlib
        self.fig = Figure(figsize=(5,4))
        self.ax1 = self.fig.add_subplot(311)
        self.ax2 = self.fig.add_subplot(312)
        self.ax3 = self.fig.add_subplot(313)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.healthRecord)
        matplotlib.rcParams.update({'font.size': 9})

    def get_bw_list(self, who):
        str_list = list(self.health_cfg.get(who, 'body_weight', "").split(','))
        int_list = map(int, str_list)
        return int_list

    def get_bp_list(self, who):
        str_list = list(self.health_cfg.get(who, 'blood_pressure', "").split(','))
        int_list = map(int, str_list)
        return int_list

    def get_bs_list(self, who):
        str_list = list(self.health_cfg.get(who, 'blood_sugar', "").split(','))
        int_list = map(int, str_list)
        return int_list

    def stt_done(self):
        self.sttText["text"] = "Voice"

    def blelight_done(self):
        self.bleligthText["text"] = "BLE Light"
        
    def speak(self, spk_str):
        cmd = "/usr/bin/espeak -vzh+f5 %s --stdout | aplay -D plughw:%s" % (spk_str, self.audio_output)
        subprocess.Popen(cmd, shell=True)

    def show_health_plot(self, val):
        idx = val & 0x0F
        who = 'small_white' if idx==0x00 else 'small_black'
        who_zh = u'小白' if idx==0x00 else u'小黑'
        who_bw = health_record[who_zh + u'体重']
        who_bp = health_record[who_zh + u'血压']
        who_bs = health_record[who_zh + u'血糖']

        self.ax1.clear()
        self.ax2.clear()
        self.ax3.clear()

        self.ax1.set_title(u'Whity' if idx==0x00 else u'Black')
        self.ax1.plot(self.get_bw_list(who) + ([who_bw] if who_bw != 0 else []), 'ro-', label='body weight')
        self.ax1.set_ylim([30,100])
        self.ax1.legend(loc=2)
        self.ax1.text(15,  80, r'avg=%.2f, today=%d' % (numpy.mean(self.get_bw_list(who) + [who_bw]), who_bw), fontsize=9)

        self.ax2.plot(self.get_bp_list(who) + ([who_bp] if who_bp != 0 else []), 'go-', label='blood pressure')
        self.ax2.set_ylim([60,220])
        self.ax2.legend(loc=2)
        self.ax2.text(15, 180, r'avg=%.2f, today=%d' % (numpy.mean(self.get_bp_list(who) + [who_bp]), who_bp), fontsize=9)

        self.ax3.plot(self.get_bs_list(who) + ([who_bs] if who_bs != 0 else []), 'bo-', label='blood sugar')
        self.ax3.set_ylim([50,200])
        self.ax3.legend(loc=2)
        self.ax3.text(15, 160, r'avg=%.2f, today=%d' % (numpy.mean(self.get_bs_list(who) + [who_bs]), who_bs), fontsize=9)

        self.canvas.show()
        self.canvas.get_tk_widget().pack()

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
                        val = self.text_to_number(transcript[4:])
                        if val != 0 or u'记录' in transcript:
                            event_type = 1
                            event_key  = key
                            event_data = val
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
            self.output_fields[0].see("end")
            if bFinal == True:
                self.output_fields[0].insert(END, '\n')
                if event_type != 0:
                    self.output_fields[event_type].insert(END, transcript + '\n')
                    self.output_fields[event_type].see("end")
                self.row = self.row + 1

            # do health
            if event_type == 1 and bFinal == True:
                val = health_patterns[event_key]
                if (val & 0x80) == 0x80:    # it's show-record command
                    self.show_health_plot(val)
                else:                       # it's data, save it to health_record and show plot
                    self.speak(transcript)
                    health_record[event_key] = event_data
                    self.show_health_plot(val)
            # do bluetooth
            elif event_type == 2:
                pass
            # do blelight
            elif event_type == 3 and self.do_blelight == True:
                for val in blelight_patterns[event_key]:
                    blelights.control(val[0], val[1])

    def text_to_number(self, txt):
        ttn_patterns = {u'九':9, u'八':8, u'七':7, u'六':6, u'五':5, u'四':4, u'三':3, u'二':2, u'一':1,}
        sum = 0
        if u'百' in txt :
            idx = txt.index(u'百')
            txt_digit = txt[idx - 1]
            digit = ttn_patterns[txt_digit]
            sum += digit * 100

        if u'十' in txt :
            idx = txt.index(u'十')
            txt_digit = txt[idx - 1]
            digit = ttn_patterns[txt_digit]
            sum += digit * 10
            if len(txt) > idx + 1:
                txt_digit = txt[idx + 1]
                try:
                    sum += ttn_patterns[txt_digit]
                except:
                    pass

        return sum

    def createWidgets(self):
        # Watson STT
        self.sttText = Label(self)
        self.sttText["text"] = "*Voice*"
        self.sttText.grid(row=0, column=0)
        self.sttField = Text(self, height=4, width=56, font=(None, 12))
        self.sttField.grid(row=0, column=1, columnspan=6, sticky=W)

        # health
        self.healthText = Label(self)
        self.healthText["text"] = "Health"
        self.healthText.grid(row=1, column=0)
        self.healthField = Text(self, height=4, width=16, font=(None, 12))
        self.healthField.grid(row=1, column=1, columnspan=2, sticky=W)
        self.healthRecord = Canvas(self, width=400, height=320)
        self.healthRecord.grid(row=1, column=3, rowspan=3, columnspan=4)

        # bleligth
        self.bleligthText = Label(self)
        self.bleligthText["text"] = "*BLE Light*"
        self.bleligthText.grid(row=2, column=0)
        self.bleligthField = Text(self, height=4, width=16, font=(None, 12))
        self.bleligthField.grid(row=2, column=1, columnspan=2, sticky=W)

        # headset
        self.bluetoothText = Label(self)
        self.bluetoothText["text"] = "HeadSet"
        self.bluetoothText.grid(row=3, column=0)
        self.bluetoothField = Text(self, height=4, width=16, font=(None, 12))
        self.bluetoothField.grid(row=3, column=1, columnspan=2, sticky=W)

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
    keyword_array = ['全', '打', '开', '关', '闭', '一', '二', '号', '灯', '小', '白', '黑', '今', '天', '血', '压', '糖', '体', '重', '记', '录']
    stt_client = sttcli.SpeechToTextClient( username, 
                                            password, 
                                            on_recv_msg = app.stt_handler,
                                            interim = "true",
                                            keywords = keyword_array, 
                                            keywords_threshold = 0.05,
                                            done_handler = app.stt_done) # block mode

    # init ble light
    if do_blelight:
        blelights = BleLight("00:02:5B:00:10:73", done_handler = app.blelight_done) # block mode

    # tk main loop
    app.mainloop()

    # ending
    if do_blelight and blelights != None: blelights.close()
    stt_client.close()
