#!/usr/bin/python2
import time, optparse, os, sys, MySQLdb, datetime

from device import Device
from ave.broker import Broker
from ave.broker.exceptions import NoSuch, Busy
from ave.network.exceptions import ConnectionTimeout

TARGET_PHONE = ""
TARGET_RESULT_FILE = ""
TARGET_APP_LIST = ""
REQUEST_TAGS = ""
ITERATION = 0

DB_HOST = "jptolx23397"
DB_USER = "root"
DB_PASS = "systemperformance"
DB_NAME = "dustbenchmarkapp"

SELECT_PACKAGE_ID = "select id from package where name='%s' AND activity='%s' AND versioncode='%s' AND versionname='%s'"

INSERT_NEW_PACKAGE = "INSERT INTO package(name, activity, versioncode, versionname) VALUES('%s', '%s', '%s', '%s')"

SELECT_DEVICE_ID = "select id from device where serialno='%s' AND imei='%s'"

INSERT_NEW_DEVICE = "INSERT INTO device(serialno, imei, chipsetinfo) VALUES('%s', '%s', '')"

INSERT_NEW_SESSION = "INSERT INTO session(ignore_reason, starttime, deviceid, product, swlabel, " \
                     "buildtype, cdfid, cdfrev, iterations, completed, endtime, operator, externalsdcard)" \
                     "VALUES('%s','%s', %d, '%s','%s','%s','%s','%s', %d, %d, '%s','%s', %d)"

INSERT_NEW_SLUGGISH_RESULT = "INSERT INTO sluggish(sessionid, packageid, bootmode, elapsed, period)" \
                             "VALUES(%d, %d, '%s', %f, %f)"

INSERT_SESSION_TAGS = "INSERT INTO sluggish_session(sessionid, tags, iteration) VALUES(%d, '%s', %d)"

def main():
    print "Start storing results to database"

    if TARGET_RESULT_FILE == "":
        print "ERROR: Result file is required."
        return

    if TARGET_APP_LIST == "":
        print "ERROR: App list is required."
        return

    # Allocate ave instances
    broker, handset, workspace = _allocate_handset(TARGET_PHONE)
    # Create device which is handset wrapper
    device = Device(handset)

    # Create database connection
    db_connection = MySQLdb.connect(host=DB_HOST, user=DB_USER, passwd=DB_PASS, db=DB_NAME, charset='utf8')

    # Get Device ID
    imei = device.get_imei()
    device_id = _get_device_id(db_connection, TARGET_PHONE, imei)

    # Get Session ID
    ignore_reason = ""
    start_time = datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")
    device_id_int = int(device_id)
    product = device.get_product_name()
    swlabel = device.get_build_label()
    buildtype = "userdebug"
    cdfid = device.get_cdf_id()
    cdfrev = device.get_cdf_rev()
    iterations = 1
    completed = 1
    endtime = start_time
    operator = ""
    externalsdcard = 0

    session_id = _get_session_id(db_connection, ignore_reason, start_time, device_id_int, product, swlabel, \
                                 buildtype, cdfid, cdfrev, iterations, completed, endtime, operator, externalsdcard)

    _add_sluggish_session(db_connection, session_id, REQUEST_TAGS, ITERATION)

    package_list = []

    # Check app list and get app id from database
    with open(TARGET_APP_LIST, "r") as f:
        for line in f:
            package_name = line.split('/')[0]
            package_version_code = device.get_package_version_code(package_name)
            package_version_name = device.get_package_version_name(package_name)

            package_id = _get_package_id(db_connection, package_name, line, package_version_code, package_version_name)
            package_list.append({
                "package_name" : package_name,
                "package_activity" : line,
                "package_id" : package_id
            })

    # Read from result file
    with open(TARGET_RESULT_FILE, "r") as f:
        isfirst = True
        for line in f:
            if isfirst:
                isfirst = False
            else:
                values = line.split(',')

                package_id = -1
                for p in package_list:
                    if p['package_activity'] == values[0]:
                        package_id = p['package_id']

                bootmode = values[1]
                elapsed = float(values[3])
                period = -1
                try:
                    period = float(values[4])
                except:
                    print "WARN: Can't convert to float period value."
                _add_sluggish_result(db_connection, session_id, package_id, bootmode, elapsed, period)

    db_connection.close()

