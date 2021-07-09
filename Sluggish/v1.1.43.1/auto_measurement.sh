#!/bin/sh
# Copyright (c) 2015 Sony Mobile Communications Inc.

################################
# Test Info
################################
DEVICE_ID=""
SW_LABEL=""
MODLE_NAME=""
SCRIPT_VER="v1.1.43.1"

################################
# Script Definition
################################
#
SCRIPT_PATH=python
FOLDERNAME=`date +%04Y%02m%02d-%02k%02M-%02S`

#Cold boot parameter
APPLIST_FOR_SLUGGISH=${SCRIPT_PATH}/Applist_40.param
COUNT_FOR_SLUGGISH=50

################################
# Script Main
################################
DEVICE_OPTION=""
MODE_OPTION=""
ANALYZE_EMMC=false
DEBUG_FLAG=""
KTRACE_OPT=""
KTRACE=false
TAGS_FLAG=false
OPT_TAGS="default"
BROADCAST_OPTION=""
THERMAL_OPTION="-T default"
STICKY_OPTION=""
HEAVY_FLAG=false

SCRIPTNAME=`basename $0`
if [ $SCRIPTNAME = "heavy_measurement" ]; then
   HEAVY_FLAG=true
fi

while getopts "a:d:eE:ko:m:s:S:t:T:b:h:n:P" arg ; do
    case "${arg}" in
        a)
            APPLIST_FOR_SLUGGISH=${OPTARG}
            ;;
        d)
            DEBUG_FLAG="-d ${OPTARG}"
            ;;
        e)
            ANALYZE_EMMC=true
            ;;
        E)
            COUNT_FOR_SLUGGISH=${OPTARG}
            ;;
        k)
            KTRACE_OPT="-k"
            KTRACE=true
            ;;
        o)
            FOLDERNAME=${OPTARG}
            ;;
        m)
            MODE_OPTION="-m ${OPTARG}"
            ;;
        s)
            DEVICE_OPTION="-s ${OPTARG}"
            ;;
        S)
            STARTCYCLE_OPTION="-S ${OPTARG}"
            ;;
        t)
            OPT_TAGS=${OPTARG}
            TAGS_FLAG=true
            ;;
        T)
            THERMAL_OPTION="-T ${OPTARG}"
            ;;
        b)
            BROADCAST_OPTION="-b ${OPTARG}"
            ;;
        n)
            STICKY_OPTION="-n ${OPTARG}"
            ;;
        P)
            HEAVY_FLAG=true
            ;;
        *)
            echo "Usage ./auto_measurement.sh [OPTION]..."
            echo "Execute sluggish script and measure memory info."
            echo " "
            echo "Option List"
            echo "  -a <file>         Specify the application list. (default=Applist_40.param)"
            echo "  -b <file>         Specify broadcast list. Broadcast items written on list before launch application. (*1)"
            echo "  -d <flag>         Specify whether to reboot on startup of script. (default=1)"
            echo "                         1: do reboot"
            echo "                         0: do not reboot"
            echo "                         e.g.) $ ./auto_measurement.sh -d 0"
            echo "  -e                Analyze emmc access. (*1)"
            echo "  -E <num>          Specify end cycle. (NOTE: Do not specify 0. default=50)"
            echo "                         when you want to execute until 5 cycles"
            echo "                         e.g.) $ ./auto_measurement.sh -E 5"
            echo "  -h                Show this help message."
            echo "  -m <type>         Specify special device. (when sluggish is executed on a terminal that is not sony mobile.)"
            echo "                         m9:      for HTC device"
            echo "                         odm-mtk: for odm device"
            echo "                         mtp:     for qualcomm device"
            echo "  -o <folder>       Specify output folder. (NOTE: Can not use '_' for folder name. default=./yyyymmdd-hhmm-ss/)"
            echo "  -s <device_id>    Specify device."
            echo "                         e.g.) $ ./auto_measurement.sh -s CB5129YJ11"
            echo "  -S <num>          Specify start cycle. (default=0)"
            echo "                         when you want to execute from 10 cycle"
            echo "                         e.g.) $ ./auto_measurement.sh -S 10"
            echo "  -t <tag_name>     Specify tag name to be added the test result. (*1)"
            echo "  -T <file>         Specify thermal mitigation configuration."
            echo "  -P                Evaluate in heavy condition environment."
            echo "  -n <num>          Specify number of sticky service app to launch. (NOTE: Max=50)"
            echo " "
            echo "*1 Advance preparation is necessary for execution. Refer to following page."
            echo "Sluggish script confluence page: <http://confluence.sonymobile.net/display/SPERF/Sluggish+Script>"
            exit 1
            ;;
    esac
