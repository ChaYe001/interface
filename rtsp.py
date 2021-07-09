#!/usr/bin/env python3
from argparse import ArgumentParser, SUPPRESS
import sys
import os
import cv2
import numpy as np
import time
import datetime

def main():

    # input_stream = 'rtsp://192.168.1.104:8554'
    input_stream = 'rtmp://192.168.1.123:1935/live/lina'
    # input_stream = 'rtmp://39.97.125.0:41935/live/lina'



    print(input_stream)

    # if input_stream.endswith('8554'):
    output_path = './output.avi'
    starttime = datetime.datetime.now()
    vc = cv2.VideoCapture(input_stream)
    # vc.set(cv2.CAP_PROP_MODE, cv2.CAP_MODE_YUYV)
    ret, frame = vc.read()
    w = int(vc.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(vc.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = vc.get(cv2.CAP_PROP_FPS)
    # format = vc.get(cv2.CAP_PROP_MONOCHROME)
    print(fps)

    # fourcc = cv2.VideoWriter_fourcc('H', '2', '6', '4')
    fourcc = cv2.VideoWriter_fourcc('I', '4', '2', '0')
    # fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
    # fourcc = cv2.VideoWriter_fourcc('H', 'E', 'V', 'C')
    vw = cv2.VideoWriter(output_path, fourcc, fps, (w, h), True)
    while ret:
        vw.write(frame)
        ret, frame = vc.read()
        cv2.namedWindow("frame", 0)
        cv2.resizeWindow("frame", 1280, 720)
        cv2.imshow('frame', frame)
        endtime = datetime.datetime.now()
        playtime = endtime - starttime
        # print(playtime.total_seconds())
        if cv2.waitKey(1) & 0xFF == ord('q'):
            cv2.destroyAllWindows()
            break
        # if playtime.total_seconds() >= 8:
        #     cv2.destroyAllWindows()
        #     break



if __name__ == '__main__':

    sys.exit(main())
