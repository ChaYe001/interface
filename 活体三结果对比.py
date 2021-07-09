#__author__ = 'Bo.Gu'
# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os
import numpy as np
import codecs
def caca(score, num):
    for filename in ['负样本20210708480眼镜5kpython.txt']:
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
            thre = st1r.split('结果：')[1][0:4]
            thre = float(thre)
            # print(thre)
            if '(D)' in st1r:
                if count <num and count1 < 5:
                    noresult += 1
                face += 1
                count = 0
                count1 = 1

                if 1>=float(thre) >= float(score):
                # if 2*thre**2/(thre**2 + score**2)-1 >= 0:
                #     # print('D_'+ str(thre))
                    count+=1
            else:
                count1+=1

                if count >= num:
                    continue

                if count1 > 5:
                    continue
                # if thre > 1:
                #     print(thre)
                if 1>=float(thre) >= float(score):
                    # print(thre)

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
        face = face - 1
        acc = realface / face *100
        # print(face, realface, noresult)
        acc = round(acc,2)
        score = round(score, 2)
        acc2 = noresult / face *100
        acc2 = round(acc2, 2)
        acc3 = (face - realface - noresult) / (face - noresult) * 100
        acc3 = round(acc3, 2)
        if filename in['正样本2021-07-07.txt', '正样本2021-07-07-1.txt','正样本20210708480眼镜python模拟.txt']:
            if acc >=0:
                print('阈值: ' + str(score) + '帧数：' + str(num) + '——真脸人数：' + str(realface) +
                      '——无结果数量：' + str(noresult) + '  正样本_' + str(filename) + '——正确率：' + str(acc))
        else:
            if acc <=100:
                print('阈值: ' + str(score) + '帧数：' + str(num) + '——假脸人数：' + str(face - realface - noresult) + '——无结果数量：' + str(noresult) +
                      '  负样本_' + str(filename) + '——正确率：' + str(100-acc-acc2) + '--无结果为假：' + str(100 -acc) + '--去除无结果：' + str(acc3))

        f.close()
    # print('---------------------------------------------------------------')
for score in range(60, 98):
    for num in range(1,3):
        caca(score/100, num)
# caca(0.7, 2)