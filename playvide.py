#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from argparse import ArgumentParser, SUPPRESS
import sys
import os
import cv2
import numpy as np
import time
import datetime
def build_argparser():
    parser = ArgumentParser(add_help=False)
    args = parser.add_argument_group('Options')
    args.add_argument('-h', '--help', action='help', default=SUPPRESS, help='Show this help message and exit.')
    args.add_argument("-i", "--input",
                      help="Required. Path to video file or image. 'cam' for capturing video stream from camera",
                      type=str, default='D:\工作内容\测试记录\G40\本地记录\YUV+H264视频验证\Movies\\1080\\')
    return parser


def main():
    filelist = os.listdir(args.input)

    for file in filelist:
        # print(file)

        input_stream = args.input + file
        print(input_stream)

        if input_stream.endswith('H264'):
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

            fourcc = cv2.VideoWriter_fourcc('H', '2', '6', '4')
            # fourcc = cv2.VideoWriter_fourcc('I', '4', '2', '0')
            # fourcc = cv2.VideoWriter_fourcc('X', 'V', 'I', 'D')
            # fourcc = cv2.VideoWriter_fourcc('H', 'E', 'V', 'C')
            vw = cv2.VideoWriter(output_path, fourcc, fps, (w, h), True)
            while ret:
                vw.write(frame)
                ret, frame = vc.read()
                cv2.imshow(file, frame)
                endtime = datetime.datetime.now()
                playtime = endtime - starttime
                # print(playtime.total_seconds())
                if cv2.waitKey(28) & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break
                if playtime.total_seconds() >= 15:
                    cv2.destroyAllWindows()
                    break

        else:
            import subprocess as sp

            # Build synthetic video and read binary data into memory (for testing):
            #########################################################################
            # mp4_filename = 'input.mp4'  # the mp4 is used just as reference
            yuv_filename = input_stream
            width, height = 1920, 1080
            # width, height = 1280, 720
            fps = 1  # 1Hz (just for testing)

            # Build synthetic video, for testing (the mp4 is used just as reference):
            # sp.run('ffmpeg -y -f lavfi -i testsrc=size={}x{}:rate=1 -vcodec libx264 -crf 18 -t 10 {}'.format(width, height, mp4_filename))
            # sp.run('ffmpeg -y -f lavfi -i testsrc=size={}x{}:rate=1 -pix_fmt yuv420p -t 10 {}'.format(width, height, yuv_filename))
            #########################################################################

            file_size = os.path.getsize(yuv_filename)
            if yuv_filename.endswith('YUY2'):
                # Number of frames: in YUV420 frame size in bytes is width*height*2
                n_frames = file_size // (width * height * 2)
            else:
                # Number of frames: in YUV420 frame size in bytes is width*height*1.5
                n_frames = file_size // (width * height * 3 // 2)

            # Open 'input.yuv' a binary file.
            f = open(yuv_filename, 'rb')
            starttime = datetime.datetime.now()
            for i in range(n_frames):
                if yuv_filename.endswith('YUY2'):
                    # Read Y, U and V color channels and reshape to height x width x 2 numpy array
                    yuv = np.frombuffer(f.read(width * height * 2), dtype=np.uint8).reshape((height, width, 2))
                else:
                    # Read Y, U and V color channels and reshape to height*1.5 x width numpy array
                    yuv = np.frombuffer(f.read(width * height * 3 // 2), dtype=np.uint8).reshape((height * 3 // 2, width))
                # print(yuv.shape)
                # Convert YUV420 to BGR (for testing), applies BT.601 "Limited Range" conversion.
                if yuv_filename.endswith('I420'):
                    bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_I420)
                if yuv_filename.endswith('YV12'):
                    bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGR_YV12)
                if yuv_filename.endswith('YUY2'):
                    bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGRA_YUY2)
                if yuv_filename.endswith('NV21'):
                    bgr = cv2.cvtColor(yuv, cv2.COLOR_YUV2BGRA_NV21)
                # Convert YUV420 to Grayscale
                # gray = cv2.cvtColor(yuv, cv2.COLOR_YUV2GRAY_I420)

                # Show RGB image and Grayscale image for testing
                cv2.imshow(file, bgr)
                endtime = datetime.datetime.now()
                playtime = endtime - starttime


                key = cv2.waitKey(30)
                if key & 0xFF == ord('q'):
                    cv2.destroyAllWindows()
                    break
                if playtime.total_seconds() >= 15:
                    cv2.destroyAllWindows()
                    break


            f.close()

if __name__ == '__main__':

    args = build_argparser().parse_args()
    sys.exit(main())
