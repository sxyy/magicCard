# coding=utf-8
import os
import re

# devicelist = os.popen("adb devices").readlines()
# print devicelist
#
# devicetxt = open("D:\\devices.txt", "wb")
# for k,i in enumerate(devicelist):
#     if 'device' in i and k!=0:
#         a =  str(re.split("[\t]", i)[0])
#         devicetxt.write(str(re.split("[\t]", i)[0])+"\n")
# devicetxt.close()

import ConfigParser
import json

config = ConfigParser.ConfigParser()
config.read('1.ini')
# try:
#     out_put = config.get('ok', 'sss')
# except ConfigParser.NoOptionError, ConfigParser.NoSectionError:
#     print 'heheh'
# print out_put
# out_put_list = out_put.split('&&')
# print out_put_list
import time
print int(time.time())
endtime = int('1524998749')
x = time.localtime(endtime)
print time.strftime('%Y-%m-%d %H:%M:%S', x)
# mystr = '{"code":0,"desc":"sucess","dui_bits":0,"free_ts":1465094923,"hlj":2,"huan_dian":150,"need_callback":null,"paopao":0,"vt_js":2,"vt_shui":0,"vt_xd":0,"vt_xs":0}'
# mystr = '<hoewaskdjaskj>asdasdjk,sajkdasjdk{"a":0}'
# # try:
# mystr_json = json.loads(mystr)
# for out_put_item in out_put_list:
#     # print out_put_item
#     out_put_item_list = out_put_item.split('#')
#     # print out_put_item_list
#     # print out_put_item_list[0]
#     if out_put_item_list[0] in mystr_json:
#         print out_put_item_list[1] + ':' + str(mystr_json[out_put_item_list[0]])
# except ValueError :

