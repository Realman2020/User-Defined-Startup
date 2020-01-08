#!/usr/bin/python2.7
# -*- coding:utf_8 -*-
# Author = 'Simon Huang'

# This script is only for Hue White Color Ambiance Product User Defined Feature Testing

import operator
import requests
import sys
import time
import string
import json
import ConfigParser
import ippower

cfg = ConfigParser.ConfigParser()
cfg.read("bridge_uds.cfg")
bridge_ip = cfg.get('Config', 'BridgeIp')
bridge_user = cfg.get('Config', 'ValidUser')
fn_bridge_ip = cfg.get('Config', 'FN_BridgeIP')
fn_bridge_user = cfg.get('Config', 'FN_ValidUser')

default_bri = float(cfg.get('Config', 'default_bri'))
default_ct = float(cfg.get('Config', 'default_ct'))
default_xc = float(cfg.get('Config', 'default_xc'))
default_yc = float(cfg.get('Config', 'default_yc'))
time_window = float(cfg.get('Config', 'time_window'))
time_between_case = float(cfg.get('Config', 'time_between_case'))
toggle_2x_switch_on = float(cfg.get('Config', 'toggle_2x_switch_on'))
toggle_2x_switch_off = float(cfg.get('Config', 'toggle_2x_switch_off'))

light_list = json.loads(cfg.get('Config', 'Light_Number'))
sn = cfg.get('Config', 'Serial_Number').split(',')
lamp_dict = dict(zip(light_list, sn))
sorted_lamp_dict = sorted(lamp_dict.items())

on_time = int(raw_input("enter power on last time: "))

print("\nLight Number List:%s" % light_list)
print("Serial Number List:%s" % sn)
print('Light Number and related Serial Number:' + str(sorted_lamp_dict)+'\n')
time.sleep(3)


def uds_set(effects):
    url_uds = "http://" + bridge_ip + "/api" + bridge_user + "/lights/" + str(light) + "/config/config"
    response = requests.put(url_uds, effects).text
    time.sleep(8)
    return response


def uds_get():
    url_get = "http://" + bridge_ip + "/api" + bridge_user + "/lights/" + str(light)
    res_json = requests.get(url_get)
    res = res_json.json()
    bri = res['state']['bri']
    ct = res['state']['ct']
    # xc = float("%.2f" % res['state']['xy'][0])
    # yc = float("%.2f" % res['state']['xy'][1])
    # print("Light's bri = %d, xc = %.2f, yc = %.2f" % (bri, ct))
    print("Light's bri = %d, ct = %.2f" % (bri, ct))
    return bri, ct
    # print("Light's bri = %d, xc = %.2f, yc = %.2f" % (bri, xc, yc))
    # return bri, xc, yc


def toggle2x(light):
    print("Executing case ID IPJ-16689: *** 2x Toggle ***")
    requests.put("http://" + bridge_ip + "/api" + bridge_user + "/lights/" + str(light) + "/state", '{"bri":1}')
    time.sleep(5)
    effect = '{"startup": {"mode": "powerfail"}}'
    uds_set(effect)
    res_text = requests.put("http://" + bridge_ip + "/api" + bridge_user + "/lights/" + str(light) + "/state", '{"on":false}').text
    time.sleep(7*2)
    res = str(res_text)
    if 'success' in res:
        ippower.smart_power(1, 2)
        time.sleep(20)
        ippower.smart_power(1, 1)
        time.sleep(on_time)
        print("discharge time is %d" % (25-on_time))
        ippower.smart_power(1, 2)
        time.sleep(20)
        ippower.smart_power(1, 1)
    else:
        return
    time.sleep(10)
    bri, ct = uds_get()
    # if bri == default_bri and xc == default_xc and yc == default_yc:
    if bri == default_bri and ct == default_ct:
        print('\033[1;32m 2 times toggling PASS \033[0m\n')
    else:
        print('\033[1;31m 2 times toggling FAIL \033[0m\n')


if __name__ == "__main__":
    ippower.smart_power(1, 1)
    for light in light_list:
        print('\033[1;42m Light Number:[%s] is running\033[0m\n' % light)
        try:
            toggle2x(light)
        except Exception, err:
            print(err)
            sys.exit()