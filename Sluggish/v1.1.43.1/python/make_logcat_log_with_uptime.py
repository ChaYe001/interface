#!/usr/bin/python
# Copyright (c) 2015 Sony Mobile Communications Inc.

import sys
import re
import optparse

FILENAME = ""

def date2sec(date):
    h = float(date.split(":")[0])
    m = float(date.split(":")[1])
    s = float(date.split(":")[2])
    return h * 3600 + m * 60 + s

def get_offset(filename_logcat):
    offset = None
    uptime = None
    e_uptime = None
    e_logcatdate = None
    re_uptime = re.compile("Activity_idle id: android.os.Binder\S+ time\:(\d+)")

    with open(filename_logcat, "r") as f:
        for line in f:
            if "Activity_idle id: android.os" in line:
                ret = re_uptime.search(line)
                if not ret is None:
                    uptime = float(ret.group(1)) / 1000
                    logcatdate = line.split()[1]
                    break

            if "Logcat start uptime" in line:
                e_uptime = float(line.split()[5])
                e_logcatdate = line.split()[1]

    if not uptime:
        uptime = e_uptime
        logcatdate = e_logcatdate

    if uptime:
        logcatsec = date2sec(logcatdate)
        offset = logcatsec - uptime
        print "logcat date: " + logcatdate
        print "logcat time: " + str(logcatsec)
        print "uptime: " + str(uptime)
        print "offset: " + str(offset)

    return offset

def parse_option():
    parser = optparse.OptionParser()
    parser.add_option("-f", "--filename", dest="filename", type="str",
        default="default.txt", help="show detail")

    options, remainder = parser.parse_args()

    global FILENAME
    FILENAME = options.filename

    return options

if __name__ == "__main__":
    parse_option()

    filename_logcat = sys.argv[1]
    offset = get_offset(filename_logcat)

    if offset is None:
        print "uptime baseline not found"
        sys.exit()


    filename_uptime_logcat = FILENAME
    fout = open(filename_uptime_logcat, "w")

    with open(filename_logcat, "r") as fin:
        for line in fin:
            logcatdate = line.split()[1]

            if len(logcatdate) == 12:
                uptime = date2sec(logcatdate) - offset

                if uptime > 3600.0 * 24:
                    uptime -= 3600.0 * 24

                if uptime < 0.0:
                    uptime += 3600.0 * 24

                fout.write('%.3f' % uptime + "\t" + line)

    fout.close()
