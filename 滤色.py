# -*- coding: utf-8 -*-
# @Time    : 2021-04-28 20:45
# @Author  : AlanWang4523
# @FileName: py_select_shadows_highlight.py

import os
import sys
import cv2
import numpy as np

def img_filter(img):                   #计算图像梯度（高反差像素）
    x=cv2.Sobel(img,cv2.CV_16S,1,0)
    y=cv2.Sobel(img,cv2.CV_16S,0,1)

    absx=cv2.convertScaleAbs(x)
    absy=cv2.convertScaleAbs(y)
    dist=cv2.addWeighted(absx,0.5,absy,0.5,0)
    return dist

def addImage(img1, img2,alpha):
    h, w, _ = img1.shape
    """
        函数要求两张图必须是同一个size
        alpha，beta，gamma可调
    """
    img2 = cv2.resize(img2, (w, h), interpolation=cv2.INTER_AREA)

    beta = 1 - alpha
    gamma = 0
    img_add = cv2.addWeighted(img1, alpha, img2, beta, gamma)
    return img_add

def hanlde_img(path):
    # 根据路径读取图片
    img = cv2.imread(path)

    img = img.astype(np.float) / 255.0

    # 分离 RGB 三个通道，注意：openCV 中图像格式是 BGR
    srcR = img[:, :, 2]
    srcG = img[:, :, 1]
    srcB = img[:, :, 0]

    # 将原图转成灰度图
    grayImg = 0.299 * srcR + 0.587 * srcG + 0.114 * srcB

    # 高光选区
    # maskThreshold = 0.64
    # luminance = grayImg * grayImg
    # luminance = np.where(luminance > maskThreshold, luminance, 0)

    # 阴影选区
    maskThreshold = 0.33
    luminance = (1 - grayImg) * (1 - grayImg)
    luminance = np.where(luminance > maskThreshold, luminance, 0)

    mask = luminance > maskThreshold

    # 显示正交叠底图
    img[:, :, 0] = luminance
    img[:, :, 1] = luminance
    img[:, :, 2] = luminance

    # 显示选区内原图
    # img[:, :, 0][~mask] = 0
    # img[:, :, 1][~mask] = 0
    # img[:, :, 2][~mask] = 0

    img = img * 255
    img = img.astype(np.uint8)

    # 创建图片显示窗口

    i = 0
    while True:
        # 循环显示图片，按 ‘q’ 键退出
        title = "ShadowHighlight" + str(i)
        cv2.namedWindow(title, 0)
        cv2.resizeWindow(title, 640, 360)
        cv2.moveWindow(title, 640*(i%3), 360*int(i/3))
        cv2.imshow(title, img)
        i += 1
        if i==9:
            i = i%9
        if cv2.waitKey(0) == ord('q'):
            break
    cv2.destroyAllWindows()



if __name__ == '__main__':
    '''
        运行环境：Python 3
        执行：python3 py_pic_handle.py <图片路径>
        如：python3 py_pic_handle.py test.jpg
    '''
    # if len(sys.argv) == 1:
    #     print("参数错误：未传入图片路径！")
    #     sys.exit(-1)
    # img_path = sys.argv[1]
    img_path = '2.jpg'
    # print("img_path Params:", img_path)
    # hanlde_img(img_path)


    img1 = cv2.imread(img_path)  # 以彩色图的形式读入
    dist_img = img_filter(img1)  # 执行高通过滤
    for i in range(1, 10):  # 循环执行（不同的alpha）：显示叠加图，写入处理后的图像
        i = i-1

        title = "ShadowHighlight" + str(i)
        cv2.namedWindow(title, 0)
        cv2.resizeWindow(title, 640, 360)
        cv2.moveWindow(title, 640 * (i % 3), 360 * int(i / 3))
        IMG_Add = addImage(img1, img1, i * 0.1)  # alpha，beta，gamma可调
        if i == 0:
            IMG_Add = img1
        cv2.imshow(title, IMG_Add)
        if cv2.waitKey(0) == ord('q'):
            break
        # cv2.imwrite('img_add_' + str(i) + ".png", IMG_Add)
    cv2.destroyAllWindows()

