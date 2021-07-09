# -*- coding: utf-8 -*-
from com.dtmilano.android.viewclient import ViewClient
import time
import os, subprocess, sys
import random
import itertools
import argparse

######利用python3 -m weditor来查看安卓控件id#########################
resolutions2 = ['1920,1080,30', '1920,1080,15']
fovs = ['50', '70', '100', '101']
global Switchdisplayfail
Switchdisplayfail = 0


def log(value):
    print(value)


def adb_shell(cmd):
    p = subprocess.getstatusoutput(cmd)
    return p


def start_test():
    global vc, device, cmd
    """采集指定抖音账号的关注推荐数据
    """
    # pic = 0
    log(u'准备测试SDK')
    # 连设备
    serialno = argv.s
    # serialno = '10.33.48.245'
    if serialno:
        os.system('adb connect {}'.format(serialno or ''))
        time.sleep(3)

    device, serialno = ViewClient.connectToDeviceOrExit(serialno=serialno)
    vc = ViewClient(device, serialno, autodump=False)

    op = adb_shell('adb shell getprop ro.build.version.release')
    if int(op[0]) == 0:
        AndroidId = op[1]
        print(AndroidId)
        if AndroidId == 10:
            log(u'Android 10')
            cmd = "adb shell 'cd /sdcard/Android/data/com.llvision.glass3.api.test/files/Movies && ls -l |wc -l'"
        else:
            log(u'Android 9-')
            cmd = "adb shell 'cd sdcard/DCIM/LLVisionCamera && ls -l |wc -l'"
    else:
        print('获取安卓版本失败，退出！！')
    # 强制关闭SDK
    log(u'强制关闭SDK.')
    device.shell('am force-stop com.llvision.glass3.api.test')
    time.sleep(2)

    # 启动SDK
    log(u'启动SDK.')
    device.shell('am start -n com.llvision.glass3.api.test/com.llvision.glass3.api.test.MainActivity')
    time.sleep(5)
    # 等待连接成功
    log(u'等待连接成功.')

    # 点击搜索按钮
    vc.dump()





def camera_test():
    start_test()
    camera_test_btn = vc.findViewById('com.llvision.glass3.api.test:id/id_base_camera_btn')

    if camera_test_btn:
        log(u'点击camera test，跳转到camera test页面.')
        # print('123')
        camera_test_btn.touch()
        time.sleep(0.2)
        vc.dump()


global pic
pic = -3


def takepicture(ti):
    for takepicturetime in range(0, ti):
        btn_takepicture = vc.findViewById('com.llvision.glass3.api.test:id/btn_takepicture')
        if btn_takepicture:
            log(u'抓帧.')
            btn_takepicture.touch()
            time.sleep(0.3)
            vc.dump()
            global pic
            piclist = []
            result = adb_shell(cmd)
            if int(result[0]) == 0:
                pic1 = int(result[1])
                piclist.append(pic1)
                if argv.OC_camera:
                    shift = 1
                else:
                    shift = 3
                if pic1 >= pic + shift:
                    pic = pic1
                    print(pic)
                else:
                    print(pic)
                    print(piclist)
                    log('camera 打开失败,打开关闭执行' + str((pic1 - piclist[-1]) / shift))
                    sys.exit()

                log(u'抓帧' + str(takepicturetime + 1) + '次')
            else:
                print('命令执行失败，退出！！')
                sys.exit()


def takephoto(ti):
    for takephototime in range(0, ti):
        btn_takephoto = vc.findViewById('com.llvision.glass3.api.test:id/btn_takepicture2')
        if not btn_takephoto:
            device.drag((345, 1550), (345, 1450), duration=100)
            vc.dump()
        btn_takephoto = vc.findViewById('com.llvision.glass3.api.test:id/btn_takepicture2')
        if btn_takephoto:
            log(u'拍照.')
            btn_takephoto.touch()
            time.sleep(0.5)
            vc.dump()
            log(u'拍照' + str(takephototime + 1) + '次')


def Record(ti):
    for Recordtime in range(0, ti):
        btn_record = vc.findViewById('com.llvision.glass3.api.test:id/btn_record')
        if btn_record:
            log(u'开始录像.')
            btn_record.touch()
            time.sleep(30)
            vc.dump()
            btn_record.touch()
            vc.dump()
            log(u'录像' + str(Recordtime + 1) + '次')


def render_Record(ti):
    for Recordtime in range(0, ti):
        render_recod_btn = vc.findViewById('com.llvision.glass3.api.test:id/id_render_recod_btn')
        if not render_recod_btn:
            device.drag((345, 1850), (345, 1250), duration=100)
            vc.dump()
        render_recod_btn = vc.findViewById('com.llvision.glass3.api.test:id/id_render_recod_btn')

        if render_recod_btn:
            log(u'开始叠加录像')
            render_recod_btn.touch()
            time.sleep(30)
            vc.dump()
            render_recod_btn.touch()
            device.drag((345, 1250), (345, 1850), duration=100)
            vc.dump()
            # occameratime =+ 1
            log(u'叠加录像' + str(Recordtime + 1) + '次')


def setFrame(frame):
    frame_btn = vc.findViewById('com.llvision.glass3.api.test:id/spinner_pixel_format')
    if frame_btn:
        log(u'选择frame: ' + str(frame))
        frame_btn.touch()
        time.sleep(0.1)
        vc.dump()

        # 切换分辨率
        user_tab = vc.findViewWithText(frame)
        if not user_tab:
            device.drag((345, 1250), (345, 1550), duration=100)
            vc.dump()
        user_tab = vc.findViewWithText(frame)
        user_tab.touch()
        time.sleep(0.1)
        vc.dump()


