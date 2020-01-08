#!/usr/bin/python2.7
# -*- coding: utf-8 -*-

import requests
import time


def smart_power(ctrl_port, ctrl_type):
    # 电源地址
    power_ip = '192.168.1.10'

    # 电源端口号
    # power_port = raw_input("Enter power port(1 or 2): ")
    power_port = ctrl_port

    # 电源控制类型，1=开启，2=关闭，3=重启
    # ctrl_kind = raw_input("Enter power control kind(1=开启, 2=关闭, 3=重启): ")
    ctrl_kind = ctrl_type

    # 电源登录的用户名与密码
    username = 'admin'
    password = 'admin'
    pre_url = 'http://192.168.1.10/'

    # 获取登录Cookie
    url_login = pre_url + 'login_auth.csp'
    paras = {'auth_user': username, 'auth_passwd': password}
    req = requests.post(url=url_login, data=paras)
    cookie = req.headers['Set-Cookie']

    # 开关控制
    url = pre_url + 'out_ctrl.csp?port=' + str(power_port) + '&ctrl_kind=' + str(ctrl_kind)
    headers = {'Cookie': cookie}
    response = requests.get(url=url, headers=headers)

    #获取开关返回状态
    if response.status_code == 200:
        print("\033[1;34m Smart Power Setting Success!\033[0m")


def power_reset():
    smart_power(1, 2)
    time.sleep(20)
    smart_power(1, 1)
    time.sleep(1)



