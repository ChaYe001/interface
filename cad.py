#!/usr/bin/env python3
# -*- coding: utf-8 -*-

'''
本模块功能：输出简易的轴类零件
要求：
1.输入轴段数
2.输入各段的长度、半径
输出：
CAD轴的图
'''

# 导入pyautocad库
from pyautocad import Autocad, APoint


# 连接，在CAD的命令窗口里显示 连接成功
aCad = Autocad(create_if_not_exists=True)
# aCad.prompt("Connect python successfully")

# 定义空列表和孔字典，我定义的比较乱 ￣へ￣
ls = []
ls1 = []
ls2 = []
dc = {}
dc1 = {}
X = []
Y = []
Z = []
Q = []

# 初始点定位(0,0)，由于在CAD里拖动比较方便，就不再让用户输入了
x1 = 0
y1 = 0
p1 = APoint(x1, y1)

# 按照轴段个数，给代表X轴和Y轴的列表传递值
num = int(input("轴段个数："))
for i in range(num):
    x = int(input("第{}段长度：".format(i+1)))
    y = int(input("第{}段直径：".format(i+1)))
    ls.append(x)
    x1 += x
    ls1.append(x1)
    ls2.append(y)
    Q.append(-y)
    Q.append(-y)

for j in range(num):
    X.append(ls1[j]-ls[j])
    Y.append(ls2[j])
    Y.append(ls2[j])
for j in range(num):
    Z.append(X[j])
    Z.append(ls1[j])

# 绘制上半部分的线段
for k in range(len(Y)):
    if k != 0:
        aCad.model.AddLine(APoint(Z[k], Y[k]), APoint(Z[k-1], Y[k-1]))
    else:
        aCad.model.AddLine(APoint(Z[k], Y[k]), p1)
        aCad.model.AddLine(APoint(Z[k], -Y[k]), p1)
        p_first2 = APoint(Z[k], -Y[k])

# 绘制下半部分的线段
for k in range(len(Y)):
    if k != 0:
        aCad.model.AddLine(APoint(Z[k], Q[k]), APoint(Z[k-1], Q[k-1]))
    else:
        aCad.model.AddLine(APoint(Z[k], Q[k]), p1)
        aCad.model.AddLine(APoint(Z[k], -Q[k]), p1)
        p_first2 = APoint(Z[k], -Q[k])

# 绘制中间的线段
for c in range(len(Y)):
    if c < len(Y)-1:
        if Y[c] != Y[c + 1]:
            aCad.model.AddLine(APoint(Z[c], Y[c]), APoint(Z[c], -min(Y[c], Y[c+1])))
    else:
        aCad.model.AddLine(APoint(Z[c], Y[c]), APoint(Z[c], -Y[c]))
        p_last = APoint(Z[c], -Y[c])

