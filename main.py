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
    keyword_array = ['打开', '关闭', '一号', '二号', '灯', '小智', '再见', '你好', '号灯']

    try:
        stt_client = sttcli.SpeechToTextClient(username, password, on_recv_msg = handler_recv_msg, keywords = keyword_array, keywords_threshold = 0.1)
        raw_input()
    finally:
        stt_client.close()


if __name__ == "__main__":
    main()


