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

light_list = json.loads(cfg.get('Config', 'Light_Number'))
sn = cfg.get('Config', 'Serial_Number').split(',')
lamp_dict = dict(zip(light_list, sn))
sorted_lamp_dict = sorted(lamp_dict.items())

default_bri = 254
default_xc = 0.46
default_yc = 0.41

print("\nLight Number List:%s" % light_list)
print("Serial Number List:%s" % sn)
print('Light Number and related Serial Number:' + str(sorted_lamp_dict)+'\n')
time.sleep(3)


def uds_set(effects):
    url_uds = "http://" + bridge_ip + "/api/" + bridge_user + "/lights/" + str(light) + "/config/"
    response = requests.put(url_uds, effects).text
    time.sleep(3)
    print response
    return response


def uds_get():
    url_get = "http://" + bridge_ip + "/api/" + bridge_user + "/lights/" + str(light)
    res_json = requests.get(url_get)
    res = res_json.json()
    bri = res['state']['bri']
    xc = float("%.2f" % res['state']['xy'][0])
    yc = float("%.2f" % res['state']['xy'][1])
    print("Light's Bri = %d, XC = %.2f, YC = %.2f" % (bri, xc, yc))
    return bri, xc, yc


def IPJ_16685(light):
    print("Executing case ID IPJ-16685 *** Default Settings Check ***")
    time.sleep(3)
    bri, xc, yc = uds_get()
    if bri == 254 and xc == 0.46 and yc == 0.41:
        print('\033[1;32m IPJ-16685: PASS \033[0m\n')
    else:
        print('\033[1;31m IPJ-16685: FAIL \033[0m\n')
    time.sleep(3)


def IPJ_16686(light):
    print("Executing case ID IPJ-16686 *** Safety Mode Recall ***")
    effect = '{"startup": {"mode": "safety"}}'
    res_text = uds_set(effect)
    res = str(res_text)
    if 'success' in res:
        print("Power Cycle Lamp and Wait 15 seconds")
        ippower.power_reset()
    time.sleep(15)
    bri, xc, yc = uds_get()
    if bri == 254 and xc == 0.46 and yc == 0.41:
        print('\033[1;32m IPJ-16686: PASS \033[0m\n')
    else:
        print('\033[1;31m IPJ-16686: FAIL \033[0m\n')
    time.sleep(3)


def IPJ_16687(light):
    print("Executing case ID IPJ-16687 *** Power Fail Mode Recall ***")
    effect = '{"startup": {"mode": "powerfail"}}'
    uds_set(effect)
    res_text = requests.put("http://"+bridge_ip+"/api/"+bridge_user+"/lights/"+str(light)+"/state",
                            '{"bri":100, "xy":[0.6915, 0.3083]}').text
    res = str(res_text)
    if 'success' in res:
        time.sleep(10)
        print("Power Cycle Lamp and Wait 15 seconds")
        ippower.power_reset()
    time.sleep(15)
    bri, xc, yc = uds_get()
    if bri == 100 and xc == 0.69 and yc == 0.31:
        print('\033[1;32m IPJ-16687: PASS \033[0m\n')
    else:
        print('\033[1;31m IPJ-16687: FAIL \033[0m\n')
    time.sleep(3)


def IPJ_16688(light):
    print("Executing case ID IPJ-16688 *** Custom Mode Recall ***")
    effect = '{"startup": {"mode": "custom", "customsettings": {"bri":100, "xy":[0.1658, 0.5369]}}}'
    res_text = uds_set(effect)
    res = str(res_text)
    if 'success' in res:
        print("Power Cycle Lamp and Wait 15 seconds")
        ippower.power_reset()
    time.sleep(15)
    bri, xc, yc = uds_get()
    if bri == 100 and xc == 0.17 and yc == 0.54:
        print('\033[1;32m IPJ-16688: PASS \033[0m\n')
    else:
        print('\033[1;31m IPJ-16688: FAIL \033[0m\n')
    time.sleep(3)


