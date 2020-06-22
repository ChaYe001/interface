#__author__ = 'Bo.Gu' 
# -*- coding: utf-8 -*-   
#!/usr/bin/python3
import os
import time
import re
import datetime
file_dir = './' 
type = "jpg"
rr = re.compile( "\.%s$" %type , re.I )

def file_name(file_dir):   
    L=[]   
    for root, dirs, files in os.walk(file_dir):  
        for file in files:  
            if os.path.splitext(file)[1] == '.jpg':  
                L.append(os.path.join(root, file))  

    return L     
def Creation_Time():
        ctime = time.localtime( info.st_ctime )         
        Creation_Time = ( str(ctime[0]) + "-" + str(ctime[1]) + "-" + str(ctime[2]) + 
                           " " + str(ctime[3]) + ":" + str(ctime[4]) + ":" + str(ctime[5]) )
        print "\tCreation Time : %s" %Creation_Time
def Modify_Time():
        mtime = time.localtime( info.st_mtime )
        Modify_Time = ( str(mtime[0]) + "-" + str(mtime[1]) + "-" + str(mtime[2]) + 
                                        " " + str(mtime[3]) + ":" + str(mtime[4]) + ":" + str(mtime[5]) )
        print "\tModify Time : %s" %Modify_Time
def Access_Time():
        atime = time.localtime( info.st_atime )
        Access_Time = ( str(atime[0]) + "-" + str(atime[1]) + "-" + str(atime[2]) + 
                                        " " + str(atime[3]) + ":" + str(atime[4]) + ":" + str(atime[5]) )
        print "\tAccess Time : %s" %Access_Time
def file_time(file_dir):
	global info
        T = file_name("./")
	for root, dirs, files in os.walk(file_dir):  
            for f in T:
		if rr.search(f):
		    info = os.stat( f )
                    print "File : [%s]" %f
       		    Modify_Time()
                    Creation_Time()
                    Access_Time()

if __name__ == '__main__':
#    L = file_name("./")
#    for each in L:
#        print (each)
    file_time("./")
#    print Creation_Time
    
        
