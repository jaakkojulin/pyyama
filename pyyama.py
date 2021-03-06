#!/usr/bin/python3
"""
    PyYama
    Copyright (C) 2018 Jaakko Julin

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2 of the License, or
    (at your option) any later version.

    See file "LICENSE" for details.
"""

__version__ = '0.1.6'
__author__ = 'Jaakko Julin'

import sys
import socket
import signal
import json
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QCoreApplication, QSettings, QTimer
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QMessageBox
from ui_mainwindow import Ui_PyYamaMainWindow
from connectdialog import ConnectDialog
from preferencesdialog import PreferencesDialog
from yama import Yama, YamaError

ORGANIZATION_DOMAIN = 'kuuks.iki.fi'
APPLICATION_NAME = 'PyYama'


class PyYamaMainWindow(QtWidgets.QMainWindow):
    def __init__(self, host=''):
        """

        :type host: str
        """
        super(PyYamaMainWindow, self).__init__()
        self.ui = Ui_PyYamaMainWindow()
        self.ui.setupUi(self)
        #self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.settings = QSettings()
        self.connected = False
        if host == '':
            self.autoconnect = self.settings.value('autoconnect', False, type=bool)
            if self.autoconnect:
                self.host = self.settings.value('autoconnect_host', '', type=str)
            else:
                self.host = self.settings.value('last_good_host', '', type=str)
        else:
            self.host = host
            self.autoconnect = True
        self.udp_port = self.settings.value('udp_port', 0, type=int)

        self.ui.actionExit.triggered.connect(self.exit)
        self.ui.actionPreferences.triggered.connect(self.open_preferences_dialog)
        self.ui.playPauseToolButton.clicked.connect(self.pause)
        self.ui.stopToolButton.clicked.connect(self.stop)
        self.ui.nextToolButton.clicked.connect(self.next)
        self.ui.previousToolButton.clicked.connect(self.previous)
        self.ui.muteToolButton.clicked.connect(self.mute_toggle)
        self.ui.zoneComboBox.currentIndexChanged.connect(self.change_zone)
        self.ui.inputComboBox.currentIndexChanged.connect(self.change_input)
        self.ui.volumeSpinBox.valueChanged.connect(self.set_volume)
        self.ui.actionAbout_PyYama.triggered.connect(self.about)
        self.ui.actionConnect.triggered.connect(self.connect)
        self.ui.action_Disconnect.triggered.connect(self.connection_disconnect)
        self.ui.powerToolButton.clicked.connect(self.power)


        self.greetingstage = 0
        self.greetingtimer = QTimer()
        self.greetingtimer.setSingleShot(True)
        self.greetingtimer.timeout.connect(self.greeting)
        self.greetingtimer.start(2000)

        self.refreshtimer = QTimer()
        self.refreshtimer.timeout.connect(self.refresh)

        self.disable_buttons()
        if self.autoconnect:
            self.connect(autoconnect=True)
        else:
            self.connect()

    def connect(self, autoconnect=False):
        host=self.host
        try:
            self.listener_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.listener_sock.bind(('', self.udp_port))
            self.listener_sock.setblocking(0)
        except OSError as error:
            QMessageBox.critical(self, "PyYama error", "Error in setting up UDP listener: " + str(error))
            return
        for attempt in range(10):
            try:
                if not autoconnect or self.host == '':
                    host=self.open_connect_dialog(host=self.host)
                    if host == '':
                        return
                self.yama = Yama(host)
            except YamaError as error:
                QMessageBox.critical(self, "PyYama error", str(error))
                autoconnect = False
            else:
                break
        else:
            return

        self.connected = True
        self.ui.actionConnect.setEnabled(False)
        self.ui.action_Disconnect.setEnabled(True)
        self.host=host
        self.settings.setValue('last_good_host', self.host)
        self.make_zone_list()
        self.zone = self.ui.zoneComboBox.currentText()
        self.yama.set_listener_port(self.listener_sock.getsockname()[1])

        try:
            self.update_status()
        except YamaError:
            print("Got an error right after connecting, something is weird.")
            self.disconnect()

        self.make_input_list()
        self.refresh(update_status=False)

        self.make_input_list()
        self.update_nowplaying()

        self.udptimer = QTimer()
        self.udptimer.setSingleShot(True)
        self.udpinterval = 100
        self.udptimer.setInterval(self.udpinterval)
        self.udptimer.timeout.connect(self.listen_UDP)
        self.udptimer.start()

        self.ui.modelNameLabel.setText(self.yama.model_name)

    def connection_disconnect(self):
        self.connected = False
        self.ui.actionConnect.setEnabled(True)
        self.ui.action_Disconnect.setEnabled(False)
        self.disable_buttons()

    def exit(self):
        QCoreApplication.exit()


    def open_connect_dialog(self, host=''):
        dialog = ConnectDialog(host)
        if dialog.exec_() == ConnectDialog.Accepted:
            return dialog.hostname
        else:
            return ''

    def open_preferences_dialog(self):
        dialog = PreferencesDialog()
        dialog.exec_()


    def greeting(self):
        msg = ('PyYama ' + __version__, 'Copyright (C) 2018 Jaakko Julin', 'This is free software.', 'See Help|About for details.', 'ABSOLUTELY NO WARRANTY')
        self.ui.statusbar.showMessage(msg[self.greetingstage], 2000)
        self.greetingstage += 1
        if self.greetingstage < len(msg):
            self.greetingtimer.start(2500)

    def about(self):
        QMessageBox.about(self, "PyYama",

                          "Python and PyQt5 based software that can control some multi-room audio devices\n\n"
                          "PyYama " +__version__ + "\nCopyright (C) 2018 " + __author__ + "\n\n"
                          "PyYama comes with ABSOLUTELY NO WARRANTY.\n\n"
                          "This program is free software; you can redistribute it and/or modify "
                          "it under the terms of the GNU General Public License as published by "
                          "the Free Software Foundation; either version 2 of the License, or "
                          "(at your option) any later version. "
                          "\n\n"
                          "This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.\n\n"

                          "You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.\n\n"
                          "This program is not supported, endorsed or authorized by any manufacturers of said audio equipment.\n\n"
                          "Some icons are from the Open Iconic collection of icons. Copyright (C) 2014 Waybury, licensed under The MIT License. See file LICENSE in icon directories.\n"
                          )

    def disable_buttons(self):
        self.ui.tabWidget.widget(0).setEnabled(False)

    def refresh(self, update_status=True):
        if not self.connected:
            if self.refreshtimer.isActive():
                self.refreshtimer.stop()
            return
        if update_status:
            try:
                self.update_status() # This can generate YamaErrors (if we have connection issues etc)
            except YamaError as error:
                self.ui.statusbar.showMessage(str(error))
                self.disable_buttons()
                self.refreshtimer.stop()
                self.refreshtimer.setSingleShot(True)
                self.refreshtimer.start(5000) # In case of errors, try again. Note this is delay, not interval.
                return
        self.update_input()
        self.update_volume()
        self.update_mute()
        self.update_power()
        self.ui.statusbar.showMessage("")
        if not self.ui.tabWidget.widget(0).isEnabled():
            self.ui.tabWidget.widget(0).setEnabled(True)
        self.refreshtimer.setSingleShot(False)
        self.refreshtimer.setInterval(60000) # Normal refresh every 60 seconds
        if not self.refreshtimer.isActive():
            self.refreshtimer.start()


    def update_status(self):
        self.yama.update_status(self.zone)

    def update_volume(self):
        volume = self.yama.get_volume(self.zone)
        maxvolume = self.yama.get_volume_max(self.zone)
        volume_dB = (volume - maxvolume) * 0.5
        # print("Volume as reported by device is " + str(volume) + " and in dB this probably is " + str(volume_dB))
        if volume_dB != self.ui.volumeSpinBox.value():
            self.ui.volumeSpinBox.blockSignals(True)
            self.ui.volumeSpinBox.setValue(volume_dB)
            self.ui.volumeSpinBox.blockSignals(False)
        self.ui.volumeSpinBox.setEnabled(True)

    def update_mute(self):
        self.ui.muteToolButton.blockSignals(True)
        muted = self.yama.get_mute(self.zone)
        if muted:
            self.ui.muteToolButton.setIcon(QtGui.QIcon(":/icons/icons32/volume-high-4x.png"))
        else:
            self.ui.muteToolButton.setIcon(QtGui.QIcon(":/icons/icons32/volume-off-4x.png"))
        self.ui.muteToolButton.blockSignals(False)

    def update_power(self):
        power = self.yama.get_power(self.zone)
        if power:
            self.ui.powerToolButton.setStyleSheet("background-color: rgb(232, 179, 213)")
            self.ui.previousToolButton.setEnabled(True)
            self.ui.nextToolButton.setEnabled(True)
            self.ui.playPauseToolButton.setEnabled(True)
            self.ui.muteToolButton.setEnabled(True)
            self.ui.zoneComboBox.setEnabled(True)
            self.ui.inputComboBox.setEnabled(True)
            self.ui.volumeSpinBox.setEnabled(True)
        else:
            self.ui.powerToolButton.setStyleSheet("background-color: rgb(122, 213, 179)")
            self.ui.previousToolButton.setEnabled(False)
            self.ui.nextToolButton.setEnabled(False)
            self.ui.playPauseToolButton.setEnabled(False)
            self.ui.muteToolButton.setEnabled(False)
            self.ui.zoneComboBox.setEnabled(False)
            self.ui.inputComboBox.setEnabled(False)
            self.ui.volumeSpinBox.setEnabled(False)

    def update_input(self):
        input_source = self.yama.get_input(self.zone)
        if input_source != self.ui.inputComboBox.currentText():
            self.make_input_list()

    def make_zone_list(self):
        self.ui.zoneComboBox.blockSignals(True)
        self.ui.zoneComboBox.clear()
        defaultzone=self.settings.value("default_zone", 'main', type=str)
        for zone in self.yama.zones:
            self.ui.zoneComboBox.addItem(zone)
        if defaultzone != '':
            try:
                self.ui.zoneComboBox.setCurrentIndex(self.yama.zones.index(defaultzone))
            except ValueError:
                print("No such zone: " + defaultzone)
                self.ui.zoneComboBox.setCurrentIndex(0)
        else:
            self.ui.zoneComboBox.setCurrentIndex(0)
        self.ui.zoneComboBox.blockSignals(False)

    def change_zone(self):
        self.zone = self.ui.zoneComboBox.currentText()
        self.make_input_list()
        self.refresh()

    def make_input_list(self):  # Call update_status() first
        self.ui.inputComboBox.blockSignals(True)
        self.ui.inputComboBox.clear()
        current_input = self.yama.get_input(self.zone)
        inputs = self.yama.get_input_list(self.zone)
        for input in inputs:
            self.ui.inputComboBox.addItem(input)
        try:
            self.ui.inputComboBox.setCurrentIndex(inputs.index(current_input))
        except ValueError:
            self.ui.inputComboBox.setCurrentIndex(0)
        self.ui.inputComboBox.blockSignals(False)

    def change_input(self):
        self.yama.change_input(self.zone, self.ui.inputComboBox.currentText())

    def mute_toggle(self):
        if not self.yama.get_mute(self.zone):
            self.simple_error_wrapper(self.yama.mute, self.zone)
        else:
            self.simple_error_wrapper(self.yama.unmute, self.zone)

    def pause(self):
        self.simple_error_wrapper(self.yama.pause)

    def simple_error_wrapper(self, meth: staticmethod, *args):
        try:
            return meth(*args)
        except YamaError as error:
            self.ui.statusbar.showMessage(str(error))
            self.disable_buttons()
            self.refresh()

    def play(self):
        self.simple_error_wrapper(self.yama.play)

    def stop(self):
        self.simple_error_wrapper(self.yama.stop)

    def previous(self):
        self.simple_error_wrapper(self.yama.previous)

    def next(self):
        self.simple_error_wrapper(self.yama.next)

    def set_volume(self):
        self.simple_error_wrapper(self.yama.set_volume_dB, self.zone, self.ui.volumeSpinBox.value())
        self.ui.volumeSpinBox.setEnabled(False)

    def power(self):
        if self.yama.get_power(self.zone):
            self.simple_error_wrapper(self.yama.standby, self.zone)
        else:
            self.simple_error_wrapper(self.yama.power_on, self.zone)

    def update_nowplaying(self):
        response = self.simple_error_wrapper(self.yama.get_nowplaying)
        try:
            if response['playback'] == 'pause':
                self.ui.nowplayingGroupBox.setTitle('Now playing (paused)')
                self.ui.playPauseToolButton.setIcon(QtGui.QIcon(":/icons/icons32/media-play-4x.png"))
                self.ui.playPauseToolButton.disconnect()
                self.ui.playPauseToolButton.clicked.connect(self.play)
                self.ui.playPauseToolButton.setEnabled(True)
                self.ui.stopToolButton.setEnabled(True)
            elif response['playback'] == 'stop':
                self.ui.nowplayingGroupBox.setTitle('Now playing (stopped)')
                self.ui.playPauseToolButton.setIcon(QtGui.QIcon(":/icons/icons32/media-play-4x.png"))
                self.ui.playPauseToolButton.disconnect()
                self.ui.playPauseToolButton.clicked.connect(self.play)
                self.ui.playPauseToolButton.setEnabled(True)
                self.ui.stopToolButton.setEnabled(False)
            else:
                self.ui.nowplayingGroupBox.setTitle('Now playing')
                self.ui.playPauseToolButton.setIcon(QtGui.QIcon(":/icons/icons32/media-pause-4x.png"))
                self.ui.playPauseToolButton.disconnect()
                self.ui.playPauseToolButton.clicked.connect(self.pause)
                self.ui.playPauseToolButton.setEnabled(True)
                self.ui.stopToolButton.setEnabled(True)
            self.ui.artistLabel.setText(response['artist'])
            self.ui.albumLabel.setText(response['album'])
            self.ui.trackLabel.setText(response['track'])
        except KeyError:
            pass

    def listen_UDP(self):
        if not self.connected:
            return
        try:
            data, address = self.listener_sock.recvfrom(10000)
        except BlockingIOError:
            self.udpinterval *= 2
            if self.udpinterval > 100:
                self.udpinterval = 100
            self.udptimer.start(self.udpinterval)
            pass
        else:
            if data:
                msg = json.loads(data.decode("utf-8"))
                if msg['device_id'] == self.yama.device_id:
                    self.ui.plainTextEdit.appendPlainText(str(address[0]) + ':' + str(address[1])  + "  " + data.decode("utf-8") + '\n')
                if self.zone in msg:
                    zone=self.zone
                    zonemsg=msg[zone]
                    if 'signal_info_updated' in zonemsg and zonemsg['signal_info_updated'] == 'true':
                        # TODO
                        pass
                    if 'power' in msg[self.zone]:
                        self.yama.update_power(zone, (zonemsg['power']=='on'))
                        self.update_power()
                    if 'volume' in msg[self.zone]:
                        self.yama.update_volume(zone, int(zonemsg['volume']))
                        self.update_volume()
                    if 'mute' in msg[self.zone]:
                        self.yama.update_mute(zone, bool(zonemsg['mute']))
                        self.update_mute()
                    if 'input' in msg[self.zone]:
                        self.yama.update_input(zone, zonemsg['input'])
                        self.update_input()
                if 'netusb' in msg and 'play_info_updated' in msg['netusb']:  # TODO: only for netusb?
                    self.update_nowplaying()
            self.udpinterval = 1
            self.udptimer.start(0)


def _keyboardinterrupt_handler(signum, frame):
    QCoreApplication.exit()

if __name__ == '__main__':
    QCoreApplication.setOrganizationDomain(ORGANIZATION_DOMAIN)
    QCoreApplication.setApplicationName(APPLICATION_NAME)
    app = QtWidgets.QApplication(sys.argv)
    host = ''
    if len(sys.argv) > 1:
        host = sys.argv[1]
    w = PyYamaMainWindow(host)
    signal.signal(signal.SIGINT, _keyboardinterrupt_handler)
    w.show()
    sys.exit(app.exec_())
