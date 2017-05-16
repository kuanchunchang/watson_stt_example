#!/usr/bin/env python
# -*- coding: utf-8 -*-

from ws4py.client.threadedclient import WebSocketClient
import base64, json, ssl, subprocess, threading, time

class SpeechToTextClient(WebSocketClient):
    def __init__(self, username, password, model = "zh-CN_BroadbandModel", interim = "false", on_recv_msg = None, timeout = -1, keywords = [], keywords_threshold = 0.0, done_handler = None):
        ws_url = "wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize?model=%s" % (model)

        auth_string = "%s:%s" % (username, password)
        base64string = base64.encodestring(auth_string).replace("\n", "")

        self.username = username
        self.password = password
        self.model = model
        self.listening = False
        self.on_recv_msg = on_recv_msg
        self.inactivity_timeout = timeout;
        self.keywords = keywords
        self.keywords_threshold = keywords_threshold
        self.interim = interim

        try:
            WebSocketClient.__init__(self, ws_url,
                headers=[("Authorization", "Basic %s" % base64string)])
            self.connect()

            if done_handler != None: done_handler()

        except: print "Failed to open WebSocket."

    def opened(self):
        # make json string
        json_data = {
            "action": "start",
            "content-type": "audio/l16;rate=16000;channels=1",
            "inactivity_timeout": self.inactivity_timeout,
            "keywords": self.keywords,
            "keywords_threshold": self.keywords_threshold,
            "interim_results": self.interim,
        }
        #print json.dumps(json_data)
        self.send(json.dumps(json_data))
        self.stream_audio_thread = threading.Thread(target=self.stream_audio)
        self.stream_audio_thread.start()

    def received_message(self, message):
        message = json.loads(str(message))
        if "state" in message:
            if message["state"] == "listening":
                if self.listening == False:
                    self.listening = True
                else:
                    self.send('{"action": "stop"}')

        if self.on_recv_msg != None:
            self.on_recv_msg(message)
        else:
            print "Message received:" + str(message)
            if message.has_key('results') and len(message['results']) > 0:
                print unicode(message['results'][0]['alternatives'][0]['transcript'])

    def stream_audio(self):
        while not self.listening:
            time.sleep(0.1)

        reccmd = ["arecord", "-f", "S16_LE", "-r", "16000", "-t", "raw"]
        p = subprocess.Popen(reccmd, stdout=subprocess.PIPE)

        while self.listening:
            data = p.stdout.read(1024)

            try: self.send(bytearray(data), binary=True)
            except ssl.SSLError: pass
            except:
                print "RECONNECT"
                self.__init__(  self.username,
                                self.password,
                                on_recv_msg = self.on_recv_msg,
                                interim = self.interim,
                                keywords = self.keywords,
                                keywords_threshold = self.keywords_threshold)

        p.kill()

    def close(self):
        self.listening = False
        self.stream_audio_thread.join()
        WebSocketClient.close(self)

