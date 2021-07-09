#__author__ = 'Bo.Gu'
# -*- coding: utf-8 -*-
#!/usr/bin/python3
import os
import numpy as np
import codecs
def caca():
    for filename in ['data.txt', 'FaceList.txt']:
        f = codecs.open(filename,mode='r',encoding='utf-8')
        line = f.readlines()
        sumscore = 0
        sum_count = 0
        face = 0
        realface = 0
        for i in range(len(line)):
            d = line[i].split()
            arr = np.array(d)
            st1r = ''.join(arr)
            score = st1r.split('：')[1].split("(")[0]

            if '(D)' in st1r:
                if (sum_count != 0):
                    sumscore = sumscore / sum_count

                    print(str(sumscore))
                T_quan = 0
                T_count = 0
                sumscore = 0
                sum_count = 0

                D_quan = 1
                sumscore = sumscore + float(score) * D_quan
                sum_count = sum_count + D_quan


            else:
                T_quan = 1 - 0.1 * T_count
                sumscore = sumscore + float(score) * T_quan
                sum_count = sum_count + T_quan

                T_count += 1
        if (sum_count != 0):
            sumscore = sumscore / sum_count

            print(str(sumscore))
        print('---------------------------------------------------------------')
caca()
