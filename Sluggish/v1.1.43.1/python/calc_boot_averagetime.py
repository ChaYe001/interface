#!/usr/bin/python
# Copyright (c) 2015 Sony Mobile Communications Inc.

import sys
import collections
import math
import optparse
APP_LIST = []
APP_LAUNCH_TIME = []

PACKAGE_NAME = "PackageName"
ELAPSED = "Elapsed"
PERIOD = "Period"

LENGTH_OF_APP_LAUNCH_TIME = 4
SKIP = 0

def read_app_list_file(filename):
    with open(filename) as f:
        for app in f:
            APP_LIST.append(app)

def read_app_launch_time_file(filename):

    with open(filename,"r") as f:
        for line in f:
            data = line.strip().split(",")
            if not len(data) == LENGTH_OF_APP_LAUNCH_TIME:	
                print "read_app_launch_time_file: unexpected data is used"
                sys.exit()
            app_launch_time = {ELAPSED:data[0], PACKAGE_NAME:data[1], PERIOD:data[3]}
            APP_LAUNCH_TIME.append(app_launch_time)

def calc_launch_time(filename):
    global SKIP
    
    with open(filename,"w") as f:
        f.write("packagename," + 
                "average," +
                "median," +
                "standard deviation,"+
                "max," +
                "min" + "\n")

        for app in APP_LIST:
            packagename = app.split("/")[0].strip("\"")
            coldboot = []

            for app_launch_time in APP_LAUNCH_TIME:
                if not float(app_launch_time[ELAPSED]) == 0:
                    if app_launch_time[PACKAGE_NAME] == packagename:
                        if float(app_launch_time[PERIOD]) > 10:
                            print "Unexpected Data"
                        coldboot.append(float(app_launch_time[PERIOD]))

            if SKIP == 1:
                if len(coldboot) > 0:
                    del coldboot[0]

            time_average = list_average(coldboot)
            time_median = -1 if len(coldboot) == 0 else sorted(coldboot)[len(coldboot) // 2]
            time_s_deviation = list_standard_deviation(coldboot)
            time_max = -1 if len(coldboot) == 0 else max(coldboot)
            time_min = -1 if len(coldboot) == 0 else min(coldboot)
            
            f.write(packagename + ",")
            f.write(str(time_average) + ",")
            f.write(str(time_median) + ",")
            f.write(str(time_s_deviation) + ",")            
            f.write(str(time_max) + ",")
            f.write(str(time_min) + ",")            

            
            for data in coldboot:
                f.write(str(data) + ",")
            f.write("\n")

def list_average(listdata):
    if len(listdata) == 0 :
        return -1

    sum = 0
    for data in listdata:
        sum = sum + data

    return  sum / len(listdata)

def list_standard_deviation(listdata):
    if len(listdata) == 0:
        return -1
    
    average = list_average(listdata)
    sum = 0
    for data in listdata:
        sum = sum + (data - average) * (data - average)
    sum = sum / len(listdata)

    return math.sqrt(sum)

def parse_option():
    parser = optparse.OptionParser()
    parser.add_option("-s", "--skip", dest="skip", type="int",
                      default=0, help="show detail")

    options, remainder = parser.parse_args()
    
    global SKIP
    SKIP = options.skip

    return options

if __name__ == "__main__":	
    parse_option()
    
    app_list_file = sys.argv[1]
    app_launch_time_file = sys.argv[2]

    read_app_list_file(app_list_file)
    read_app_launch_time_file(app_launch_time_file)

    names = app_launch_time_file.split(".")
    calc_launch_time(names[0]+"_summary.csv")