def saveFrame(ti):
    saveFrame_btn = vc.findViewById('com.llvision.glass3.api.test:id/btn_save_raw_frame')
    if not saveFrame_btn:
        device.drag((345, 1850), (345, 1250), duration=100)
        vc.dump()
    saveFrame_btn = vc.findViewById('com.llvision.glass3.api.test:id/btn_save_raw_frame')

    if saveFrame_btn:
        log(u'开始保存frame: ' + str(ti))
        saveFrame_btn.touch()
        time.sleep(0.1)
        vc.dump()


def StopFrame(ti):
    StopFrame_btn = vc.findViewById('com.llvision.glass3.api.test:id/btn_stop_raw_frame')
    if not StopFrame_btn:
        device.drag((345, 1250), (345, 1550), duration=100)
        vc.dump()
    StopFrame_btn = vc.findViewById('com.llvision.glass3.api.test:id/btn_stop_raw_frame')

    if StopFrame_btn:
        log(u'stop frame: ' + str(ti))
        StopFrame_btn.touch()
        time.sleep(0.1)
        vc.dump()


def RegisterCallback(ti):
    RegisterCallback_btn = vc.findViewById('com.llvision.glass3.api.test:id/btn_frame_callback')
    if not RegisterCallback_btn:
        device.drag((345, 1550), (345, 1450), duration=100)
        vc.dump()
    RegisterCallback_btn = vc.findViewById('com.llvision.glass3.api.test:id/btn_frame_callback')

    if RegisterCallback_btn:
        if ti == 0:
            log(u'注册callback')
        if ti == 1:
            log(u'注销callback')
        RegisterCallback_btn.touch()
        time.sleep(0.1)
        vc.dump()


def Ocamera(ti):
    # occameratime = 0
    for occameratime in range(ti):
        btn_camera = vc.findViewById('com.llvision.glass3.api.test:id/btn_camera')
        if not btn_camera:
            device.drag((345, 1450), (345, 1550), duration=100)
            vc.dump()
        btn_camera = vc.findViewById('com.llvision.glass3.api.test:id/btn_camera')
        if btn_camera:
            log(u'打开/关闭camera.')
            btn_camera.touch()
            time.sleep(3)
            if (occameratime % 2) == 0:
                time.sleep(5)
                vc.dump()

            else:
                log(u'打开/关闭camera' + str(occameratime / 2 + 0.5) + '次')


def Set_resolution(resolution):
    id_spinner_view = vc.findViewById('com.llvision.glass3.api.test:id/id_spinner_view')
    if id_spinner_view:
        log(u'选择分辨率.' + str(resolution))
        id_spinner_view.touch()
        time.sleep(0.5)
        vc.dump()

        # 切换分辨率
        user_tab = vc.findViewWithText(resolution)
        if not user_tab:
            device.drag((345, 550), (345, 1550), duration=100)
            vc.dump()
        user_tab = vc.findViewWithText(resolution)
        user_tab.touch()
        time.sleep(0.2)
        vc.dump()


def Set_FOV(fov):
    id_spinner_view = vc.findViewById('com.llvision.glass3.api.test:id/spinner_fov')
    if id_spinner_view:
        log(u'选择fov.' + str(fov))
        id_spinner_view.touch()
        time.sleep(0.5)
        vc.dump()

        # 切换分辨率
        user_tab = vc.findViewWithText(fov)
        if not user_tab:
            device.drag((345, 550), (345, 1550), duration=100)
            vc.dump()
        user_tab = vc.findViewWithText(fov)
        user_tab.touch()
        time.sleep(0.2)
        vc.dump()
        Ocamera(2)


def testFrame():
    for resolution in resolutions2:
        Set_resolution(resolution)
        if resolution in ['3840,2160,15']:
            fovs1 = ['101']
        elif resolution in ['1280,720,30', '1920,1080,30']:
            fovs1 = ['100', '70', '50']
        else:
            fovs1 = ['101', '100', '70', '50']
        for fov in fovs1:
            Set_FOV(fov)
            for frame in ['NV21', 'YV12', 'I420', 'YUY2']:
                setFrame(frame)
                RegisterCallback(0)
                saveFrame(resolution)
                setFrame('H264')
                RegisterCallback(0)
                saveFrame(resolution)
                takephoto(1)
                time.sleep(5)

                setFrame(frame)
                StopFrame(resolution)
                RegisterCallback(1)
                setFrame('H264')
                StopFrame(resolution)
                RegisterCallback(1)

                # setFrame('H264')
                RegisterCallback(0)
                saveFrame(resolution)
                setFrame(frame)
                RegisterCallback(0)
                saveFrame(resolution)
                time.sleep(5)
                takephoto(1)
                StopFrame(resolution)
                RegisterCallback(1)
                setFrame('H264')
                StopFrame(resolution)
                RegisterCallback(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument("-s", '--s', help="devices", default='10.33.49.34')
    parser.add_argument("-cam", '--camera', help="camera test or display test", action='store_true')
    argv = parser.parse_args()
    if argv.camera:
        camera_test()
        testFrame()

        # if argv.Switch_resolution:
        #     Switch_resolution()
        # elif argv.Switch_fov:
        #     Switch_fov()
        # elif argv.Switch_fov1:
        #     Switch_fov1()
        # elif argv.OC_camera:
        #     if argv.resolution == 0:
        #         resolution123 = '3840,2160,15'
        #     if argv.resolution == 1:
        #         resolution123 = '1920,1080,30'
        #     OC_camera(resolution123)
    else:
        print('没有测试项')