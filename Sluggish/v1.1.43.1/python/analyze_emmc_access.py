#!/usr/bin/python
# Copyright (c) 2015 Sony Mobile Communications Inc.

import sys, re
import commands
import optparse
from collections import Counter

APP_LIST = None
TOP_N = 15
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
                            print "previous launch of " + pkgname + " didn't finish"
                        
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

def get_emmc_pagefault_record(filename):
    re_str_retry = re.compile(".*\[(.*)] .*SOMC page_fault_retried\[.*]\:.+\:(\S+)us")
    re_str_major = re.compile(".*\[(.*)] .*SOMC page_fault_major\[.*]\:(\S+)us")
    re_str_minor_sum = re.compile(".*\[(.*)] .*SOMC page_fault_minor_sum\:(.+)\:(\S+)us")
    re_str_minor = re.compile(".*\[(.*)] .*SOMC page_fault_minor\[.*]\:(\S+)us")

    page_fault_list = []

    with open(filename, "r") as f:
        for line in f:
            if "SOMC page_fault_retried" in line:
                ret = re_str_retry.search(line)

                if not ret is None:
                    dict = {}
                    dict["type"] = "RETRY"
                    dict["uptime"] = float(ret.group(1))
                    dict["count"] = 1
                    dict["period"] = ret.group(2)
                    page_fault_list.append(dict)
                continue

            if "SOMC page_fault_major" in line:
                ret = re_str_major.search(line)

                if not ret is None:
                    dict = {}
                    dict["type"] = "MAJOR"
                    dict["uptime"] = float(ret.group(1))
                    dict["count"] = 1
                    dict["period"] = ret.group(2)

                    page_fault_list.append(dict)
                continue

            if "SOMC page_fault_minor_sum" in line:
                ret = re_str_minor_sum.search(line)

                if not ret is None:
                    dict = {}
                    dict["type"] = "MINOR"
                    dict["uptime"] = float(ret.group(1))
                    dict["count"] = ret.group(2)
                    dict["period"] = ret.group(3)
                    page_fault_list.append(dict)
                continue

            if "SOMC page_fault_minor" in line:
                ret = re_str_minor.search(line)

                if not ret is None:
                    dict = {}
                    dict["type"] = "MINOR"
                    dict["uptime"] = float(ret.group(1))
                    dict["count"] = 1
                    dict["period"] = ret.group(2)
                    page_fault_list.append(dict)
                continue

    return page_fault_list

def get_pagefault_list(launch_list, all_pagefault_record_list):
    index = 0
    pagefault_period_list_retry = [0 for row in range(len(launch_list))]
    pagefault_period_list_major = [0 for row in range(len(launch_list))]
    pagefault_period_list_minor = [0 for row in range(len(launch_list))]

    for pagefault_record in all_pagefault_record_list:
        type = pagefault_record["type"]
        uptime = pagefault_record["uptime"]
        count = pagefault_record["count"]
        period = pagefault_record["period"]

        for launch in launch_list[index:]:
            start = launch[0]
            end = launch[1]
            if uptime < start:
                break
            if end < uptime:
                index += 1
                continue

            if type is "RETRY":
                pagefault_period_list_retry[index] += int(period)
            elif type is "MAJOR":
                pagefault_period_list_major[index] += int(period)
            elif type is "MINOR":
                pagefault_period_list_minor[index] += int(period)
            else:
                print "unexpected result"
                sys.exit()

    return pagefault_period_list_retry, pagefault_period_list_major, pagefault_period_list_minor

def get_emmc_access_record(filename):
    re_str = re.compile(".*\[(.*)] .*SOMC.*readpages\[(.*)]\:size (\S+):(\S+)us:(\S+)")
    access_record_list = []

    with open(filename, "r") as f:
        for line in f:
            if not "readpages" in line:
                continue

            ret = re_str.search(line)

            if not ret is None:
                dict = {}
                dict["uptime"] = float(ret.group(1))
                dict["pkgname"] = ret.group(2)
                dict["size"] = ret.group(3)
                dict["period"] = ret.group(4)
                dict["cachename"] = ret.group(5)
                access_record_list.append(dict)

    return access_record_list

