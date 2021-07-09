#__author__ = 'Bo.Gu' 
# -*- coding: utf-8 -*-   
#!/usr/bin/python3
import os
import numpy as np
import codecs
facefile = "D:\工作内容\测试记录\样本\清晰度0\清晰度25添加人脸\ErroPicture\清晰度40过滤\\"
piclist = os.listdir(facefile)
f = codecs.open('data.txt',mode='r',encoding='utf-8')
line = f.readlines()
d = []
for i in range(len(line)):
    d = line[i].split()
    arr = np.array(d)
    str = ''.join(arr)
    print(str)
    os.system('mv ' +facefile + str + ' ' + 'D:\工作内容\测试记录\样本\清晰度0\清晰度25添加人脸\ErroPicture\清晰度40过滤\sanwu\\' +str)
