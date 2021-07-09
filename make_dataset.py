import cv2
import glob
import os
import shutil

videoPaths = glob.glob("D:/下载内容/CFM56-7NG-20200714/正样本/*.mp4")
count = 1
for videoPath in videoPaths:
    if videoPath.endswith('mp4'):
        print("Process video:%s"%videoPath)
        video = cv2.VideoCapture(videoPath)
        total_num = video.get(cv2.CAP_PROP_FRAME_COUNT)
        imgForder = "1/"
        if os.path.exists(imgForder):
            pass
            # shutil.rmtree(imgForder)
        # else:
        #     os.makedirs(imgForder)

        if video.isOpened()==0:
            print("Can not open %s"%videoPath)
            exit(0)
        while True:
            success, frame = video.read()
            interval = 15
            if(count%interval==0):
                imgPath = imgForder +str(count//interval).zfill(5)+".jpg"
                print(count)
                # cv2.imwrite(str(imgPath), frame)
            count +=1
            if success is False:
                break
        # video.release()

