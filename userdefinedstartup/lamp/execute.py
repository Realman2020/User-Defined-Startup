import subprocess
import time
import string
import sys

light_type = ""
while True:
    lamp_type = string.upper(raw_input("Enter test product type(e.g: HW/HWA/HWCA): "))
    lamp_type_list = ['HW', 'HWA', 'HWCA']
    if lamp_type not in lamp_type_list:
        print("Type Error, Try again\n")
        continue
    else:
        light_type = lamp_type
        break

if light_type == 'HW':
    try:
        print "\n" + "#" * 10 + "\t" + light_type + " User Defined Startup Test" + "\t" + "#" * 10
        subprocess.check_call("python %s" % "HW.py")
        time.sleep(5)
    except subprocess.CalledProcessError as e:
        print e
        sys.exit()
elif light_type == 'HWA':
    try:
        print "\n" + "#" * 10 + "\t" + light_type + " User Defined Startup Test" + "\t" + "#" * 10
        subprocess.check_call("python %s" % "HWA.py")
        time.sleep(5)
    except subprocess.CalledProcessError as e:
        print e
        sys.exit()
elif light_type == 'HWCA':
    try:
        print "\n" + "#" * 10 + "\t" + light_type + " User Defined Startup Test" + "\t" + "#" * 10
        subprocess.check_call("python %s" % "HWCA.py")
        time.sleep(5)
    except subprocess.CalledProcessError as e:
        print e
        sys.exit()
else:
    sys.exit()