def _get_package_id(db_connection, package_name, activity, package_version_code, package_version_name):
    package_id = -1

    cursor = db_connection.cursor()
    cursor.execute(SELECT_PACKAGE_ID % (package_name, activity, package_version_code, package_version_name))

    r = cursor.fetchall()
    for rs in r:
        package_id = rs[0]

    cursor.close()

    if package_id > -1:
        return package_id
    else:
        return _add_package_id(db_connection, package_name, activity, package_version_code, package_version_name)

def _add_package_id(db_connection, package_name, activity, package_version_code, package_version_name):
    cursor = db_connection.cursor()
    cursor.execute(INSERT_NEW_PACKAGE % (package_name, activity, package_version_code, package_version_name))
    db_connection.commit()

    package_id = cursor.lastrowid
    cursor.close()

    return package_id

def _get_device_id(db_connection, serialno, imei):
    device_id = -1

    cursor = db_connection.cursor()
    cursor.execute(SELECT_DEVICE_ID % (serialno, imei))

    r = cursor.fetchall()
    for rs in r:
        device_id = rs[0]

    cursor.close()

    if device_id > -1:
        return device_id
    else:
        return _add_device_id(db_connection, serialno, imei)

def _add_device_id(db_connection, serialno, imei):
    cursor = db_connection.cursor()
    cursor.execute(INSERT_NEW_DEVICE % (serialno, imei))
    db_connection.commit()

    device_id = cursor.lastrowid
    cursor.close()

    return device_id

def _get_session_id(db_connection, ignore_reason, start_time, device_id, product, swlabel, \
                    buildtype, cdfid, cdfrev, iterations, completed, endtime, operator, externalsdcard):
    cursor = db_connection.cursor()
    cursor.execute(INSERT_NEW_SESSION % (ignore_reason, start_time, device_id, product, swlabel, \
                    buildtype, cdfid, cdfrev, iterations, completed, endtime, operator, externalsdcard))
    db_connection.commit()

    session_id = cursor.lastrowid
    cursor.close()

    return session_id

def _add_sluggish_result(db_connection, sessionid, packageid, bootmode, elapsed, period):
    cursor = db_connection.cursor()
    cursor.execute(INSERT_NEW_SLUGGISH_RESULT % (sessionid, packageid, bootmode, elapsed, period))
    db_connection.commit()

    session_id = cursor.lastrowid
    cursor.close()

    return session_id

def _add_sluggish_session(db_connection, session_id, REQUEST_TAGS, ITERATION):
    cursor = db_connection.cursor()
    cursor.execute(INSERT_SESSION_TAGS % (session_id, REQUEST_TAGS, ITERATION))
    db_connection.commit()
    cursor.close()

def _allocate_handset(serial):
    if serial != '':
        profiles = ({'type':'handset', 'platform':'android', 'serial':serial}, {'type':'workspace'})
    else:
        profiles = ({'type':'handset', 'platform':'android'}, {'type':'workspace'})

    broker = Broker()

    try:
        h, w = broker.get(*profiles)
    except (NoSuch, Busy, ConnectionTimeout) as e:
        print('Failed to allocate handset:[%s].' %(e))  # @UndefinedVariable
        sys.exit(vcsjob.BUSY)
    except Exception as e:
        print_exc()
        # pre-condition; broker must be available: BLOCKED
        sys.exit(vcsjob.BLOCKED)

    return broker, h, w

###
# Option Parser
###
def parse_option():
    parser = optparse.OptionParser()
    parser.add_option("-s", "--device", dest="device", type="str",
        default="", help="Specify device name. You can get by using adb devices command.")
    parser.add_option("-a", "--applist", dest="applist", type="str",
                      default="", help="Sluggish measurement app list")
    parser.add_option("-r", "--result", dest="result", type="str",
                      default="", help="Sluggish result file path to COLDBOOT_process_status_updated.csv ")
    parser.add_option("-t", "--tags", dest="tags", type="str",
                      default="", help="What is this measurement for? You can use tags for search results later.")
    parser.add_option("-i", "--iteration", dest="itr", type="int",
                      default=0, help="Iteration for sluggish script")

    options, remainder = parser.parse_args()

    global TARGET_PHONE
    TARGET_PHONE = options.device

    global TARGET_RESULT_FILE
    TARGET_RESULT_FILE = options.result

    global TARGET_APP_LIST
    TARGET_APP_LIST = options.applist

    global REQUEST_TAGS
    REQUEST_TAGS = options.tags

    global ITERATION
    ITERATION = options.itr

if __name__ == "__main__":
    parse_option()
    main()