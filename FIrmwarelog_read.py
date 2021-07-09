#!/usr/bin/env python3
import codecs
import numpy as np
from argparse import ArgumentParser, SUPPRESS
import sys
import os

def build_argparser():
    parser = ArgumentParser(add_help=False)
    args = parser.add_argument_group('Options')
    args.add_argument('-h', '--help', action='help', default=SUPPRESS, help='Show this help message and exit.')
    args.add_argument("-m", "--logtxt", help="Required. Path to an .xml file with a trained model.",
                      type=str)
    return parser

def getlist(list1, str):
    if str in line:
        # print(line)
        a = line.split(str)
        b = a[-1:]  # 这是选取需要读取的位数
        b = b[0].split(' ')[0]
        list1.append(float(b))  # 将其添加在列表之中

def getmean(list1):
    if len(list1) > 0:
        mean = np.mean(list1)
        mean = round(mean , 2)
    else:
        mean = 0
    return mean
args = build_argparser().parse_args()
if args.logtxt is None:
    print('Path to logtxt is required: use -m.')
    sys.exit()
else:
    if os.path.exists(args.logtxt):
        txtfile = args.logtxt
    else:
        print('No such file or directory: ' + args.logtxt)
        sys.exit()
f = codecs.open(txtfile, mode='r', encoding='utf-8')  # 打开txt文件，以‘utf-8'编码读取
lines = f.readlines()  # 以行的形式进行读取文件
Phase2 = []
Phase1 = []
pose = []
kps = []
feature = []
JPEG = []
send_data = []

for line in lines:

    strPhase2 = 'Phase2 TimeMs:'
    strPhase1 = 'Phase1 TimeMs:'
    strpose = 'Pose elapsed '
    strkps = 'kps elapsed '
    strfeature = 'Feature elapsed '
    strJPEG = 'JPEG encode elapsed '
    strsend_data = 'Face data send elapsed '
    getlist(Phase1, strPhase1)
    getlist(Phase2, strPhase2)
    getlist(pose, strpose)
    getlist(kps, strkps)
    getlist(feature, strfeature)
    getlist(JPEG, strJPEG)
    getlist(send_data, strsend_data)

f.close()
send_datatime = getmean(send_data)
Phase1time = getmean(Phase1)
Phase2time = getmean(Phase2)
posetime = getmean(pose)
kpstime = getmean(kps)
featuretime = getmean(feature)
JPEGtime = getmean(JPEG)
print('检测人脸数量为：'+ str(len(Phase1)))
print(lPhase1time, posetime, kpstime, featuretime, JPEGtime, send_datatime, Phase2time)

