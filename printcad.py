#!/usr/bin/env python
# -*- coding: utf-8 -*-

import math
import win32com.client
import pythoncom

# 接口是照抄另外一个大神的
acad = win32com.client.Dispatch("AutoCAD.Application.23")
# AutoCAD.Application.19为 ProgID
acaddoc = acad.ActiveDocument
acaddoc.Utility.Prompt("Hello AutoCAD\n")
acadmod = acaddoc.ModelSpace


def APoint(x, y):
    """坐标点转化为浮点数"""
    # 需要两个点的坐标
    return win32com.client.VARIANT(pythoncom.VT_ARRAY | pythoncom.VT_R8, (x, y))


def Print(kind, Scale, x, y, path, Fname):
	# 两种格式的图纸用到两种打印机
    if 'PDF' in kind:
        name = 'DWG To PDF.pc3'
    elif 'DWF' in kind:
        name = 'DWF6 ePlot.pc3'

    layout = acaddoc.layouts.item('Model') # 先来个layout对象
    plot = acaddoc.Plot # 再来个plot对象

    acaddoc.SetVariable('BACKGROUNDPLOT', 0) # 前台打印
    layout.StyleSheet = 'monochrome.ctb' # 选择打印样式
    layout.PlotWithLineweights = False # 不打印线宽
    a = layout.GetCanonicalMediaNames() # 这句忽略
    layout.ConfigName = name # 选择打印机
    layout.CanonicalMediaName = 'ISO_full_bleed_A2_(594.00_x_420.00_MM)' # 图纸大小这里选择A2
    layout.PaperUnits = 1 # 图纸单位，1为毫米
    layout.PlotRotation = 0 # 横向打印
    layout.StandardScale = 0 # 图纸打印比例
    layout.CenterPlot = True # 居中打印
    layout.PlotWithPlotStyles = True # 依照样式打印
    layout.PlotHidden = False # 隐藏图纸空间对象

    po1 = APoint(x * Scale - 1, y * Scale)
    po2 = APoint(x * Scale - 1 + 11880, y * Scale + 8400) # 左下点和右上点
    layout.SetWindowToPlot(po1, po2)
    layout.PlotType = 3.5 # 按照窗口打印，别问我为什么是3.5我试出来的。
    plot.PlotToFile(path + '\ ' + Fname)
