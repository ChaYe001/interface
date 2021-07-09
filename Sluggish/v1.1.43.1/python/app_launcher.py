#!/usr/bin/python
# Copyright (c) 2015 Sony Mobile Communications Inc.

import os, sys, re, commands, string, optparse, subprocess, fcntl
import datetime, time, sched, threading, math, csv, codecs
import tempfile
from numpy import array
import ktrace

#option parameter
QUICKMODE = 0
COUNTER = 5
INC_MODE = 1
FILENAME = ""
DEVICE = ""
APP_LIST = []

ZRAM_USED = True
KSM_USED = True

THERMAL_PATH_EMMC = ""
THERMAL_PATH_MSM = ""
THERMAL_PATH_BATT = ""

DISKSTATS_SYSTEM = ""
DISKSTATS_DATA = ""

start_cycle = 0
test_global_cycle = 0
test_global_counter = 0
logcatthread = None
logcat_event_thread = None
logcat_radio_thread = None
dmesgthread = None

NO_REBOOT = False
DEBUG_LEVEL = 0

RETRY_CNT = 10

#dumpsys parameter
DUMP_OF_SERVICE = ["meminfo", "SurfaceFlinger", "activity", "battery", "cpuinfo", "procstats"]
FLAG_MEMINFO = 1 << 0                           # 'meminfo' on/off FLAG
FLAG_SURFACEFLINGER = 1 << 1                    # 'SurfaceFlinger' on/off FLAG
FLAG_ACTIVITY = 1 << 2                          # 'activity' on/off FLAG
FLAG_BATTERY = 1 << 3                           # 'battery' on/off FLAG
FLAG_CPUINFO = 1 << 4                           # 'cpuinfo' on/off FLAG
FLAG_PROCSTATS = 1 << 5                         # 'procstats' on/off FLAG


#store data list
WHOLE_DATA_LIST = []

FORMAT_LOGCAT_EVENTS_FILE_NAME = "logcat_events.txt"
FORMANT_LOGCAT_RADIO_FILE_NAME = "logcat_radio.txt"

MODE_MAIN = 0
MODE_EVENTS = 1
MODE_RADIO = 2