done
shift $(($OPTIND - 1))

[ -z "$1" ] || DEVICE_OPTION="-s $1"

if [ "$MODE_OPTION" != "" ]; then
    THERMAL_OPTION=""
fi

if $HEAVY_FLAG ; then
    echo "Heavy Condition Measurement!"
    if [ "$THERMAL_OPTION" = "-T default" ]; then
        THERMAL_OPTION="-T heavy"
    fi
    if [ "$BROADCAST_OPTION" = "" ]; then
        BROADCAST_OPTION="-b ${SCRIPT_PATH}/broadcast.list"
    fi
    if [ "$STICKY_OPTION" = "" ]; then
        STICKY_OPTION="-n 30"
    fi
fi

FILENAME_FOR_SLUGGISH=${FOLDERNAME}/intermediates/COLDBOOT

mkdir ${FOLDERNAME}
mkdir ${FOLDERNAME}/intermediates
mkdir ${FOLDERNAME}/outputs
mkdir ${FOLDERNAME}/outputs/logs
mkdir ${FOLDERNAME}/outputs/lmk
mkdir ${FOLDERNAME}/outputs/lmk/details
mkdir ${FOLDERNAME}/outputs/ramcheck
if $ANALYZE_EMMC ; then
	mkdir ${FOLDERNAME}/outputs/emmc
	mkdir ${FOLDERNAME}/outputs/emmc/summary
	mkdir ${FOLDERNAME}/outputs/emmc/cache_rank
	mkdir ${FOLDERNAME}/outputs/emmc/process_rank
	mkdir ${FOLDERNAME}/outputs/emmc/pagefault
fi

DEVICE_ID=`adb ${DEVICE_OPTION} shell getprop ro.serialno`
SW_LABEL=`adb ${DEVICE_OPTION} shell getprop ro.build.id`
MODLE_NAME=`adb ${DEVICE_OPTION} shell getprop ro.build.product`

echo "Test Info:"
echo "\tData file: "${FOLDERNAME}
echo "\tModel: "${MODLE_NAME}
echo "\tDevice ID: "${DEVICE_ID}
echo "\tSW label":${SW_LABEL}

# Save test info to TestInfo.csv
echo "Data file" > ${FOLDERNAME}/TestInfo.csv
echo ${FOLDERNAME} >> ${FOLDERNAME}/TestInfo.csv
echo "Prototype,Device ID" >> ${FOLDERNAME}/TestInfo.csv
echo ${MODLE_NAME},${DEVICE_ID} >> ${FOLDERNAME}/TestInfo.csv
echo "SWBase,patches" >> ${FOLDERNAME}/TestInfo.csv
echo ${SW_LABEL} >> ${FOLDERNAME}/TestInfo.csv
echo "script" >> ${FOLDERNAME}/TestInfo.csv
echo ${SCRIPT_VER} >> ${FOLDERNAME}/TestInfo.csv
echo "Run command" >> ${FOLDERNAME}/TestInfo.csv
echo  $0 $* >> ${FOLDERNAME}/TestInfo.csv
echo "Application list" >> ${FOLDERNAME}/TestInfo.csv
echo ${APPLIST_FOR_SLUGGISH} >> ${FOLDERNAME}/TestInfo.csv

## measurement for sluggish cold boot

python ${SCRIPT_PATH}/app_launcher.py \
    -c ${COUNT_FOR_SLUGGISH} \
    -a ${APPLIST_FOR_SLUGGISH} ${DEVICE_OPTION} \
    -i 1 \
    -q 1 \
    -f ${FILENAME_FOR_SLUGGISH} \
    ${BROADCAST_OPTION} \
    ${THERMAL_OPTION} \
    ${STICKY_OPTION} \
    ${STARTCYCLE_OPTION} ${DEBUG_FLAG} ${KTRACE_OPT} \
    --meminfo

if [ -r ${FILENAME_FOR_SLUGGISH}logcat.txt ]; then
    python ${SCRIPT_PATH}/make_logcat_log_with_uptime.py \
        ${FILENAME_FOR_SLUGGISH}logcat.txt \
        -f ${FILENAME_FOR_SLUGGISH}_uptime_logcat.txt
else
    exit 1
fi

python ${SCRIPT_PATH}/applaunchtimecheck.py \
    $MODE_OPTION -f ${FILENAME_FOR_SLUGGISH}_uptime_logcat.txt

