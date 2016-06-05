# coding=utf-8
import os
import re

devicelist = os.popen("adb devices").readlines()
print devicelist

devicetxt = open("D:\\devices.txt", "wb")
for k,i in enumerate(devicelist):
    if 'device' in i and k!=0:
        a =  str(re.split("[\t]", i)[0])
        devicetxt.write(str(re.split("[\t]", i)[0])+"\n")
devicetxt.close()