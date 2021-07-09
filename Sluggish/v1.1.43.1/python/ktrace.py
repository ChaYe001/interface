#!/usr/bin/python
# Copyright (c) 2016 Sony Mobile Communications Inc.

import commands, subprocess, threading, time, optparse, sys, re

ktrace_base = "/sys/kernel/debug/tracing/"
ktrace_events = "/sys/kernel/debug/tracing/events/"

TRACES = [ "filemap/mm_filemap_fault_end/" ]

def adb_shell(device, command):
    devicecommand = "-s %s "%(device) if device else ""
    _command = "adb " + devicecommand + "shell '" + command + "'"
    ret = commands.getoutput(_command)
    return ret

def enable(device):
    f_enable = ktrace_base + "tracing_on"
    ret = adb_shell(device, "echo 1 > " + f_enable + "; cat " + f_enable).strip()
    if ret != "1":
        return False

    for trace in TRACES:
        f_enable = ktrace_events + trace + "enable"
        cmd = "if [ -f " + f_enable + " ]; then echo 1 > " + f_enable + "; cat " + f_enable + "; else echo 0; fi"
        ret = adb_shell(device, cmd).strip()
        if ret != "1":
            return False
    return True

def set_mark(device, trace_id):
    f_mark = ktrace_base + "trace_marker"
    ret = adb_shell(device, "echo " + trace_id + " > " + f_mark + ";echo $?").strip()
    if ret != "1":
        return False
    return True

def open_trace(device = ""):
    f_pipe = ktrace_base + "trace_pipe"
    if device:
        cmd = ["adb", "-s", device, "shell", "cat", f_pipe]
    else:
        cmd = ["adb", "shell", "cat", f_pipe]
    return subprocess.Popen(cmd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)

class KTraceThread(threading.Thread):
    def __init__(self, device, filename='ktrace.txt', name='KTraceThread'):
        self.stop = threading.Event()
        self._filename = filename
        self._device = device
        self.proc = None
        threading.Thread.__init__(self, name=name)

    def run(self):
        self.proc = open_trace(self._device)
        if self.proc.poll() != None:
            print "Failed to open kernel trace"
            return False

        print "Start read kernel trace"

        f = open(self._filename,"w", buffering=1)

        while not self.stop.isSet():
            try:
                if self.proc.poll() != None:
                    if self.proc.poll() == 255:
                        self.stop.set()
                    else:
                        self.proc = open_trace(self._device)
                    continue

                line = self.proc.stdout.readline().strip()
#                print line
                f.write(line + "\n")
            except IOError:
                self.stop.set()
                pass
            except KeyboardInterrupt:
                self.stop.set()
                pass

        f.close()
        try:
            self.proc.terminate()
        except OSError:
            pass

# ----------------------- POST PROCESSING -------------------------------------

def parse_applaunchfile(filename):
    times = {}
    with open(filename,"r") as f:
        for line in f:
            data = line.strip().split(",")
            if len(data) != 4:
                print "Invalid data in file \"" + filename + "\""
                sys.exit(1)
            name = data[1]
            data = [float(data[0]), (float(data[0]) + float(data[3]))]
            if times.has_key(name):
                times[name].append(data)
            else:
                times[name] = [data]

    return times

def find_launch_near(time, pkg, launch_list):
    if not launch_list.has_key(pkg):
        return 0, 0

    for launch in launch_list[pkg]:
        if abs(launch[0] - time) < 2.0:
            return launch
    return 0, 0

def parse_ktracefile(filename, launch_list):
    times = []
    out = {}
    package = None
    debug = False

    with open(filename,"r") as f:
        for line in f:
            line = line.strip()
            if debug and package: print "LINE: " + line
            if 'tracing_mark_write' in line:
                if package != None:
                    if debug: print "END " + package
                    out[package].append([start, end - start, num_flt,
                            float(tot_time_us) / 1000, max_qlen, files])

                data = line.split('tracing_mark_write:')
                time = float(data[0].split()[-1][0:-1])
                package = data[1].split('/')[0].strip()
                start, end = find_launch_near(time, package, launch_list)
                if start == 0 or end == 0:
                    print "No matching launch for \"" + package + "\" at " + str(time)
                    package = None
                if debug: print "PACKAGE: %s TIME %f %f %f" % (package, time, start, end)
                if not out.has_key(package):
                    out[package] = []
                max_qlen = 0
                num_flt = 0
                tot_time_us = 0
                files = ""
                continue

            if package == None:
                if debug: print "no pkg: " + line
                continue

            data = line.split("mm_filemap_fault_end:")
            if len(data) != 2:
                print >> sys.stderr, "Ignoring line \"%s\"" % line
                continue

            try:
                time = float(data[0].split()[-1][0:-1])
                filename, data = data[1].split('offset=')
                filename = filename.strip()
                offset, time_us, qlen = data.split()
                offset = int(offset)
                time_us = int(time_us.split('=')[1])
                qlen = int(qlen.split('=')[1])
            except ValueError:
                print >> sys.stderr, "Unable to parse \"%s\"" % line
                continue

            if time >= start and time <= end:
                if qlen > max_qlen:
                    max_qlen = qlen
                num_flt += 1
                tot_time_us += time_us
                if not filename in files:
                    files += '"' + filename + '" '
            if time > end:
                if debug: print "END " + package
                out[package].append([start, end - start, num_flt,
                        float(tot_time_us) / 1000, max_qlen, files])
                package = None
    return out

def parse_option():
    parser = optparse.OptionParser()
    parser.add_option("-o", "--outfile", dest="outfile", type="str",
        default="majpgflt.csv", help="out file name")

    options, remainder = parser.parse_args()

    if len(remainder) != 2:
        print "Usage: ktrace.py [-o outfile] <applaunchtimes file> <ktraces file>"
        sys.exit(1)

    outfile = options.outfile

    return [remainder[0], remainder[1], outfile]

if __name__ == "__main__":
    applfile, ktracefile, outfile = parse_option()
    launch_times = parse_applaunchfile(applfile)
    ktrace = parse_ktracefile(ktracefile, launch_times)

    with open(outfile, "w") as f:
        f.write("package,uptime,launch_time,num_pgflt,time_pgflt_ms,max_qlen,files\n")
        for pkg in ktrace.keys():
            for l in ktrace[pkg]:
                out = pkg + ","
                for field in l:
                    out += str(field) + ","
                out = out[0:-1] + "\n"
                f.write(out)


# TEST CODE BELOW
#    print "start!!"
#    enable("")

#    t = KTraceThread("", "test.txt")
#    t.start()
#    time.sleep(5)
#    set_mark(None, "trace_test")
#    time.sleep(5)

#    print "Thread join"
#    t.stop.set()
#    if t.proc:
#        t.proc.terminate()
#    t.join()
#    print "Thread join end"

