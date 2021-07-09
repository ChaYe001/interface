#!/usr/bin/python
# Copyright (c) 2015 Sony Mobile Communications Inc.

import sys, re, optparse
from collections import Counter

FILENAME = ""

def get_applaunch_period(filename, target_pkgname):
    re_start = re.compile(".*I\/ActivityManager.*START u0.*act\=android\.intent\.action\.MAIN.* cmp\=(\S+)\}.*")
    re_end = re.compile(".*I\/Timeline.*Activity_windows_visible.* u0 (\S+) .*")
    
    data = []
    launchlist = []
    flag = False

    with open(filename, "r") as f:
        for line in f:
            if "START u0" in line:
                ret = re_start.search(line)
                if not ret is None:
                    pkgname, activity_name = ret.group(1).split("/")
                    uptime = line.split()[0]

                    if pkgname in target_pkgname:
                        if flag:
                            print "previous launch didn't finish"
                        
                        flag = True
                        data = []
                        data.append(float(uptime))
                continue

            if "Activity_windows_visible" in line:
                ret = re_end.search(line)
                if not ret is None:
                    pkgname, activity_name = ret.group(1).split("/")
                    uptime = line.split()[0]
                    
                    if pkgname in target_pkgname and flag:
                        flag = False
                        data.append(float(uptime))
                        launchlist.append(data)
    
    return launchlist

def get_killed_list(filename):
    re_lmk = re.compile(".*\[(.*)] lowmemorykiller.*\'(.*)\'.*")
    lmklist = []
    with open(filename, "r") as f:
        for line in f:
            if not "lowmemorykiller" in line:
                continue
            
            ret = re_lmk.search(line)

            if not ret is None:
                uptime = ret.group(1)
                pkgname = ret.group(2)
                lmklist.append([float(uptime), pkgname])

    return lmklist

def get_killed_list_during_launch(filename, lmklist, apkname):
    launchlist = get_applaunch_period(filename, apkname)
    killed_process_list = []
    lmk_details_list = []

    for launch in launchlist:
        start = launch[0]
        end = launch[1]
        count_total = 0
        count_direct = 0
        for lmk in lmklist:
            if start < lmk[0] and lmk[0] < end:
                killed_process_list.append(lmk[1])
                count_total += 1
                if not lmk[2] == "kswapd0":
                    count_direct += 1
                    
#        print str(count_total)+","+str(count_direct)
        lmk_details_list.append([launch[0], launch[1], launch[1]-launch[0], count_total, count_direct])

    pkgname = apkname.split("/")[0]

    filename = FILENAME.replace('.csv', '_[' + pkgname + '].csv')
    print filename
    with open(filename, "w") as f:
        f.writelines("start, end, duration, total lmk, direct lmk\n")
        for data in lmk_details_list:
            f.writelines(str(data[0]) + "," + str(data[1]) + "," + str(data[2]) + "," + str(data[3]) + "," + str(data[4]) + "\n")

    return killed_process_list

def get_killer_list(filename):
    re_killer = re.compile(".*\[(.*)].*on behalf of \'(.*)\'.*")
    killerlist = []
    with open(filename, "r") as f:
        for line in f:
            if not "on behalf of" in line:
                continue
            
            ret = re_killer.search(line)

            if not ret is None:
                uptime = ret.group(1)
                killer = ret.group(2)
                killerlist.append([float(uptime), killer])

    return killerlist

def get_app_list(filename):
    output = []
    with open(filename, "r") as f:
        for line in f:
            if not "#" in line:
                output.append(line.strip().replace(",","").replace("\"",""))
    return output

def make_summary_all(lmklist):
    line = "Total killed process ranking\n"
    total_killed_process_list = []
    for lmk in lmklist:
        total_killed_process_list.append(lmk[1])

    counter = Counter(total_killed_process_list)
    for data in counter.most_common(10):
        line += data[0] + "," + str(data[1]) + "\n"

    line += "\nTotal killer process ranking\n"
    total_killer_process_list = []
    for lmk in lmklist:
        total_killer_process_list.append(lmk[2])

    counter = Counter(total_killer_process_list)
    for data in counter.most_common(10):
        line += data[0] + "," + str(data[1]) + "\n"

    return line

def remove_broken_log(list1, list2):
    count = 0

    while True:
        if len(list1) <= count or len(list2) <= count:
            break

        if list1[count][0] - list2[count][0] > 0.002:
            print list2[count], "is removed"
            del list2[count]
        elif list2[count][0] - list1[count][0] > 0.002:
            print list1[count], "is removed"
            del list1[count]
        else:
            count += 1

    if len(list1) < len(list2):
        for i in range(len(list2) - len(list1)):
            del list2[len(list1)]
    elif len(list1) > len(list2):
        for i in range(len(list1) - len(list2)):
            del list1[len(list2)]

def parse_option():
    parser = optparse.OptionParser()
    parser.add_option("-f", "--filename", dest="filename", type="str",
        default="default.csv", help="show detail")

    options, remainder = parser.parse_args()
    global FILENAME

    if options.filename != "":
        FILENAME = options.filename

if __name__ == "__main__":
    parse_option()

    if len(sys.argv) < 4:
        print "invalid argument"
        sys.exit(1)
    
    filename_logcat = sys.argv[1]    
    filename_dmesg = sys.argv[2]
    filename_applist = sys.argv[3]

    apkname = "com.sonyericsson.android.camera/.CameraActivity"

    lmklist = get_killed_list(filename_dmesg)
    killerlist = get_killer_list(filename_dmesg)

    if not len(lmklist) == len(killerlist):
        print "the size of list is", len(lmklist), "and", len(killerlist)
        remove_broken_log(lmklist, killerlist)
        if not len(lmklist) == len(killerlist):
            print "length of the list is not the same"
            sys.exit()
        print "list is recovered"

    for i in range(len(lmklist)):
        lmklist[i].append(killerlist[i][1])

    summary = make_summary_all(lmklist)

    app_list = get_app_list(filename_applist)

    killed_process_count_all = {}
    for apkname in app_list:
        killed_process_list = get_killed_list_during_launch(filename_logcat, lmklist, apkname)
        counter = Counter(killed_process_list)

        killed_process_count_all[apkname] = len(killed_process_list)

    counter = Counter(killed_process_count_all)

    summary += "\nTotal LMK occurance ranking\n"
    for data in counter.most_common(10):
        summary += data[0].split("/")[0] + "," + str(data[1]) + "\n"

    with open(FILENAME, "w") as f:
#        print summary
        f.writelines(summary)