def get_access_list(launch_list, all_access_record_list, access_process):
    index = 0
    access_pkgname_list = [[] for row in range(len(launch_list))]
    access_cache_list = [[] for row in range(len(launch_list))]
    access_size_list = [0 for row in range(len(launch_list))]
    access_period_list = [0 for row in range(len(launch_list))]


    for access_record in all_access_record_list:
        uptime = access_record["uptime"]
        pkgname = access_record["pkgname"]
        size = access_record["size"]
        period = access_record["period"]
        cachename = access_record["cachename"]

        for launch in launch_list[index:]:
            start = launch[0]
            end = launch[1]
            if uptime < start:
                break
            if end < uptime:
                index += 1
                continue

            access_pkgname_list[index].append(pkgname)

            if access_process is None:
                access_cache_list[index].append(cachename)
            elif pkgname == access_process:
                access_cache_list[index].append(cachename)

            access_size_list[index] += int(size)
            access_period_list[index] += int(period)

    return access_pkgname_list, access_cache_list, access_size_list, access_period_list

def make_table(input_all_list):
    output_table = {}

    for input_list in input_all_list:
        counter = Counter(input_list)

        for data in counter.most_common():
            if data[0] in output_table:
                output_table[data[0]] += data[1]
            else:
                output_table[data[0]] = data[1]                

    # Sort
    output_table = sorted(output_table.items(), key=lambda x:x[1], reverse=True)

    # Make Header
    table_header = [data[0] for data in output_table]

    output_table_0_filled = []
    for input_list in input_all_list:
        counter = Counter(input_list)
        
        rows = [0 for row in range(len(table_header))]
        for data in counter.most_common():
            rows[table_header.index(data[0])] = data[1]

        output_table_0_filled.append(rows)

    return table_header, output_table_0_filled

def generate_file(filename, table_header, table, launch_list, access_size_list, access_period_list, pkgname):
    with open(filename, "w") as f:
        line = "EMMC access record during " + pkgname + " launch\n"
        line += "appname, start uptime(ms), end uptime(ms), launch period(ms), total emmc access, total access size(kb), total access period(us),"

        for header in table_header:
            line += header + ","
        line += "\n"

        for i, launch in enumerate(table):
            start = launch_list[i][0]
            end = launch_list[i][1]
            period = end - start
            total_access_for_launch = 0
            for data in launch:
                total_access_for_launch += data

            # 2016/01/21 Midashi to data ga zureru ken : Change START
            #if len(launch_list[i]) == 3:
            #    line += launch_list[i][2] + ","
            #line += str(start) + "," + str(end) + "," + str(end - start) + "," + str(total_access_for_launch) + "," + str(access_size_list[i]) + "," + str(access_period_list[i]) + ","
            if len(launch_list[i]) == 3:
                line += launch_list[i][2]
            line += "," + str(start) + "," + str(end) + "," + str(end - start) + "," + str(total_access_for_launch) + "," + str(access_size_list[i]) + "," + str(access_period_list[i]) + ","
            # Change END

            for data in launch:
                line += str(data) + ","
            line += "\n"

        total_access_for_cache = [0 for row in range(len(table_header))]
        for launch in table:
            for i, data in enumerate(launch):
                total_access_for_cache[i] += data
        line += ",,,,,,total,"
        for data in total_access_for_cache:
            line += str(data) + ","

        f.writelines(line)

def get_ranking(input_all_list):
    output_table = {}

    for input_list in input_all_list:
        counter = Counter(input_list)

        for data in counter.most_common():
            if data[0] in output_table:
                output_table[data[0]] += data[1]
            else:
                output_table[data[0]] = data[1]                

    # Sort
    output_table = sorted(output_table.items(), key=lambda x:x[1], reverse=True)
    return  output_table

def make_summary(ranking_process_list, ranking_cache_list, pkgname, topN):
    line = "----- " + pkgname + "-----\n" 
    line += "Total eMMC Access Number\n"
    total = 0
    for process, count in ranking_process_list:
        total += count
    line += str(total) + "\n"

    line += "\n"
    line += "Top " + str(topN) + " eMMC Access Process ranking\n"
    for process, count in ranking_process_list[:topN]:
        line += process + "," + str(count) + "\n"
        
    line += "\n"
    line += "Top " + str(topN) + " eMMC Access Cache ranking\n"
    for cache, count in ranking_cache_list[:topN]:
        line += cache + "," + str(count) + "\n"

    return line

