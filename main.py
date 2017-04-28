#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sttcli
import ConfigParser

def handler_recv_msg(msg):
    if msg.has_key('results') and len(msg['results']) > 0:
        print unicode(msg['results'][0]['alternatives'][0]['transcript'])

def main():
    # load username/password
    cfg = ConfigParser.ConfigParser()
    cfg.read("./account.conf")
    username = cfg.get("bluemix", "username")
    password = cfg.get("bluemix", "password")
    keyword_array = ['小白', '小黑', '血压', '体重', '血糖', '开灯', '关灯']

    try:
        stt_client = sttcli.SpeechToTextClient(username, password, on_recv_msg = None, keywords = keyword_array, keywords_threshold = 0.1)
        raw_input()
    finally:
        stt_client.close()


if __name__ == "__main__":
    main()