def popen_logcat(mode):
    logcatcom = ["adb", "shell", "logcat", "-v", "time"]
    if DEVICE:
        logcatcom = ["adb", "-s", DEVICE, "shell", "logcat", "-v", "time"]

    if mode == MODE_EVENTS:
        logcatcom.append("-b")
        logcatcom.append("events")
    elif mode == MODE_RADIO:
        logcatcom.append("-b")
        logcatcom.append("radio")

    process = subprocess.Popen(logcatcom, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fd = process.stdout
    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    return process

class LogcatThread(threading.Thread):
    def __init__(self, filename='logcat.txt', mode=0, name='LogcatThread'):
        self._stopevent = threading.Event()
        self._sleepperiod = 0.5
        self._filename = filename
        self._mode = mode
        self._retry_cnt = 0
        threading.Thread.__init__(self, name=name)

    def run(self):
        utime_from_dtime = lambda x: int(time.mktime(x.timetuple()))
        get_datetime = lambda y: datetime.datetime.strptime("2016-"+y.strip(), '%Y-%m-%d %H:%M:%S')

        def getstarttime():
            raw_start_datetime = adbcommand(["shell","\"date '+%m-%d %H:%M:%S'\""])
            start_datetime = get_datetime(raw_start_datetime)
            return start_datetime

        def get_start_up_time():
            cmd = '''shell 'sec=$(date +%S); while [ "$(date +%S)" = "$sec" ]; do
                     echo -n; done; echo -n "$(date +%m-%d\ %H:%M:%S) "; cat /proc/uptime' '''
            raw = adbcommand([cmd]).split()
            if len(raw) != 4 or len(raw[1].split(":")) != 3:
                return None, None
            if len(raw[2].split(".")) != 2:
                return None, None
            return raw[0] + " " + raw[1], raw[2]

        print "LogcatThread start run"

        start_datetime = None
        try:
            start_datetime = getstarttime()
        except ValueError:
            self._stopevent.wait(1)
            start_datetime = getstarttime()

        self._start_datetime = start_datetime

        date, start_up_time = get_start_up_time()
        i = 0
        while date == None and i < 5:
            i += 1
            time.sleep(1)
            date, start_up_time = get_start_up_time()
        if date == None:
            # Results will be incomplete on some (ODM) platforms
            print "ERROR: Failed getting uptime"

        global FILENAME
        f = open(FILENAME + self._filename,"w", buffering=1)
        print(date + " Logcat start uptime: " + str(start_up_time))
        f.write(date + " Logcat start uptime: " + str(start_up_time) + "\n")
        process = popen_logcat(self._mode)
        while not self._stopevent.isSet():
            try:
                while not process.poll() is None:
                    while self.logcat_clear() == False:
                        if self._retry_cnt < RETRY_CNT:
                            self._retry_cnt += 1
                            if self._mode == MODE_MAIN:
                                print "logcat main connection lost. retry %d/%d" % (self._retry_cnt, RETRY_CNT)
                            elif self._mode == MODE_EVENTS:
                                print "logcat events connection lost. retry %d/%d" % (self._retry_cnt, RETRY_CNT)
                            else:
                                print "logcat radio connection lost. retry %d/%d" % (self._retry_cnt, RETRY_CNT)
                            time.sleep(1)
                        else:
                            if self._mode == MODE_MAIN:
                                print "logcat main disconnect"
                            elif self._mode == MODE_EVENTS:
                                print "logcat events disconnect"
                            else:
                                print "logcat radio disconnect"
                            return

                    process = popen_logcat(self._mode)

                self._retry_cnt = 0
                line = process.stdout.readline().strip()
                raw_line = line.strip().split(".")
                if len(raw_line) < 2:
                    continue
                millisec = raw_line[1].split(" ")[0]
                log_datetime = get_datetime(raw_line[0])
                diff_time = utime_from_dtime(log_datetime) - utime_from_dtime(start_datetime)
                if diff_time < 0:
                    continue
                line = line.strip()
                f.write(line + "\n")
            except IOError:
                self._stopevent.wait(self._sleepperiod)
                pass
            except ValueError:
                self._stopevent.wait(self._sleepperiod)
                pass
        process.terminate()

    def join(self, timeout=None):
        print "LogcatThread join"
        self._stopevent.set()
        threading.Thread.join(self, timeout)

    def logcat_clear(self):
        ret = adbcommand(["shell logcat -c"])
        if ret.strip() == "":
            return True
        else:
            return False

def popen_dmesg():
    flag = True

    dmesgcom = ["adb", "shell", "cat", "/proc/kmsg"]
    if DEVICE:
        dmesgcom = ["adb", "-s", DEVICE, "shell", "cat", "/proc/kmsg"]
    process = subprocess.Popen(dmesgcom, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    fd = process.stdout

    if "Permission denied" in fd.readline():
        flag = False
        process.terminate()
        adbcommand(["root"])
        time.sleep(10)

    fl = fcntl.fcntl(fd, fcntl.F_GETFL)
    fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)

    return process, flag

class DmesgThread(threading.Thread):
    def __init__(self, filename='dmesg.log', name='DmesgThread'):
        self._stopevent = threading.Event()
        self._sleepperiod = 0.5
        self._filename = filename
        self._retry_cnt = 0
        threading.Thread.__init__(self, name=name)

    def run(self):
        global FILENAME
        print "DmesgThread start run"

        process, flag = popen_dmesg()
        if not flag:
            print "Permissin denied for /proc/kmsg"
            #make empty file for the following script
            f = open(FILENAME + "_" + self._filename,"w")
            f.close()
            return

        with open(FILENAME + "_" + self._filename,"w", buffering=1) as f:
            while not self._stopevent.isSet():
                try:
                    while not process.poll() is None:
                        if self._retry_cnt < RETRY_CNT:
                            self._retry_cnt += 1
                            print "kmsg connection lost. retry %d/%d" % (self._retry_cnt, RETRY_CNT)
                            process, flag = popen_dmesg()
                            time.sleep(1)
                        else:
                            print "kmsg disconnect"
                            return
                    self._retry_cnt = 0
                    line = process.stdout.readline().strip()
                    f.write(line + "\n")
                except IOError, e:
#                    print "IOError: " + str(e.args[0])
                    self._stopevent.wait(self._sleepperiod)
                    pass
                except ValueError, e:
#                    print "ValueError: " + str(e.args[0])
                    self._stopevent.wait(self._sleepperiod)
                    pass
            process.terminate()

    def join(self, timeout=None):
        print "DmesgThread join"
        self._stopevent.set()
        threading.Thread.join(self, timeout)

def main():
    global FILENAME
    global do_KTrace
    global logcatthread
    global logcat_event_thread
    global logcat_radio_thread
    global dmesgthread

    prepare()
    start_unix_time = datetime.datetime.today().strftime('%s')
    saveinfo(start_unix_time)

    global process_status_file
    process_status_file = open(FILENAME + "_process_status.csv","w", buffering=1)

    global am_start_time_file
    am_start_time_file = open(FILENAME + "_am_start_time.csv","w", buffering=1)

    if do_KTrace and not ktrace.enable(DEVICE):
            do_KTrace = False
            print "WARNING failed to enable kernel trace logging"

    if do_KTrace:
        ktracethread = ktrace.KTraceThread(DEVICE, FILENAME + "_ktraces.txt")
        ktracethread.start()

    logcatthread = LogcatThread()
    logcatthread.setDaemon(True)
    logcatthread.start()
    time.sleep(2)

    logcat_event_thread = LogcatThread(FORMAT_LOGCAT_EVENTS_FILE_NAME,\
        MODE_EVENTS, "LogcatEventThread")
    logcat_event_thread.setDaemon(True)
    logcat_event_thread.start()
    time.sleep(2)

    logcat_radio_thread = LogcatThread(FORMANT_LOGCAT_RADIO_FILE_NAME,\
        MODE_RADIO, "LogcatRadioThread")
    logcat_radio_thread.setDaemon(True)
    logcat_radio_thread.start()
    time.sleep(2)

    dmesgthread = DmesgThread()
    dmesgthread.setDaemon(True)
    dmesgthread.start()
    time.sleep(8)

    scenario = threading.Thread(name='scenario', target=run_scenario)
    scenario.setDaemon(True)
    scenario.start()

    scenario.join()

    if do_KTrace:
        print "ktracethread join"
        ktracethread.stop.set()
        if ktracethread.proc:
            ktracethread.proc.terminate()
        ktracethread.join()
        print "ktraceThread join end"

    print "LogcatThread join waiting"
    logcatthread.join()
    print "LogcatThread join end"

    print "LogcatEventThread join waiting"
    logcat_event_thread.join()
    print "LogcatEventThread join end"

    print "LogcatRadioThread join waiting"
    logcat_radio_thread.join()
    print "LogcatRadioThread join end"

    print "DmesgThread join waiting"
    dmesgthread.join()
    print "DmesgThread join end"
    saveinfo(start_unix_time)

    process_status_file.close()
    am_start_time_file.close()

    global WHOLE_DATA_LIST

    filename = FILENAME + "_ramcheckresult.csv"
    if QUICKMODE:
        write_dict2csv(WHOLE_DATA_LIST, filename)

def write_dict2csv(datalist, filename):
    with codecs.open(filename, "wb","utf_8_sig") as f:
        csvWriter = csv.writer(f)
        header = sorted(datalist[0].keys())
        csvWriter.writerow(header)
        w = csv.DictWriter(f, sorted(datalist[0].keys()))
        for line in datalist:
            w.writerow(line)

def adbcommand(option_list):
    global DEVICE
    devicecommand = "-s %s "%(DEVICE) if DEVICE else ""
    _command = "adb " + devicecommand + " ".join(option_list)
    ret = commands.getoutput(_command)
    return ret

def adbcommand_cat(option_list):
    global DEVICE
    devicecommand = "-s %s "%(DEVICE) if DEVICE else ""
    ret = ""
    for o in option_list:
        _command = "adb " + devicecommand + "shell cat " + o
        ret = ret + "@@@@@\n" + commands.getoutput(_command) + "\n"
    return ret

def adbcommand_wo_cat(option_list):
    global DEVICE
    devicecommand = "-s %s "%(DEVICE) if DEVICE else ""
    _command = "adb " + devicecommand + "shell dmesg"
    ret = ""
    for o in option_list:
        _command = "adb " + devicecommand + "shell " + o
        ret = ret + "@@@@@\n" + commands.getoutput(_command) + "\n"

    return ret

def getdevicename():
    devices = commands.getoutput("adb devices")
    devicename = devices.split("\n")[1].split("\t")[0]
    return devicename

def saveinfo(u_time):
    global DEVICE
    devicename = DEVICE if DEVICE else getdevicename()
    dumpsys_output = ""
    for i in range(len(DUMP_OF_SERVICE)):
        if DUMPSYS_FLAG & 1 << i != 0:
            command_base = ["shell","dumpsys",DUMP_OF_SERVICE[i]]
            temp_output = adbcommand(command_base)
            dumpsys_output = dumpsys_output + "[" + DUMP_OF_SERVICE[i] + "]\n" + temp_output + "\n"
    procrank = adbcommand(["shell procrank"])

    with open(FILENAME + '_%s_%s.txt'%(devicename, u_time), 'a') as f:
        f.write(dumpsys_output + procrank + "\n----------\n")

    dumpsys_output = adbcommand(["shell cat /proc/pagetypeinfo"])

    with open(FILENAME + '_%s_pagetypeinfo_%s.txt'%(devicename, u_time), 'a') as f:
        f.write(dumpsys_output + "\n----------\n")

def prepare():
    global KSM_USED, ZRAM_USED
    global NO_REBOOT
    global thermal_conf_path

    #check zram config
    zram = adbcommand(["shell cat /sys/block/zram0/mem_used_total"])
    if "No such file or directory" in zram:
        ZRAM_USED = False

    #check ksm confi
    ksm = adbcommand(["shell ls /sys/kernel/mm/ksm/"])
    if "No such file or directory" in ksm:
        KSM_USED = False

    #rm files
    adbcommand(["shell rm -rf /sdcard/CrashDump"])
    adbcommand(["shell rm -rf /sdcard/DCIM"])
    adbcommand(["shell rm -rf /data/data/com.android.providers.media/databases"])
    time.sleep(1)

    #change thermal mitigation configuration
    if thermal_conf_path != "" and thermal_conf_path != "default":
        change_thermal_config()

    #reboot
    if not NO_REBOOT:
        adbcommand(["reboot"])
        time.sleep(60)

    for i in range(120):
        if getdevicename():
            break
        time.sleep(1)

    if getdevicename():
        print "device: ", getdevicename()
    else:
        print "No device"
        sys.exit(1)

    #wait boot complete
    for i in range(120):
        boot_completed = adbcommand(["shell getprop sys.boot_completed"])
        if "1" in boot_completed:
            break
        time.sleep(1)

    if "1" in boot_completed:
        print "Boot completed ok"

    adbcommand(["root"])
    time.sleep(10)

    user = adbcommand(["shell 'echo $USER_ID'"]).strip()
    if user == "0":
        print "Got device root access"
    else:
        print "No root access"
        sys.exit(1)

    if not NO_REBOOT:
        time.sleep(120)

    #stop thermal
    if thermal_conf_path == "default":
        stop_thermal()

    #get thermal path
    global THERMAL_PATH_EMMC
    global THERMAL_PATH_MSM
    global THERMAL_PATH_BATT
    global THERMAL_NAME
    global DISKSTATS_SYSTEM
    global DISKSTATS_DATA

    THERMAL_PATH_EMMC = get_thermal_path("emmc_therm")
    if THERMAL_PATH_EMMC != '/':
        THERMAL_NAME = "emmc"
    else:
        THERMAL_PATH_EMMC = get_thermal_path("ufs_therm")
        if THERMAL_PATH_EMMC != '/':
            THERMAL_NAME = "ufs"
        else:
            THERMAL_PATH_EMMC = get_thermal_path("case")
            if THERMAL_PATH_EMMC != '/':
                THERMAL_NAME = "case"
            else:
                THERMAL_NAME = "unknown"

    THERMAL_PATH_MSM =  get_thermal_path("msm_therm")
    THERMAL_PATH_BATT =  get_thermal_path("battery")
    DISKSTATS_SYSTEM, DISKSTATS_DATA = get_emmc_path()

    global num_sticky
    if num_sticky > 0:
        start_stickyservice(num_sticky)


def start_stickyservice(num_max):
    n = 1
    package_prefix = "com.sonymobile.tests.variableweight.sticky"
    package_suffix = "/.VariableWeightActivity"
    while n <= num_max:
        num = '%02d' % n
        package = package_prefix + num + package_suffix
        print "Launching Sticky : %s" % package
        start_activity_f(package)
        time.sleep(8)
        back_to_home(0)
        time.sleep(1)
        n += 1

    print "Lanching completed!"

def run_scenario():
    global start_cycle
    scheduler = sched.scheduler(time.time, time.sleep)
    scenario = [(saveinfo, 5), (back_to_home, 0), (start_applications, 2)]

    for r in range(COUNTER - start_cycle):
        start_time = time.time()
        one_cycle = 0
        for i, (method, interval) in enumerate(scenario):
            one_cycle += interval
            scheduler.enterabs(start_time + one_cycle, 1, method, (i,))
        scheduler.run()

def get_uptime():
    command_list = ["/proc/uptime"]
    raw_data = adbcommand_cat(command_list)
    splited_raw_data = raw_data.split("@@@@@")
    return splited_raw_data[1].split()[0]

def check_is_process(fullname):
    PS_OPTION = False
    rel_ver = adbcommand(["shell getprop ro.build.version.release"])
    rel_ver = rel_ver.split(".")
    if rel_ver[0] == "O" or rel_ver[0] == "8":
        PS_OPTION = True

    pkg_name = fullname.split("/")[0]
    if PS_OPTION:
        ret = adbcommand(["shell \"ps -A | grep \ " + pkg_name + "$\""])
    else:
        ret = adbcommand(["shell \"ps | grep \ " + pkg_name + "$\""])

    if ret != "":
        isProcess = "True"
    else:
        isProcess = "False"

    uptime = get_uptime()
    process_status_file.writelines(fullname + "," + isProcess + "," + str(uptime) + "\n")

def start_applications(sleeptime):
    global APP_LIST
    global test_global_cycle
    global test_global_counter
    global INC_MODE
    global do_KTrace
    global logcatthread
    global logcat_event_thread
    global logcat_radio_thread
    global dmesgthread

    test_local_counter = 0

    print "cycle: " + str(test_global_cycle+1) + "/" + str(COUNTER)
    for app in APP_LIST:
        if logcatthread.is_alive() == False or \
           logcat_event_thread.is_alive() == False or \
           logcat_radio_thread.is_alive() == False or \
           dmesgthread.is_alive() == False:
            print "logcat or dmsg thread Die. process terminate !!!"
            sys.exit(1)
            break
        if test_local_counter > test_global_cycle and INC_MODE == 1:
            break

        print app
        if QUICKMODE > 0 and test_global_counter % QUICKMODE == 0:
            perform_ram_check()
        check_is_process(app.strip())
        time.sleep(1)

        am_start_time_file.writelines(app.strip() + "," + str(get_uptime()) + "\n")
        if do_KTrace:
            ktrace.set_mark(DEVICE, app.strip())

        if broadcast_enabled != "":
            send_broadcast()

        start_activity_f(app.strip())
        time.sleep(8)

        back_to_home(0)
        time.sleep(1)
        test_local_counter += 1
        test_global_counter += 1
    test_global_cycle += 1

def send_broadcast():
    command_base = "shell am broadcast -a"

    with open(broadcast_enabled, "r") as f:
        for line in f:
            print "Send broadcast %s" % line.strip()
            adbcommand(["%s %s"%(command_base, line.strip())])

def change_thermal_config():
    global thermal_conf_path
    adbcommand(["wait-for-device root"])
    ret = adbcommand(["wait-for-device remount"])
    if "dm_verity is enabled" in ret:
        adbcommand(["wait-for-device disable-verity"])
        adbcommand(["reboot"])
        time.sleep(120)
        adbcommand(["wait-for-device root"])
        ret = adbcommand(["wait-for-device remount"])

    if "remount failed" in ret:
        thermal_conf_path = "default"

    if thermal_conf_path == "heavy":
        ret = adbcommand(["shell getprop | grep ro.build.product"])
        ret = ret.strip().split(" ")
        ret = ret[1].strip("][")
        ret = ret.split("_")
        thermal_conf_path = "./python/thermal_conf/thermal-engine_" + ret[0] + "_sluggish_heavy.conf"
        print "Thermal conf file: %s" % thermal_conf_path
        if not os.path.isfile(thermal_conf_path):
            thermal_conf_path = "default"

    if thermal_conf_path != "default":
        print "Change thermal mitigation configuration."
        adbcommand(["wait-for-device shell mv /etc/thermal-engine.conf /etc/thermal-engine.conf-back"])
        adbcommand(["wait-for-device push %s /etc/thermal-engine.conf"%(thermal_conf_path)])
        adbcommand(["wait-for-device shell rm /system/etc/change.cfg"])
        time.sleep(1)

def stop_thermal():
    print "Stop thermal-engine."
    adbcommand(["shell setprop ctl.stop thermal-engine"])
    time.sleep(5)

def start_activity_f(fullname):
    command_base = "shell am start -n"
    adbcommand(["%s %s -a android.intent.action.MAIN -c android.intent.category.LAUNCHER"%(command_base, fullname)])

def back_to_home(args):
    input_keyevent("3")

def input_keyevent(key):
    command_base = "shell input keyevent"
    adbcommand(["%s %s"%(command_base, key)])

def parse_proc_zoneinfo(raw):
    try:
        cpu = ""
        matcher = {}
        for zone in raw.split("Node 0, zone"):
            splited_zone = zone.split("\n")
            zonename = splited_zone[0].strip()
            r = re.compile("([a-zA-Z :_]*) ([0-9 (), ]*)")
            for proc in splited_zone[1:]:
                line = r.findall(proc)
                if len(line) == 1:
                    head = cpu + line[0][0].strip()
                    tail = line[0][1].strip()
                    if tail.isdigit():
                        if line[0][0].strip() == 'cpu:':
                            cpu = head + tail + ' '
                            continue
                        elif line[0][0].strip() == 'vm stats threshold:':
                            cpu = ""

                        matcher["zoneinfo:" + zonename + ":" + head] = int(tail) * 4
        return matcher
    except:
        print ("WARNING : data analyze fail(parse_proc_zoneinfo): raw = " + raw)
        return ""

def parse_proc_vmstat(raw):
    try:
        matcher = {}
        for proc in raw.split("\n"):
            head_tail = proc.lstrip().split(" ")
            head_tail = [h for h in head_tail if h]
            if len(head_tail) != 2:
                continue
            head, tail = head_tail[0].strip(), head_tail[1].strip()
            if tail.isdigit():
                matcher["vmstat:" + head] = int(tail)
        return matcher
    except:
        print ("WARNING : data analyze fail(parse_proc_vmstat): raw = " + raw)
        return ""

def parse_proc_meminfo(raw):
    try:
        matcher = {}
        x = string.maketrans(" kB", "   ")
        for proc in raw.split("\n"):
            splited = proc.split(":")
            if len(splited) < 2:
                continue
            head, tail = splited[0], splited[1]
            val = tail.translate(x).strip()
            matcher["meminfo:" + head] = int(val)
        return matcher
    except:
        print ("WARNING : data analyze fail(parse_proc_meminfo): raw = " + raw)
        return ""

def parse_proc_diskstats(raw):
    try:
        proc_dict = {}
        for line in raw.split("\n"):
            if DISKSTATS_SYSTEM and DISKSTATS_SYSTEM in line:
                proc_dict["diskstats:system:read IO"] = line.split()[3]
                proc_dict["diskstats:system:write IO"] = line.split()[7]
            if DISKSTATS_DATA and DISKSTATS_DATA in line:
                proc_dict["diskstats:data:read IO"] = line.split()[3]
                proc_dict["diskstats:data:write IO"] = line.split()[7]

        return proc_dict
    except:
        print ("WARNING : data analyze fail(parse_proc_diskstats): raw = " + raw)
        return ""

def parse_thermal_emmc(raw):
    try:
        ret = "0.0"
        if "Is a directory" in raw:
            return ret

        ret = float(raw.strip())/10
        return '%.1f' % ret
    except:
        print ("WARNING : data analyze fail(parse_thermal_emmc): raw = " + raw)
        return ""

def parse_thermal_msm(raw):
    try:
        ret = "0.0"
        if "Is a directory" in raw:
            return ret

        ret = float(raw.strip())/10
        return '%.1f' % ret
    except:
        print ("WARNING : data analyze fail(parse_thermal_msm): raw = " + raw)
        return ""

def parse_thermal_batt(raw):
    try:
        ret = "0.0"
        if "Is a directory" in raw:
            return ret

        ret = float(raw.strip())/1000
        return '%.1f' % ret
    except:
        print ("WARNING : data analyze fail(parse_thermal_batt): raw = " + raw)
        return ""

def parse_proc_buddyinfo(raw):
    try:
        dict = {}
        for zone in raw.split("Node 0, zone"):
            ret = zone.split()
            for i, data in enumerate(ret):
                if i == 0:
                    zonename = data
                if i > 0:
                    dict["buddyinfo:" + zonename + ":2^" +'%02d' % (i-1)] = data

        return dict
    except:
        print ("WARNING : data analyze fail(parse_proc_buddyinfo): raw = " + raw)
        return ""


def parse_zram_used(raw):
    try:
        if "No such file or directory" in raw:
            return 0

        return float(raw) / 1024
    except:
        print ("WARNING : data analyze fail(parse_zram_used): raw = " + raw)
        return ""

def get_uptime():
    uptime_com = "shell cat /proc/uptime"
    uptime = adbcommand([uptime_com])
    try:
        uptime = float(uptime.split(" ")[0])
    except ValueError:
        print ("ERROR(get_uptime): uptime = " + uptime)
        uptime = float(-1)

    return uptime

def parse_uptime(raw):
    try:
        return float(raw.split(" ")[0])
    except:
        print ("WARNING : data analyze fail(parse_uptime): raw = " + raw)
        return ""

def parse_battery_temp(raw):
    try:
        tmpdict = {}

        if "No such file or directory" in raw:
            return tmpdict

        tmpdict["battery_temp"] = float(raw.strip()) / 10
        return tmpdict
    except:
        print ("WARNING : data analyze fail(parse_battery_temp): raw = " + raw)
        return ""

def get_thermal_path(target_label):
    zone_list = adbcommand(["shell ls /sys/class/thermal"]).split()
    ret = "/"

    for zone in zone_list:
        path = "shell cat /sys/class/thermal/" + zone.strip()
        label = adbcommand([path + "/type"]).strip()
        if target_label in label:
            ret = "/sys/class/thermal/" + zone.strip() + "/temp"
    return ret

def get_emmc_path():
    system_name = ""
    data_name = ""

    ret = adbcommand(["shell ls -l /dev/block/bootdevice/by-name | grep system"])
    if ret:
        system_name = ret.split()[-1].split("/")[-1]

    ret = adbcommand(["shell ls -l /dev/block/bootdevice/by-name | grep data"])
    if ret:
        data_name = ret.split()[-1].split("/")[-1]

    return system_name, data_name

def perform_ram_check():
    #prepare command list
    global THERMAL_PATH_EMMC
    global THERMAL_PATH_MSM
    global THERMAL_PATH_BATT
    global THERMAL_NAME
    command_list_w_cat_thermal_emmc =  [THERMAL_PATH_EMMC]
    command_list_w_cat_thermal_msm  =  [THERMAL_PATH_MSM]
    command_list_w_cat_thermal_batt =  [THERMAL_PATH_BATT]

    command_list_w_cat = ["/proc/uptime",
                          "/proc/zoneinfo",
                          "/proc/meminfo",
                          "/proc/vmstat",
                          "/sys/block/zram0/mem_used_total",
                          "/proc/diskstats",
                          "/proc/buddyinfo",
                          "/sys/class/power_supply/battery/temp"]

    #execute command
    raw_data = adbcommand_cat(command_list_w_cat)
    splited_raw_data = raw_data.split("@@@@@")

    raw_data_thermal = adbcommand_cat(command_list_w_cat_thermal_emmc)
    splited_raw_data_thermal_emmc = raw_data_thermal.split("@@@@@")

    raw_data_thermal = adbcommand_cat(command_list_w_cat_thermal_msm)
    splited_raw_data_thermal_msm = raw_data_thermal.split("@@@@@")

    raw_data_thermal = adbcommand_cat(command_list_w_cat_thermal_batt)
    splited_raw_data_thermal_batt = raw_data_thermal.split("@@@@@")

    command_list =\
        command_list_w_cat + \
        command_list_w_cat_thermal_emmc + \
        command_list_w_cat_thermal_msm + \
        command_list_w_cat_thermal_batt

    splited_raw_data =\
        splited_raw_data + \
        splited_raw_data_thermal_emmc + \
        splited_raw_data_thermal_msm + \
        splited_raw_data_thermal_batt

    splited_raw_data = [s for s in splited_raw_data if s]

    #get the result of command
    data_dict = dict(zip(command_list, splited_raw_data))

    #parse the result
    uptime = parse_uptime(data_dict["/proc/uptime"])
    battery_temp = parse_battery_temp(data_dict["/sys/class/power_supply/battery/temp"])
    zoneinfo = parse_proc_zoneinfo(data_dict["/proc/zoneinfo"])
    meminfo = parse_proc_meminfo(data_dict["/proc/meminfo"])
    zram_used = parse_zram_used(data_dict["/sys/block/zram0/mem_used_total"])
    vmstat = parse_proc_vmstat(data_dict["/proc/vmstat"])
    diskstats = parse_proc_diskstats(data_dict["/proc/diskstats"])
    buddyinfo = parse_proc_buddyinfo(data_dict["/proc/buddyinfo"])

    emmc_therm = parse_thermal_emmc(data_dict[THERMAL_PATH_EMMC])
    msm_therm = parse_thermal_msm(data_dict[THERMAL_PATH_MSM])
    battery_therm = parse_thermal_batt(data_dict[THERMAL_PATH_BATT])
    #set the result
    stat = {}
    stat["uptime"] = uptime
    stat.update(battery_temp)
    stat.update(zoneinfo)
    stat.update(meminfo)
    stat["zram_used"] = zram_used
    stat.update(vmstat)
    stat["therm:"+THERMAL_NAME] = emmc_therm
    stat["therm:msm"] = msm_therm
    stat["therm:battery"] = battery_therm
    stat.update(diskstats)
    stat.update(buddyinfo)

    WHOLE_DATA_LIST.append(dict(zip(stat.keys(), stat.values())))
#    for k in sorted(stat.keys()):
#        print k, stat[k]

def parse_option():
    parser = optparse.OptionParser()
    parser.add_option("-c", "--counter", dest="counter", type="int",
        default=5, help="show detail")
    parser.add_option("-d", "--debug", dest="debug", type="int",
        default=0, help="show detail")
    parser.add_option("-s", "--device", dest="device", type="str",
        default="", help="show detail")
    parser.add_option("-a", "--applist", dest="applist", type="str",
        default="", help="show detail")
    parser.add_option("-q", "--quickmode", dest="quickmode", type="int",
        default=1, help="quick mode")
    parser.add_option("-k", "--ktraces", action="store_true", dest="ktrace",
        default=False, help="read kernel traces")
    parser.add_option("-i", "--incmode", dest="incmode", type="int",
        default=1, help="incremental mode")
    parser.add_option("-f", "--filename", dest="filename", type="str",
        default="", help="show detail")
    parser.add_option("-S", "--start-cycle", dest="start_cycle", type="int",
        default=0, help="start cycle")
    parser.add_option("-b", "--broadcast", dest="broadcast", type="str",
        default="", help="file path of broadcast list, send broadcasts before launch application")
    parser.add_option("-T", "--thermal_conf", dest="thermal_conf", type="str",
        default="", help="file path of thermal mitigation configuration")
    parser.add_option("-n", "--num_stickyservice", dest="num_stickyservice", type="int",
        default=0, help="number of sticky service app to launch")
    parser.add_option("--meminfo", action="store_true", dest="meminfo",
        default=False, help="select dump of 'meminfo' service")
    parser.add_option("--SurfaceFlinger", action="store_true", dest="surfaceflinger",
        default=False, help="select dump of 'SurfaceFlinger' service")
    parser.add_option("--activity", action="store_true", dest="activity",
        default=False, help="select dump of 'activity' service")
    parser.add_option("--battery", action="store_true", dest="battery",
        default=False, help="select dump of 'battery' service")
    parser.add_option("--cpuinfo", action="store_true", dest="cpuinfo",
        default=False, help="select dump of 'cpuinfo' service")
    parser.add_option("--procstats", action="store_true", dest="procstats",
        default=False, help="select dump of 'procstats' service")

    options, remainder = parser.parse_args()

    global COUNTER
    COUNTER = options.counter

    global DEBUG_LEVEL
    DEBUG_LEVEL = options.debug

    global NO_REBOOT
    if (DEBUG_LEVEL & 0x1):
        NO_REBOOT = True

    global DEVICE
    DEVICE = options.device

    global start_cycle
    start_cycle = options.start_cycle
    if start_cycle >= COUNTER:
        print "Invalid argument: start cycle >= end cycle"
        sys.exit(1)

    global test_global_cycle
    test_global_cycle = start_cycle
    global test_global_counter
    test_global_counter = start_cycle

    global APP_LIST
    if options.applist:
        output = []
        with open(options.applist, "r") as f:
            for line in f:
                if not "#" in line:
                    output.append(line.replace(",","").replace("\n","").replace("\"",""))
        APP_LIST = output

    global QUICKMODE
    QUICKMODE = options.quickmode

    global do_KTrace
    do_KTrace = options.ktrace

    global INC_MODE
    INC_MODE = options.incmode

    global FILENAME
    if options.filename == "":
        FILENAME = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
    else:
        FILENAME = options.filename

    global DUMPSYS_FLAG
    DUMPSYS_FLAG = 0                                  # command 'dumpsys XXXXX' on/off FLAG

    global broadcast_enabled
    broadcast_enabled = options.broadcast

    global thermal_conf_path
    thermal_conf_path = options.thermal_conf

    global num_sticky
    num_sticky = options.num_stickyservice
    if num_sticky > 50:
        num_sticky = 50

    if options.meminfo:
        DUMPSYS_FLAG = DUMPSYS_FLAG + FLAG_MEMINFO

    if options.surfaceflinger:
        DUMPSYS_FLAG = DUMPSYS_FLAG + FLAG_SURFACEFLINGER

    if options.activity:
        DUMPSYS_FLAG = DUMPSYS_FLAG + FLAG_ACTIVITY

    if options.battery:
        DUMPSYS_FLAG = DUMPSYS_FLAG + FLAG_BATTERY

    if options.cpuinfo:
        DUMPSYS_FLAG = DUMPSYS_FLAG + FLAG_CPUINFO

    if options.procstats:
        DUMPSYS_FLAG = DUMPSYS_FLAG + FLAG_PROCSTATS

    print ("select dumpsys service flag:" + str(bin(DUMPSYS_FLAG)))

    return options

if __name__ == "__main__":
    print "start!!"
    parse_option()
    main()