def analyze_emmc_access(filename_logcat, filename_dmesg, pkg_activity_name, topN):
    pkgname = pkg_activity_name.split("/")[0]

    launch_list = get_applaunch_period(filename_logcat, pkg_activity_name)

    all_access_record_list = get_emmc_access_record(filename_dmesg)
    all_pagefault_record_list = get_emmc_pagefault_record(filename_dmesg)

    access_pkgname_list, access_cache_list, access_size_list, access_period_list = \
        get_access_list(launch_list, all_access_record_list, None)

    if len(access_pkgname_list) == 0:
        return

    table_header, table = make_table(access_pkgname_list)
    generate_file(FILENAME + "emmc_access_record_[" + pkgname + "]" + "_process_rank.csv",
                  table_header,
                  table,
                  launch_list,
                  access_size_list,
                  access_period_list,
                  pkg_activity_name)
    
    table_header, table = make_table(access_cache_list)
    generate_file(FILENAME + "emmc_access_record_[" + pkgname + "]" + "_cache_rank.csv",
                  table_header,
                  table,
                  launch_list,
                  access_size_list,
                  access_period_list,
                  pkg_activity_name)

    ranking_process_list = get_ranking(access_pkgname_list)
    ranking_cache_list = get_ranking(access_cache_list)
    
    with open(FILENAME + "emmc_access_record_summary_[" + pkgname + "].csv", "w") as f:
        summary = make_summary(ranking_process_list, ranking_cache_list, pkgname, topN)
        print summary
        f.writelines(summary)

    pagefault_period_list_retry, pagefault_period_list_major, pagefault_period_list_minor = get_pagefault_list(launch_list, all_pagefault_record_list)

    with open(FILENAME + "pagefault_[" + pkgname + "].csv", "w") as f:
        f.writelines("start, end, launch time, retry, major, minor\n")
        for i in range(len(launch_list)):
            f.writelines(str(launch_list[i][0]) + "," + \
                             str(launch_list[i][1]) + "," + \
                             str(launch_list[i][1] - launch_list[i][0]) + "," + \
                             str(pagefault_period_list_retry[i]) + "," + \
                             str(pagefault_period_list_major[i]) + "," + \
                             str(pagefault_period_list_minor[i]) + "\n")
    
def analyze_emmc_access_for_all(filename_logcat, filename_dmesg):
    dict = {}

    for pkg_activity_name in APP_LIST:
        launch_list = get_applaunch_period(filename_logcat, pkg_activity_name)
        pkgname = pkg_activity_name.split("/")[0].replace('"','')
        for i in range(len(launch_list)):
            dict[float(launch_list[i][0])] = pkgname

    pre = 0
    app = "reboot"
    launch_list = []
    for k in sorted(dict.keys()):
        launch_list.append([pre, k, app])
        pre = k
        app = dict[k]
    launch_list.append([pre, 1000000, app])

    all_access_record_list = get_emmc_access_record(filename_dmesg)
    access_pkgname_list, access_cache_list, access_size_list, access_period_list = \
        get_access_list(launch_list, all_access_record_list, None)

    table_header, table = make_table(access_pkgname_list)
    generate_file(FILENAME + "emmc_access_record_all_process_rank.csv",
                  table_header,
                  table,
                  launch_list,
                  access_size_list,
                  access_period_list,
                  "all applications")

def parse_option():
    parser = optparse.OptionParser()
    parser.add_option("-a", "--applist", dest="applist", type="str",
        default="", help="show detail")
    parser.add_option("-n", "--topn", dest="topn", type="int",
        default=5, help="show detail")
    parser.add_option("-f", "--filename", dest="filename", type="str",
        default="", help="show detail")

    options, remainder = parser.parse_args()
    global APP_LIST
    global TOP_N
    global FILENAME

    if options.applist:
        output = []
        with open(options.applist, "r") as f:
            for line in f:
                output.append(line.split(",")[0])
        APP_LIST = output
    TOP_N = options.topn

    if options.filename != "":
        FILENAME = options.filename

if __name__ == "__main__":
    parse_option()

    if len(sys.argv) < 3:
        print "invalid argument"
        sys.exit(1)

    filename_logcat = sys.argv[1]    
    filename_dmesg = sys.argv[2]    

    for pkg_activity_name in APP_LIST:
        analyze_emmc_access(filename_logcat, filename_dmesg, pkg_activity_name, TOP_N)

    analyze_emmc_access_for_all(filename_logcat, filename_dmesg)








