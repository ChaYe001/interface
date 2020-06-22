#__author__ = 'Bo.Gu' 
# -*- coding: utf-8 -*-   
#!/usr/bin/python3
import os
import time
import datetime
import numpy as np
import codecs
facefile = "D:\工作内容\测试记录\G26\滑油盖测试集\summary\summary\负样本\\"
piclist = os.listdir(facefile)
f = codecs.open('data.txt',mode='r',encoding='utf-8')
line = f.readlines()
d = []
for i in range(len(line)):
    d = line[i].split()
    arr = np.array(d)
    str = ''.join(arr)
    print(str)
    # print(d)
    # for okname in piclist:
    #     if okname.endswith('.jpg'):
    #         # okname = okname.split('.jpg')
    #         # print(okname)
    #         if d == okname:
    #             print(d[0])
    os.system('mv ' +facefile + str + ' ' + 'D:\工作内容\测试记录\G26\滑油盖测试集\summary\summary\检测错误\\' +str)
# def file_name(fileA_dir):
#     L=[]
#     for root, dirs, files in os.walk(file_dir):
#         for file in files:
#             if os.path.splitext(file)[1] == '.jpg':
#                 L.append(os.path.join(root, file))
#                 os.
#     return L
#
#
# if __name__ == '__main__':
#     L = file_name("./")
#     for each in L:
#         print (each)
#
        