def IPJ_16689(light):
    print("Executing case ID IPJ-16689: *** 2x Toggle ***")
    requests.put("http://" + bridge_ip + "/api/" + bridge_user + "/lights/" + str(light) + "/state", '{"on":true, "bri":30}')
    time.sleep(3)
    effects = ['{"startup": {"mode": "safety"}}',
               '{"startup": {"mode": "powerfail"}}',
               '{"startup": {"mode": "custom", "customsettings": {"bri":100, "xy":[0.17, 0.7]}}}']
    for effect in effects:
        uds_set(effect)
        effect_dict = json.loads(effect)
        if effect_dict['startup']['mode'] == 'powerfail':
            # print effect_dict
            res_text = requests.put("http://" + bridge_ip + "/api/" + bridge_user + "/lights/" + str(light) + "/state", '{"on":false}').text
        else:
            res_text = requests.put("http://" + bridge_ip + "/api/" + bridge_user + "/lights/" + str(light) + "/state", '{"bri":150}').text
        res = str(res_text)
        time.sleep(10)
        if 'success' in res:
            ippower.smart_power(1, 2)
            time.sleep(30)
            ippower.smart_power(1, 1)
            time.sleep(5)
            ippower.smart_power(1, 2)
            time.sleep(30)
            ippower.smart_power(1, 1)
        else:
            print("clip put error")
            return
        time.sleep(15)
        bri, xc, yc = uds_get()
        if bri == default_bri and xc == default_xc and yc == default_yc:
            continue
        else:
            print('\033[1;31m IPJ-16689: FAIL \033[0m\n')
            return
    print('\033[1;32m IPJ-16689: PASS \033[0m\n')
    time.sleep(3)



def IPJ_16690(light):
    print("Executing case ID IPJ-16690 *** OTAU not change uds parameters ***")
    print('\033[1;33m IPJ-16690: Please check during OTAU \033[0m\n')
    time.sleep(3)


def IPJ_16691(light):
    print("Executing case ID IPJ-16691 *** Remote Reset Function Test ***")
    print("Scan lamp %s with bridge out of Zigbee network, wait 60 seconds" % lamp_dict[light])
    requests.post("http://" + fn_bridge_ip + "/api/" + fn_bridge_user + "/lights", '{"deviceid": ["%s"]}' % lamp_dict[light])
    time.sleep(60)
    print("Scan lamp with bridge in Zigbee network, wait 90 seconds")
    requests.post("http://" + bridge_ip + "/api/" + bridge_user + "/lights", '{"deviceid": ["%s"]}' % lamp_dict[light])
    time.sleep(90)
    bri, xc, yc = uds_get()
    if bri == 254 and xc == 0.46 and yc == 0.41:
        print('\033[1;32m IPJ-16691: PASS \033[0m\n')
    else:
        print('\033[1;31m IPJ-16691: FAIL \033[0m\n')


def IPJ_16693(light):
    print("Executing case ID IPJ-16693 *** Attribute read and write ***")
    mode_list = ['safety', 'powerfail', 'custom']
    effect = '{"startup": {"mode": "safety"}}'
    res_text = uds_set(effect)
    res = str(res_text)
    print(res)
    if 'success' in res:
        print("Write attribute success")
    else:
        print("Write attribute error")
    res_get = json.loads(requests.get("http://" + bridge_ip + "/api/" + bridge_user + "/lights/" + str(light)).text)
    if res_get['config']['startup']['mode'] in mode_list:
        print("Read attribute success")
        print('\033[1;32m IPJ-16689: PASS \033[0m\n')
    else:
        print("Read attribute error")
    time.sleep(3)


def IPJ_16694(light):
    print("Executing case ID IPJ-16694 *** Reachable False Function Test ***")
    time.sleep(3)
    effect1 = '{"startup": {"mode": "safety"}}'
    uds_set(effect1)
    time.sleep(3)
    print("Power OFF Lamp within 5 seconds")
    ippower.smart_power(1, 2)
    time.sleep(3)
    effect2 = '{"startup": {"mode": "custom", "customsettings": {"bri":1, "xy":[0.1658, 0.5369]}}}'
    res_text = uds_set(effect2)
    res = str(res_text)
    time.sleep(3)
    if 'success' in res:
        print("Power ON Lamp")
        ippower.smart_power(1, 1)
    time.sleep(15)
    bri, xc, yc = uds_get()
    if bri == 254 and xc == 0.46 and yc == 0.41:
        print('\033[1;32m IPJ-16694: PASS \033[0m\n')
    else:
        print('\033[1;31m IPJ-16694: FAIL \033[0m\n')
    time.sleep(3)


def IPJ_16695(light):
    print("Executing case ID IPJ-16695 *** Mode Validation Test ***")
    time.sleep(3)
    effect = '{"startup": {"mode": "test"}}'
    res_text = str(uds_set(effect))
    res = str(res_text)
    if 'error' in res:
        print('\033[1;32m IPJ-16695: PASS \033[0m\n')
    else:
        print('\033[1;31m IPJ-16695: FAIL \033[0m\n')
    time.sleep(3)