python ${SCRIPT_PATH}/make_boottime_files.py \
    ${APPLIST_FOR_SLUGGISH} \
    ${FILENAME_FOR_SLUGGISH}_process_status.csv \
    ${FILENAME_FOR_SLUGGISH}_uptime_applaunchtime.csv

echo ${FILENAME_FOR_SLUGGISH}_uptime_applaunchtime_summary.csv is generated
sleep 1

if [ "$MODE_OPTION" != "-m odm-mtk" ]; then
    python ${SCRIPT_PATH}/calclmk.py \
        ${FILENAME_FOR_SLUGGISH}_uptime_logcat.txt \
        ${FILENAME_FOR_SLUGGISH}_dmesg.log \
        ${APPLIST_FOR_SLUGGISH} \
        -f ${FILENAME_FOR_SLUGGISH}_lmk_summary.csv
fi

if $ANALYZE_EMMC ; then
    python ${SCRIPT_PATH}/analyze_emmc_access.py \
        ${FILENAME_FOR_SLUGGISH}_uptime_logcat.txt \
        ${FILENAME_FOR_SLUGGISH}_dmesg.log \
        -f ${FILENAME_FOR_SLUGGISH}_ \
        -a ${APPLIST_FOR_SLUGGISH}
    mv ${FILENAME_FOR_SLUGGISH}_*_cache_rank.csv ${FOLDERNAME}/outputs/emmc/cache_rank
    mv ${FILENAME_FOR_SLUGGISH}_*_process_rank.csv ${FOLDERNAME}/outputs/emmc/process_rank
    mv ${FILENAME_FOR_SLUGGISH}_*emmc*_summary_*.csv ${FOLDERNAME}/outputs/emmc/summary
    mv ${FILENAME_FOR_SLUGGISH}_pagefault*.csv ${FOLDERNAME}/outputs/emmc/pagefault
fi

if $KTRACE ; then
    python ${SCRIPT_PATH}/ktrace.py \
        ${FILENAME_FOR_SLUGGISH}_uptime_applaunchtime.csv \
        ${FILENAME_FOR_SLUGGISH}_ktraces.txt \
        -o ${FILENAME_FOR_SLUGGISH}_major_page_fault_summary.csv
    mv ${FILENAME_FOR_SLUGGISH}_major_page_fault_summary.csv ${FOLDERNAME}/outputs/
fi
sleep 10

echo "Generating a bugreport..."
adb ${DEVICE_OPTION} bugreport > ${FOLDERNAME}/outputs/Bugreport_${DEVICE_ID}_finial.txt

mv ${FILENAME_FOR_SLUGGISH}_uptime_applaunchtime_summary.csv ${FOLDERNAME}/outputs/
mv ${FILENAME_FOR_SLUGGISH}_uptime_applaunchtime.csv ${FOLDERNAME}/outputs/
mv ${FILENAME_FOR_SLUGGISH}_uptime_applaunchtime_average_boot_times.csv ${FILENAME_FOR_SLUGGISH}_average_boot_times.csv
mv ${FILENAME_FOR_SLUGGISH}_average_boot_times.csv ${FOLDERNAME}/outputs/
cp ${FILENAME_FOR_SLUGGISH}_dmesg.log ${FOLDERNAME}/outputs/logs/
mv ${FILENAME_FOR_SLUGGISH}_uptime_logcat.txt ${FOLDERNAME}/outputs/logs/
mv ${FILENAME_FOR_SLUGGISH}_lmk_summary.csv ${FOLDERNAME}/outputs/lmk/
mv ${FILENAME_FOR_SLUGGISH}_lmk_*.csv ${FOLDERNAME}/outputs/lmk/details/
mv ${FILENAME_FOR_SLUGGISH}_ramcheckresult.csv ${FOLDERNAME}/outputs/ramcheck/
cp ${0} ./${FOLDERNAME}/
zip ${FOLDERNAME} -r ${FOLDERNAME}
mv ${FOLDERNAME}.zip ${FOLDERNAME}/

####################################
# Save sluggish result to db
#####################################

if $TAGS_FLAG ; then
    python ${SCRIPT_PATH}/storedb.py \
        ${DEVICE_OPTION} \
        -a ${APPLIST_FOR_SLUGGISH} \
        -r ${FILENAME_FOR_SLUGGISH}_process_status_updated.csv \
        -t ${OPT_TAGS} \
        -i ${COUNT_FOR_SLUGGISH}
fi
