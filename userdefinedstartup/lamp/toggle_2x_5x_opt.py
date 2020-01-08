#!/usr/bin/python2.7
# -*- coding:utf_8 -*-
# Author = 'Simon Huang'

# This script is only for Hue White Ambiance Product User Defined Feature Testing


import requests
import sys
import time
import datetime
import string
import json
import ConfigParser
import ippower

cfg = ConfigParser.ConfigParser()
cfg.read("bridge_uds.cfg")
bridge_ip = cfg.get('Config', 'BridgeIp')
bridge_user = cfg.get('Config', 'ValidUser')
default_bri = 254
default_ct = 366
light = 6
light_url = "http://" + bridge_ip + "/api" + bridge_user + "/lights/" + str(light)
state_url = "http://" + bridge_ip + "/api" + bridge_user + "/lights/" + str(light) + "/state"


def uds_set(effects):
    url_uds = light_url + "/config/config"
    response = requests.put(url_uds, effects).text
    return response


def uds_get():
    res_json = requests.get(light_url)
    res = res_json.json()
    bri = res['state']['bri']
    print("Light's Bri is: %d" % bri)
    return bri


def toggle_2x():
    print("execute 2x toggle to revert back to default settings...")
    requests.put(state_url, '{"on":true, "bri":100}')
    time.sleep(1)
    effect = '{"startup": {"mode": "powerfail"}}'
    uds_set(effect)
    res_text = requests.put(state_url, '{"on":false}').text
    res = str(res_text)
    time.sleep(10)
    if 'success' in res:
        ippower.smart_power(1, 2)
        time.sleep(30)
        ippower.smart_power(1, 1)
        time.sleep(2)
        ippower.smart_power(1, 2)
        time.sleep(23)
        ippower.smart_power(1, 1)
    time.sleep(15)
    bri = uds_get()
    if bri == default_bri:
        print('\033[1;32m 2x toggle PASS \033[0m\n')
    else:
        print('\033[1;31m 2x toggle FAIL \033[0m\n')
    time.sleep(3)


def toggle_5x():
    print("execute 5x toggle to FN lamp ...")
    requests.put(state_url, '{"on":true, "bri":125}')
    effect = '{"startup": {"mode": "powerfail"}}'
    uds_set(effect)
    time.sleep(10)
    print("1th toggle")
    ippower.smart_power(1, 2)
    time.sleep(5)
    ippower.smart_power(1, 1)
    time.sleep(2)
    print("2th toggle")
    ippower.smart_power(1, 2)
    time.sleep(5)
    ippower.smart_power(1, 1)
    time.sleep(2)
    print("3th toggle")
    ippower.smart_power(1, 2)
    time.sleep(5)
    ippower.smart_power(1, 1)
    time.sleep(2)
    print("4th toggle")
    ippower.smart_power(1, 2)
    time.sleep(5)
    ippower.smart_power(1, 1)
    time.sleep(2)
    print("5th toggle")
    ippower.smart_power(1, 2)
    time.sleep(5)
    ippower.smart_power(1, 1)
    time.sleep(60)
    res_json = requests.get(light_url)
    res = res_json.json()
    status = res['state']['reachable']
    if status is False:
        requests.post("http://" + bridge_ip + "/api" + bridge_user + "/lights/")
        time.sleep(40)
        res_json = requests.get(light_url)
        res = res_json.json()
        mode = res['config']['startup']['mode']
        if mode == 'safety':
            print('\033[1;32m 5x toggle PASS \033[0m\n')
        else:
            print('\033[1;31m 5x toggle FAIL \033[0m\n')
    else:
        return
    time.sleep(3)


if __name__ == "__main__":
        try:
            toggle_2x()
            # toggle_5x()
        except Exception, err:
            print(err)
            sys.exit()