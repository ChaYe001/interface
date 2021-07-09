#!/usr/bin/python
# Copyright (c) 2015 Sony Mobile Communications Inc.

import sys
import collections
from collections import Counter
from math import sqrt

APP_LIST = []
APP_LAUNCH_TIME = []
PROCESS_STATUS = []

UNKNOWN_APP_LIST = []
DUPLICATED_APP_LIST = []
FAILED_APP_LIST = []

PACKAGE_NAME = "PackageName"
ELAPSED = "Elapsed"
PERIOD = "Period"
BOOTMODE_P = "BootMode_P"
FAILED = "FAILED"
INI_MIN_DIFF = 100000000000

LENGTH_OF_APP_LAUNCH_TIME = 4
LENGTH_OF_PROCESS_STATUS = 3

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

def read_process_status_file(filename):

    with open(filename,"r") as f:
        i = 0
        for line in f:
            data = line.strip().split(",")
            if not len(data) == LENGTH_OF_PROCESS_STATUS:	
                print "read_process_status_file: unexpected data is used"
                sys.exit()
            process_status = {PACKAGE_NAME:data[0], BOOTMODE_P:data[1], ELAPSED:data[2]}
            PROCESS_STATUS.append(process_status)
            i=i+1

def write_process_status_file(filename):
    with open(filename,"w") as f:
        f.write("pkgname, bootmode_p, ,elapsed, period\n")
        for process_status in PROCESS_STATUS:
            package_name = process_status[PACKAGE_NAME]
            bootmode_p = process_status[BOOTMODE_P]
            elapsed = process_status[ELAPSED]
            period = process_status[PERIOD]
            f.write(package_name + "," + bootmode_p + ",," + elapsed + "," + period + "\n")

def print_summary():
    print "Summary:"
    print "Total Observed Launch:\t" + str(len(APP_LAUNCH_TIME))
    print "\t" + str(len(PROCESS_STATUS) - len(FAILED_APP_LIST)) + "\t" + "Succeed" + " (Attepted Launch: " +  str(len(PROCESS_STATUS)) + ")"
    print "\t" + str(len(DUPLICATED_APP_LIST)) + "\t" + "Duplicated Launch"
    print "\t" + str(len(UNKNOWN_APP_LIST)) + "\t" + "Unknown Apps"

    print "Unknown Application List: "
    count_dict = collections.Counter(UNKNOWN_APP_LIST)
    for k,v in count_dict.items():
        print "\t", v, "\t", k

    print "Failed Application List: "
    count_dict = collections.Counter(FAILED_APP_LIST)
    for k,v in count_dict.items():
        print "\t", v, "\t", k

def add_period_to_process_status():
    for app_launch_time in APP_LAUNCH_TIME:
        min_diff = INI_MIN_DIFF
        i = 0
        id = -1
        for process_status in PROCESS_STATUS:
            if app_launch_time[PACKAGE_NAME] in process_status[PACKAGE_NAME]:
                if 0 <= float(process_status[ELAPSED]):
                    diff = abs(float(app_launch_time[ELAPSED]) - float(process_status[ELAPSED]))
                    if diff < min_diff:
                        min_diff = diff
                        id = i
            i=i+1
        if id >= 0:
            process_status = PROCESS_STATUS[id]
            if len(process_status) != LENGTH_OF_PROCESS_STATUS:
                DUPLICATED_APP_LIST.append(app_launch_time[PACKAGE_NAME])
                print "Duplicated:\t", app_launch_time[ELAPSED], "\t\t", app_launch_time[PACKAGE_NAME]
            else:
                process_status[PERIOD] = app_launch_time[PERIOD]
                PROCESS_STATUS[id] = process_status
                if min_diff > 5:
                    print "LargeDiff:\t", app_launch_time[ELAPSED], "\t", str(min_diff), "\t",  app_launch_time[PACKAGE_NAME]
        else:
            UNKNOWN_APP_LIST.append(app_launch_time[PACKAGE_NAME])

    i = 0
    for process_status in PROCESS_STATUS:
        if not PERIOD in process_status:
            process_status[PERIOD] = FAILED
            PROCESS_STATUS[i] = process_status
        i=i+1