def IPJ_16696(light):
    print("Executing case ID IPJ-16696 *** Attribute ON Test ***")
    time.sleep(3)
    effect = '{"startup": {"mode": "custom", "customsettings": {"on":false}}}'
    res_text = str(uds_set(effect))
    res = str(res_text)
    if 'error' in res:
        print('\033[1;32m IPJ-16696: PASS \033[0m\n')
    else:
        print('\033[1;31m IPJ-16696: FAIL \033[0m\n')
    time.sleep(3)


def IPJ_16697(light):
    print("Executing case ID IPJ-16697 *** Attribute None Test ***")
    time.sleep(3)
    effect = '{"startup": {"mode": "powerfail"}}'
    uds_set(effect)
    requests.put("http://" + bridge_ip + "/api/" + bridge_user + "/lights/" + str(light) + "/state",
                 '{"bri":254,"xy":[0.1658, 0.5369]}')
    time.sleep(10)
    url = "http://" + bridge_ip + "/api/" + bridge_user + "/lights/" + str(light)
    res_json = requests.get(url)
    res = res_json.json()
    mode = res['config']['startup']['mode']
    time.sleep(3)
    if mode == 'powerfail':
        effect = '{"startup": {"mode": "custom", "customsettings": {}}}'
        uds_set(effect)
        print('Attribute {"customsettings":{}} configured successfully')
        time.sleep(3)
    print("Power Cycle Lamp and Wait 15 seconds")
    ippower.power_reset()
    time.sleep(15)
    bri, xc, yc = uds_get()
    if bri == 254 and xc == 0.46 and yc == 0.41:
        print('\033[1;32m IPJ-16697: PASS \033[0m\n')
    else:
        print('\033[1;31m IPJ-16697: FAIL \033[0m\n')
    time.sleep(3)


def IPJ_16698(light):
    print("Executing case ID IPJ-16698 *** Actual Status Test ***")
    print('\033[1;31m IPJ-16698: Not implemented by Software Team \033[0m\n')
    time.sleep(3)


def IPJ_16699(light):
    print("Executing case ID IPJ-16699 *** Flicker Verification ***")
    print("Please observe flicker by eyes manually !!!")
    effects = ['{"startup": {"mode": "custom", "customsettings": {"bri":1,"xy":[0.69, 0.31]}}}',
               '{"startup": {"mode": "custom", "customsettings": {"bri":1,"xy":[0.17, 0.7]}}}',
               '{"startup": {"mode": "custom", "customsettings": {"bri":1,"xy":[0.15, 0.05]}}}']
    for effect in effects:
        uds_set(effect)
        time.sleep(3)
        ippower.smart_power(1,2)
        time.sleep(30)
        ippower.smart_power(1,1)
        time.sleep(25)
        bri, xc, yc = uds_get()
        effect_dict = json.loads(effect)
        if bri == effect_dict['startup']['customsettings']['bri'] and [xc,yc] == effect_dict['startup']['customsettings']['xy']:
            continue
        else:
            print('\033[1;31m IPJ-16699: FAIL \033[0m\n')
            return
    print("\033[1;32m IPJ-16699: PASS \033[0m\n")
    time.sleep(3)


def IPJ_16700(light):
    print("Executing case ID IPJ-16700 *** 5x toggle to factory new lamp ***")
    requests.put("http://"+bridge_ip+"/api/"+bridge_user+"/lights/"+str(light)+"/state", '{"on":true, "bri":254, "xy":[0.17,0.7]}')
    effect = '{"startup": {"mode": "powerfail"}}'
    uds_set(effect)
    time.sleep(10)
    print("1th toggle")
    ippower.smart_power(1, 2)
    time.sleep(7)
    ippower.smart_power(1, 1)
    time.sleep(2)
    print("2th toggle")
    ippower.smart_power(1, 2)
    time.sleep(7)
    ippower.smart_power(1, 1)
    time.sleep(2)
    print("3th toggle")
    ippower.smart_power(1, 2)
    time.sleep(7)
    ippower.smart_power(1, 1)
    time.sleep(2)
    print("4th toggle")
    ippower.smart_power(1, 2)
    time.sleep(7)
    ippower.smart_power(1, 1)
    time.sleep(2)
    print("5th toggle")
    ippower.smart_power(1, 2)
    time.sleep(7)
    ippower.smart_power(1, 1)
    time.sleep(60)
    res_json = requests.get("http://" + bridge_ip + "/api/" + bridge_user + "/lights/" + str(light))
    res = res_json.json()
    status = res['state']['reachable']
    if status is False:
        requests.post("http://" + bridge_ip + "/api/" + bridge_user + "/lights/")
        time.sleep(60)
        res_json = requests.get("http://" + bridge_ip + "/api/" + bridge_user + "/lights/" + str(light))
        res = res_json.json()
        mode = res['config']['startup']['mode']
        if mode == 'safety':
            print('\033[1;32m IPJ-16700: PASS \033[0m\n')
        else:
            print('\033[1;31m IPJ-16700: FAIL \033[0m\n')
    else:
        return
    time.sleep(3)


