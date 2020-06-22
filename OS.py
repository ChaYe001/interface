#__author__ = 'Bo.Gu' 
# -*- coding: utf-8 -*-   

import os
import time
import datetime
  
 
          
    
def TimeStampToTime(timestamp):
    timeStruct = time.localtime(timestamp)
    return time.strftime('%Y-%m-%d %H:%M:%S',timeStruct)

def get_FileAccessTime(filePath):
    filePath = unicode(filePath,'utf8')
    t1 = os.path.getatime(filePath)
    return TimeStampToTime(t1)
    print TimeStampToTime(t1)
#def get_FileCreateTime(filePath):
#　　　　　　filePath = unicode(filePath,'utf8')
#　　　　　　t2 = os.path.getctime(filePath)
#　　　　　　return TimeStampToTime(t)

#def get_FileModifyTime(filePath):
#　　　　　　filePath = unicode(filePath,'utf8')
#　　　　　　t3 = os.path.getmtime(filePath)
#　　　　　　return TimeStampToTime(t)
if __name__ == '__main__':
#    L = file_name("./")
#    for each in L:
#        print (each)
    get_FileAccessTime('/home/gubo/Python/os')