def calc_launch_time(filename):
    average_coldboot = {}

    with open(filename,"w") as f:
        f.write("packagename" + "," +
                "average first boot" + "," +
                "average cold boot" + "," +
                "," +
                "average warm boot" + "," +
                "maximum first boot" + "," +
                "maximum cold boot" + "," +
                "," +
                "maximum warm boot" + "," +
                "minimum first boot" + "," +
                "minimum cold boot" + "," +
                "," +
                "minimum warm boot" + "," +
                "standard deviation first boot" + "," +
                "standard deviation cold boot" + "," +
                "," +
                "standard deviation warm boot" + "," +
                "normalization standard deviation first boot" + "," +
                "normalization standard deviation cold boot" + "," +
                "," +
                "normalization standard deviation warm boot" + "\n")

        for app in APP_LIST:
            packagename = app.split("/")[0].strip("\"")
            flag_fast = True
            fastboot = []
            warmboot = []
            coldboot = []

            for status in PROCESS_STATUS:
                if status[PACKAGE_NAME].split("/")[0].strip("\"") == packagename:
                    if status[PERIOD] == FAILED:
                        continue

                    if flag_fast:
                        fastboot.append(status[PERIOD])
                        flag_fast = False
                    elif status[BOOTMODE_P] == "False":
                        coldboot.append(status[PERIOD])
                    else:
                        warmboot.append(status[PERIOD])

            average_coldboot[app.strip().replace(",","").replace("\"","")] = list_average(coldboot)

            f.write(packagename + "," +
                    str(list_average(fastboot)) + "," +
                    str(list_average(coldboot)) + "," +
                    "," +
                    str(list_average(warmboot)) + "," +
                    str(list_maximum(fastboot)) + "," +
                    str(list_maximum(coldboot)) + "," +
                    "," +
                    str(list_maximum(warmboot)) + "," +
                    str(list_minimum(fastboot)) + "," +
                    str(list_minimum(coldboot)) + "," +
                    "," +
                    str(list_minimum(warmboot)) + "," +
                    str(list_standard_deviation(fastboot)) + "," +
                    str(list_standard_deviation(coldboot)) + "," +
                    "," +
                    str(list_standard_deviation(warmboot)) + "," +
                    str(list_normalization_standard_deviation(fastboot)) + "," +
                    str(list_normalization_standard_deviation(coldboot)) + "," +
                    "," +
                    str(list_normalization_standard_deviation(warmboot)) + "\n")

    return average_coldboot

def calc_launch_average_boot_times(filename):
    average_boot = {}

    with open(filename,"w") as f:
        f.write("packagename" + "," +
                "average boot time" + "," +
                "boot count" + "," +
                "cold count" + "," +
                "warm count" + "\n")

        for app in APP_LIST:
            packagename = app.split("/")[0].strip("\"")
            boottimes = []
            flag_fast = True
            boot_count = 0
            cold_count = 0
            warm_count = 0

            for status in PROCESS_STATUS:
                if status[PACKAGE_NAME].split("/")[0].strip("\"") == packagename:
                    if status[PERIOD] == FAILED:
                        continue

                    if flag_fast:
                        flag_fast = False
                        continue
                    elif status[BOOTMODE_P] == "False":
                        cold_count += 1
                    else:
                        warm_count += 1

                    boot_count += 1
                    boottimes.append(status[PERIOD])

            average_boot[app.strip().replace(",","").replace("\"","")] = list_average(boottimes)

            f.write(packagename + "," +
                    str(list_average(boottimes)) + ","+
                    str(boot_count) + "," +
                    str(cold_count) + "," +
                    str(warm_count) + "\n")

    return average_boot

def make_failed_applist():
    for status in PROCESS_STATUS:
        if status[PERIOD] == FAILED:

            FAILED_APP_LIST.append(status[PACKAGE_NAME])

def list_average(listdata):
    if len(listdata) == 0 :
        return -1

    sum = 0
    for data in listdata:
        sum = sum + float(data)

    return  sum / len(listdata)

def list_maximum(listdata):
    if len(listdata) == 0 :
        return -1

    max_val = float(listdata[0])
    for data in listdata:
        if max_val < float(data):
            max_val = float(data)

    return max_val

def list_minimum(listdata):
    if len(listdata) == 0 :
        return -1

    min_val = float(listdata[0])
    for data in listdata:
        if min_val > float(data):
            min_val = float(data)

    return min_val

def list_standard_deviation(listdata):
    ave = list_average(listdata)
    if ave == -1 :
        return -1

    sum = 0
    for data in listdata:
        sum = sum + ((ave - float(data)) ** 2)

    return  sqrt(sum / len(listdata))

def list_normalization_standard_deviation(listdata):
    if len(listdata) == 0 :
        return -1

    min_val = float(list_minimum(listdata))
    max_val = float(list_maximum(listdata))

    normalization_listdata = []
    for data in listdata:
        if min_val < max_val:
            x_val = (float(data) - min_val) / (max_val - min_val)
        else:
            x_val = 0
        normalization_listdata.append(x_val)

    return list_standard_deviation(normalization_listdata)

if __name__ == "__main__":

    if not len(sys.argv) == 4:
        print "Usage"
        print "python make_boottime_files [Applist_40.params] [COLDBOOT_process_status.csv] [COLDBOOT_uptime_applaunchtime.csv]"
        sys.exit()

    app_list_file = sys.argv[1]
    process_status_file = sys.argv[2]
    app_launch_time_file = sys.argv[3]

    read_app_list_file(app_list_file)
    read_process_status_file(process_status_file)
    read_app_launch_time_file(app_launch_time_file)

    add_period_to_process_status()
    make_failed_applist()

    names = process_status_file.split(".")
    write_process_status_file(names[0]+"_updated."+names[1])
    print_summary()

    names = app_launch_time_file.split(".")
    launch_time_list = calc_launch_average_boot_times(names[0]+"_average_boot_times.csv")

    names = app_launch_time_file.split(".")
    launch_time_list = calc_launch_time(names[0]+"_summary.csv")
    counter = Counter(launch_time_list)

    with open(names[0]+"_sluggish_ranking.csv","w") as f:
        for data in counter.most_common():
            f.write(data[0] + "," + str(data[1]) + "\n")


