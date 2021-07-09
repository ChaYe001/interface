#!/usr/bin/python2
import re, time, os

from ave.broker import Broker

class Device:
    # Key code values from Android SDK
    # http://developer.android.com/reference/android/view/KeyEvent.html
    KEYCODE_HOME = 3
    KEYCODE_BACK = 4

    am_facebook = "com.facebook.katana/.LoginActivity"
    am_twitter = "com.twitter.android/.StartActivity"

    thermalconf_path = "/etc/thermal-engine.conf"
    thermalconf_back_path = "/etc/thermal-engine.conf-back"

    def __init__(self, handset):
        # self.serial = serial
        # self.broker, self.handset, self.workspace = self._allocate_handset(serial)
        self.handset = handset

    # Wraps all methods in the Handset allocated through AVE
    def __getattr__(self, name):
        return getattr(self.handset, name)

    def factory_reset(self):
        self.press_key(self.KEYCODE_HOME)
        self.shell('am broadcast -a android.intent.action.MASTER_CLEAR')

        # Wait until the phone is rebooted
        self.wait_power_state('offline', timeout = 3*60)
        self.wait_power_state('boot_completed', timeout = 15*60)

        print "Start init device..."
        self._init_device()

    ##
    # Local API
    ##
    def _init_device(self):
        print "Disable DM verity (if configured)"
        self.root()
        self.disable_dm_verity(reboot=True)

        print "Init device for benchmarking"
        print "Root and remount device"
        self.root()
        self.remount()

        print "Disable USB dialog"
        self._disbale_usb_always_ask()
        print "Calling: disable_upload_reminder"
        self.disable_upload_reminder()
        print "Calling: disable_keyguard"
        self.disable_keyguard()
        print "Calling: uninstall_learning_client"
        self.uninstall_learning_client()
        print "Calling: disable_setup_wizard"
        self.disable_setup_wizard()
        print "Calling: disable_pc_companion"
        self.disable_pc_companion()
        print "Calling: disable_auto_power_off"
        self.disable_auto_power_off()
        print "Calling: disable_data_disclaimer"
        self.disable_data_disclaimer()
        print "Calling: disable_waterproof"
        self.disable_waterproof()
        print "Calling: disable_package_verifier"
        self.disable_package_verifier()
        print "Calling: disable_charge_state_dialog"
        self.disable_charge_state_dialog()
        print "Calling: disable_volume_warning"
        self.disable_immersive_mode()
        print "Calling: disable_immersive_mode"
        self.disable_volume_warning(True)

        print "Turn on display and keep it awake"
        self.screen_on(True)
        self.shell("am startservice -a com.sony.semctools.ave.gort.SET_SCREEN_TIMEOUT --ei screen_timeout 7200000")
        self.execute_gort()
        self.stay_awake(True)

        # self.set_locale('en_US')
        # self.set_flight_mode(True)
        self.navigateToHomeScreen()

    def navigateToHomeScreen(self):
        print "Navigate to Homescreen"
        self.press_key(self.KEYCODE_BACK)
        self.press_key(self.KEYCODE_BACK)
        self.press_key(self.KEYCODE_HOME)

    def google_login(self, gid, passwd):
            print "Start Google login. Wait a moment...."

            # Move to home screen
            self.navigateToHomeScreen()
            # Launch Google Play to set a Google account
            self.shell('am start -n com.android.vending/com.google.android.finsky.activities.LaunchUrlHandlerActivity --activity-clear-top')
            time.sleep(60)

            # Google ID Screen
            self.press_key(20)  # Down Key
            self.press_key(20)  # Down Key
            print "Input text %s" % gid
            self.shell("input text " + gid)
            self.press_key(66)  # Enter
            self.click_item_with_id("next_button")
            print "Go to next screen"

            # Password Screen
            time.sleep(60)
            print "Input text %s" % passwd
            self.shell("input text " + passwd)
            time.sleep(3)
            self.press_key(66)  # Enter

            # License Screen
            print "Go to license screen"
            time.sleep(60)
            self.press_key(20)  # Down Key
            self.press_key(20)  # Down Key
            self.press_key(66)  # Enter

            # Google service Screen
            print "Go to Google Service screen"
            time.sleep(30)
            self.press_key(20)  # Down Key
            self.press_key(20)  # Down Key
            self.press_key(20)  # Down Key
            self.press_key(20)  # Down Key
            self.press_key(20)  # Down Key
            self.press_key(66)  # Enter

            # Credit Card Screen
            print "Go to credit card screen"
            time.sleep(30)
            self.press_key(20)  # Down Key
            self.press_key(66)  # Enter
            self.press_key(20)  # Down Key
            self.press_key(66)  # Enter
            time.sleep(10)

            # Open settings view
            print "Open play store settings view"
            self.shell('am start -n com.android.vending/com.google.android.finsky.activities.SettingsActivity --activity-clear-top')
            time.sleep(5)

            # Setting Auto Update
            print "Disabling auto update"
            self.press_key(160)  # NUMPAD_ENTER Key
            time.sleep(3)

            print "Disable notifications"
            self.press_key(19)  # Up Key
            self.press_key(19)  # Up Key
            self.press_key(19)  # Up Key
            self.press_key(66)  # Enter
            time.sleep(3)

            # Settings Notification
            self.press_key(20)  # Down Key
            self.press_key(20)  # Down Key
            self.press_key(20)  # Down Key
            self.press_key(160)  # NUMPAD_ENTER Key
            self.press_key(20)  # Down Key
            self.press_key(160)  # NUMPAD_ENTER Key
            time.sleep(3)

            # Move to home screen
            self.navigateToHomeScreen()

    def facebook_login(self, fbid, fbpasswd):
        print "Start Facebook login. Wait a moment...."

        self.shell('am start -n %s' % self.am_facebook)
        time.sleep(10)

        self.press_key(20)  # Right Key
        print "Input text %s" % fbid
        self.shell("input text " + fbid)

        self.press_key(20)  # Down Key
        print "Input text %s" % fbpasswd
        self.shell("input text " + fbpasswd)

        self.press_key(61)  # Down Key
        self.press_key(66)  # Down Key

        time.sleep(10)
        self.navigateToHomeScreen()

    def facebook_logout(self, tp_scroll_down, tp_logout_button, tp_logout_confirm):
        print "Start Facebook logout. Wait a moment...."

        self.shell('am start -n %s' % self.am_facebook)
        time.sleep(10)

        self.press_key(22)  # Right Key
        self.press_key(22)  # Right Key
        self.press_key(22)  # Right Key
        self.press_key(22)  # Right Key

        for x in range (0, 6):
            self.shell("input touchscreen swipe %s" % tp_scroll_down)

        time.sleep(5)
        self.shell("input touchscreen tap %s" % tp_logout_button)
        time.sleep(2)
        self.shell("input touchscreen tap %s" % tp_logout_confirm)

        time.sleep(10)
        self.navigateToHomeScreen()

    # copy file from c2d server
    def copy_files(self, workspace, package, version):
        print "Start Copying Content Files. Wait a moment...."

        # For file copy test
        if package == "test":
            cur_dir = os.path.join(os.getcwd(), "contents")
            self.push(cur_dir, "/sdcard/")
            return

        # Download from c2d
        print "Downloading from c2d..."
        path = workspace.download_c2d(package, version = version, pc = "testcontent")
        dst = workspace.unpack_c2d(path, "./packages")
        print "Downloading package path = %s" % dst

        print "Copying contents..."
        cur_dir = os.path.join(dst, "contents")
        print "Content file path = %s" % cur_dir
        self.push(cur_dir, "/sdcard/")
        print "Copying completed!"

    def install_files(self, workspace, package, version):
        print "Start Application Install. Wait a moment...."

        # Download from c2d
        print "Downloading from c2d..."
        path = workspace.download_c2d(package, version = version, pc = "testcontent")
        dst = workspace.unpack_c2d(path, "./packages")
        print "Downloading package path = %s" % dst

        files = os.listdir(os.path.join(dst, "apps"))

        print "Installing packages..."
        for f in files:
            fullpath = os.path.join(dst, "apps", f)
            print "  Install package %s" % fullpath
            try:
                self.install(fullpath, timeout=120, args="-r -d -g")
                time.sleep(2)
            except Exception as e:
                print e

        print "Installing completed!"

    def reboot_with_waiting(self, pre_wait, post_wait):
        print "Start rebooting. Wait a moment...."
        if pre_wait > 0:
            print "Waiting %d sec before rebooting." % pre_wait
            time.sleep(pre_wait)

        self.reboot()
        self.wait_power_state('boot_completed', timeout = 15*60)

        if post_wait > 0:
            print "Waiting %d sec after rebooting." % post_wait
            time.sleep(post_wait)

        self.root()
        self.remount()

        print "Finish rebooting."

    def change_thermal_mitigation(self, conf_path):
        print "Start changing thermal mitigation config file. Wait a moment...."
        self.root()
        self.remount()

        # backup original thermal conf.
        if not self.path_exists(self.thermalconf_back_path):
            self.mv(self.thermalconf_path, self.thermalconf_back_path)

        self.push(conf_path, self.thermalconf_path)

        print "Finish changing thermal mitigation config."

    # TODO Imprement
    def restore_thermal_mitigation(self):
        print "Start restore thermal mitigation config."

    def disable_permissions(self, list_file):
        print "Start disabling permission. Wait a moment...."

        with open(list_file, mode = 'r') as f:
            for l in f:
                kv = l.split(":")
                print "%s : %s" % (kv[0].strip(), kv[1].strip())

                try:
                    self.grant_permissions(kv[0].strip(), kv[1].strip())
                except Exception as e:
                    print e

        print "End disbaling permission."

    def grant_permission(self, package, permission):
        print "%s : %s" % (package, permission)

        try:
            self.handset.grant_permissions(package, permission)
        except Exception as e:
            print e

    def get_package_version_name(self, package):
        result = self.shell("dumpsys package %s | grep versionName" % package)
        result = result.split('=')

        version_name = ""

        try:
            version_name = result[1]
        except Exception, e:
            print e

        return version_name

    def get_package_version_code(self, package):
        result = self.shell("dumpsys package %s | grep versionCode" % package)
        result = result.split('=')

        version_code = ""

        try:
            version_code = result[1].split(' ')[0]
        except Exception, e:
            print e

        return version_code

    def get_imei(self):
        imei = ""

        result = self.shell("dumpsys iphonesubinfo")
        match = re.search("Device ID = (.*)", result)
        if match:
            imei = match.group(1)
        else:
            raise Exception("Failed to find IMEI information.")

        return imei

    def get_cdf_id(self):
        try:
            swversion = self.get_property("ro.semc.version.cust")
        except Exception:
            swversion = "N/A"
            # Only log and no error
            print("No software CDF version found")  # @UndefinedVariable
        return swversion

    def get_cdf_rev(self):
        try:
            swrevision = self.get_property("ro.semc.version.cust_revision")
        except Exception:
            swrevision = "N/A"
            # Only log and no error
            print("No software CDF revision found")  # @UndefinedVariable
        return swrevision

    def _disbale_usb_always_ask(self):
        file_name = "/data/data/com.sonyericsson.usbux/shared_prefs/com.sonyericsson.usbux_preferences.xml"
        usb_pref = self.shell("cat %s" % file_name)
        # Change "ask_enabled" to false
        if 'ask_enabled' in usb_pref:
            usb_pref = re.sub(r"(ask_enabled.*value.*)true", r"\1false", usb_pref)
        else:
            usb_pref = re.sub(r"(<map>)", r'\1 <boolean name="ask_enabled" value="false" />', usb_pref)

        # Must fix double quotas in order to do echo later
        usb_pref = re.sub(r"\"", r"\"", usb_pref)
        # Write back new content to file
        self.shell("echo \"%s\" > %s" % (usb_pref, file_name))
