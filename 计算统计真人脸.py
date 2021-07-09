#__author__ = 'Bo.Gu'
# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os
import numpy as np
import codecs
def caca(score, num):
    for filename in ['Trueface_0603_333.txt']:
        f = codecs.open(filename,mode='r',encoding='utf-8')
        line = f.readlines()
        count1 = 0
        count = 0.0
        face = 1
        noresult = -1
        realface = 0
        for i in range(len(line)):
            d = line[i].split()
            arr = np.array(d)
            st1r = ''.join(arr)
            thre = st1r.split('：')[1].split("(")[0]
            thre = float(thre)
            # print(thre)
            if '(D)' in st1r:
                if count <num and count1 < 5:
                    noresult += 1
                face += 1
                count = 0
                count1 = 1

                if float(thre) >= float(score):
                # if 2*thre**2/(thre**2 + score**2)-1 >= 0:
                #     # print('D_'+ str(thre))
                    count+=1
            else:
                count1+=1

                if count >= num:
                    continue

                if count1 > 5:
                    continue
                if float(thre) >= float(score):
                # if 2*thre**2/(thre**2 + score**2)-1 >= 0:
                    # print('T_'+ str(thre))
                    count += 1
            # print(count)
            if count >= num:
                # print(thre)
                realface+=1
                continue
        if count <num and count1 < 5:
            noresult += 1
        acc = realface / face *100
        # print(face)
        acc = round(acc,2)
        score = round(score, 2)
        if filename == 'Trueface_0603pthone.txt' or filename == 'Trueface_0531.txt':
            if acc >=80:
                print('阈值: ' + str(score) + '帧数：' + str(num) + '——真脸人数：' + str(realface) + '——无结果数量：' + str(noresult) + '  正样本_' + str(filename) + '——正确率：' + str(acc))
        else:
            if acc <=20:
                print('阈值: ' + str(score) + '帧数：' + str(num) + '——假脸人数：' + str(face - realface) + '——无结果数量：' + str(noresult) + '  负样本_' + str(filename) + '——正确率：' + str(100-acc))

        f.close()
    # print('---------------------------------------------------------------')
for score in range(30, 98):
    for num in range(2,5):
        caca(score/100, num)
# caca(0.7, 2)
# caca(0.93, 9)
# caca(0.9, 3)
# caca(0.88, 9)
# caca(0.83, 9)
# caca(0.8, 9)
# caca(0.7, 9)
# caca(0.6, 9)
#
# caca(0.93, 8)
# caca(0.9, 8)
# caca(0.88, 8)
# caca(0.83, 8)
# caca(0.8, 8)
# caca(0.7, 8)
# caca(0.6, 8)
#
# caca(0.93, 7)
# caca(0.9, 7)
# caca(0.88, 7)
# caca(0.83, 7)
# caca(0.8, 7)
# caca(0.7, 7)
# caca(0.6, 7)
#
# caca(0.93, 6)
# caca(0.9, 6)
# caca(0.88, 6)
# caca(0.83, 6)
# caca(0.8, 6)
# caca(0.7, 6)
# caca(0.6, 6)
#
# caca(0.93, 5)
# caca(0.9, 5)
# caca(0.88, 5)
# caca(0.83, 5)
# caca(0.8, 5)
# caca(0.7, 5)
# caca(0.6, 5)
#
# caca(0.93, 4)
# caca(0.9, 4)
# caca(0.88, 4)
# caca(0.83, 4)
# caca(0.8, 4)
# caca(0.7, 4)
# caca(0.6, 4)
#
# caca(0.93, 3)
# caca(0.9, 3)
# caca(0.88, 3)
# caca(0.83, 3)
# caca(0.8, 3)
# caca(0.7, 3)
# caca(0.6, 3)
#
# caca(0.93, 2)
# caca(0.9, 2)
# caca(0.88, 2)
# caca(0.83, 2)
# caca(0.8, 2)
# caca(0.7, 2)
# caca(0.6, 2)