#!/usr/bin/python

import os
import re
import time

dir = "./"
type = "jpg"

files = os.listdir( dir)
rr = re.compile( "\.%s$" %type , re.I )
for f in files:
    if rr.search(f):
        info = os.stat( f )
        print "File : [%s]" %f
        ctime = time.localtime( info.st_ctime )
        print "\tCreation Time : %s" %( str(ctime[0]) + "-" + str(ctime[1]) + "-" + str(ctime[2]) + 
                                        " " + str(ctime[3]) + ":" + str(ctime[4]) + ":" + str(ctime[5]) )
        mtime = time.localtime( info.st_mtime )
        print "\tModify Time : %s" %( str(mtime[0]) + "-" + str(mtime[1]) + "-" + str(mtime[2]) + 
                                        " " + str(mtime[3]) + ":" + str(mtime[4]) + ":" + str(mtime[5]) )
        atime = time.localtime( info.st_atime )
        print "\tAccess Time : %s" %( str(atime[0]) + "-" + str(atime[1]) + "-" + str(atime[2]) + 
                                        " " + str(atime[3]) + ":" + str(atime[4]) + ":" + str(atime[5]) )
        print "\tFile Size : %s bytes\n" %info.st_size