def IPJ_16701(light):
    print("Executing case ID IPJ-16701 *** Living Color Test ***")
    print('\033[1;33m IPJ-16701: Manual test based on product feature design\033[0m\n')
    time.sleep(3)


def IPJ_16702(light):
    print("Executing case ID IPJ-16702 *** Hue Go Test ***")
    print('\033[1;33m IPJ-16702: Manual test based on product feature design\033[0m\n')
    time.sleep(3)


def IPJ_16703(light):
    print("Executing case ID IPJ-16703 *** Transition time <7s not change startup setting***")
    effect = '{"startup": {"mode": "powerfail"}}'
    uds_set(effect)
    time.sleep(3)
    requests.put("http://" + bridge_ip + "/api/" + bridge_user + "/lights/" + str(light) + "/state",
                 '{"bri":254,"xy":[0.1700, 0.7000]}')
    bri, xc, yc = uds_get()
    time.sleep(10)
    if bri == 254 and xc == 0.17 and yc == 0.70:
        requests.put("http://"+bridge_ip+"/api/"+bridge_user+"/lights/"+str(light)+"/state", '{"bri":1, "transitiontime":600}')
        print("Start transition")
    time.sleep(2)
    print("IPJ-16703: Power cycle lamp and wait 15 seconds")
    ippower.smart_power(1,2)
    time.sleep(15)
    ippower.smart_power(1,1)
    time.sleep(15)
    bri, xc, yc = uds_get()
    if bri == 254 and xc == 0.17 and yc == 0.70:
        print('\033[1;32m IPJ-16703: PASS \033[0m\n')
    else:
        print('\033[1;31m IPJ-16703: FAIL \033[0m\n')


def IPJ_16704(light):
    print("Executing case ID IPJ-16704 *** Transition time >7s change startup setting***")
    effect = '{"startup": {"mode": "powerfail"}}'
    uds_set(effect)
    time.sleep(3)
    requests.put("http://" + bridge_ip + "/api/" + bridge_user + "/lights/" + str(light) + "/state",
                 '{"bri":1, "xy":[0.1700, 0.7000]}')
    bri, xc, yc = uds_get()
    time.sleep(10)
    if bri == 1 and xc == 0.17 and yc == 0.70:
        requests.put("http://"+bridge_ip+"/api/"+bridge_user+"/lights/"+str(light)+"/state",
                     '{"bri":254, "xy":[0.6915, 0.3083], "transitiontime":600}')
        print("Start transition")
    time.sleep(7*2)
    print("IPJ-16704: Power cycle lamp and wait 15 seconds")
    ippower.power_reset()
    time.sleep(15)
    bri, xc, yc = uds_get()
    if bri == 254 and xc == 0.69 and yc == 0.31:
        print('\033[1;32m IPJ-16704: PASS \033[0m\n')
    else:
        print('\033[1;31m IPJ-16704: FAIL \033[0m\n')


def uds_execute(lamp):
    IPJ_16686(lamp)
    IPJ_16685(lamp)
    IPJ_16687(lamp)
    IPJ_16688(lamp)
    IPJ_16689(lamp)
    IPJ_16690(lamp)
    IPJ_16693(lamp)
    IPJ_16694(lamp)
    IPJ_16695(lamp)
    IPJ_16696(lamp)
    IPJ_16697(lamp)
    IPJ_16699(lamp)
    # IPJ_16700(lamp)
    # IPJ_16701(lamp)
    # IPJ_16702(lamp)
    IPJ_16703(lamp)
    IPJ_16704(lamp)
    # IPJ_16691(lamp)


if __name__ == "__main__":

    for light in light_list:
        print('\033[1;42m Light Number:[%s] is running\033[0m\n' % light)
        try:
            uds_execute(light)
            time.sleep(5)
        except Exception, err:
            print(err)
            sys.exit()