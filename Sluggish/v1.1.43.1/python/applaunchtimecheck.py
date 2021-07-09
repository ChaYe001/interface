#!/usr/bin/python
# Copyright (c) 2015 Sony Mobile Communications Inc.

import os, sys, re, commands, string, optparse, subprocess, fcntl
import datetime, time, sched, threading, math, csv, codecs

MODE = None
FILENAME_LOG = None
FILENAME_ISSUE_INTENT = None

def do_precheck(log, precheck_list):
    flag = False
    for precheck in precheck_list:
        if precheck in log:
            flag = True
            break
    return flag

def analyze(log_list, re_start, re_end):
    activity_stack = {}
    re_start = re.compile(re_start)
    re_end = re.compile(re_end)

    for uptime, log in log_list:
        pkgname, timeline, activity_name, tag = "", "", "", ""

        ret = re_start.search(log)
        if not ret is None:
            pkgname, activity_name = ret.group(1).split("/")
            timeline = uptime
            tag = "START"

        ret = re_end.search(log)
        if not ret is None:
            pkgname, activity_name = ret.group(1).split("/")
            timeline = uptime
            tag = "END"

        if not pkgname:
            continue

        stack = activity_stack.get(pkgname, [])
        stack.append((timeline, tag, activity_name))
        activity_stack[pkgname] = stack

    line = ""
    for k, v in activity_stack.items():
        starttime, duration = 0, 0
        for timeline, tag, activity_name in v:
            if "START" == tag:
                starttime = timeline
            elif "END" == tag and starttime != 0:
                duration = timeline - starttime

            if duration != 0:
                line += "%s,%s,%s,%s\n"%(starttime, k, activity_name, duration)
                starttime, duration = 0, 0

    filename_split = FILENAME_LOG.split('_')
    filename = filename_split[0] + "_" + filename_split[1] + "_applaunchtime.csv"
    f = open(filename, "w")
    f.writelines(line)
    f.close()


def parse_option():
    parser = optparse.OptionParser()
    parser.add_option("-m", "--mode", dest="mode", type="str",
        default=None, help="judgement mode accodring to the device log type")
    parser.add_option("-f", "--filename", dest="filename", type="str",
        default=None, help="log file name")
    parser.add_option("-s", "--filename2", dest="filename2", type="str",
        default=None, help="log file name")

    options, remainder = parser.parse_args()

    global MODE
    global FILENAME_LOG
    global FILENAME_ISSUE_INTENT

    MODE = options.mode
    FILENAME_LOG = options.filename
    FILENAME_ISSUE_INTENT = options.filename2

def check_option():
    if FILENAME_LOG is None:
        print "Usage"
        print "python applaunchtimecheck.py -f [COLDBOOT_uptime_logcat.txt]"
        print "-f should be used to identify the adb log file"
        sys.exit()

    if MODE == "s6" and FILENAME_ISSUE_INTENT is None:
        print "-s should be used in case of S6"
        sys.exit()

def main():
    parse_option()
    check_option()

    precheck_list = ["START u0", "Activity_windows_visible", "Displayed", "ISSUE_INTENT",
        "ACT-windowsVisible"]
    log_list = []

    try:
        with open(FILENAME_LOG, "r") as f:
            for line in f:
                if do_precheck(line, precheck_list):
                    log_list.append([float(line.split("\t")[0]), line.split("\t")[1]])
    except IOError, (errno, msg):
        print >> sys.stderr, 'except: Cannot open "%s"' % FILENAME_LOG
        print >> sys.stderr, '  errno: [%d] msg: [%s]' % (errno, msg)
        sys.exit()

    if MODE == "odm-mtk":
        # "ACT-windowsVisible" print, available on eng variant
        # on kabini platform
        re_start = ".*I\/ActivityManager.*START u0.* cmp\=(\S+)\}.*"
        re_end = ".*ActivityManager.*ACT-windowsVisible.* u0 (.*) .*\}.*"
    elif MODE is None:
        re_start = ".*I\/ActivityManager.*START u0.* cmp\=(\S+)\}.*"
        re_end = ".*I\/Timeline.*Activity_windows_visible.* u0 (\S+) .*"
    elif MODE == "m9":
        re_start = ".*I\/ActivityManager.*START u0.*act\=android\.intent\.action\.MAIN.* cmp\=(\S+)\}.*"
        re_end = ".*I\/ActivityManager.*Displayed (\S+)\:.*"
    elif MODE == "s6":
        with open(FILENAME_ISSUE_INTENT, "r") as f:
            for line in f:
                log_list.append([float(line.split(",")[1]), "ISSUE_INTENT " +  line.split(",")[0]])
        from operator import itemgetter
        log_list.sort(key=itemgetter(0,1))
        re_start = "ISSUE_INTENT (\S+).*"
        re_end = ".*I\/Timeline.*Activity_windows_visible.* u0 (\S+) .*"
    elif MODE == "mtp":
        re_start = ".*I\/ActivityManager.*START u0.*act\=android\.intent\.action\.MAIN.* cmp\=(\S+)\}.*"
        re_end = ".*I\/ActivityManager.*Displayed (\S+)\:.*"

    analyze(log_list, re_start, re_end)

if __name__ == "__main__":
    main()
