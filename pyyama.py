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

__version__ = '0.1.5'
__author__ = 'Jaakko Julin'

import sys
import socket
import signal
import json
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QCoreApplication, QSettings, QTimer
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QMessageBox
from pyyamamainwindow import Ui_PyYamaMainWindow
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
        settings = QSettings()
        if host == '':
            host = settings.value('hostname', type=str)
            autoconnect = settings.value('autoconnect', False, type=bool)
        else:
            autoconnect = True
        udp_port = settings.value('udp_port', 0, type=int)
        try:
            self.listener_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.listener_sock.bind(('', udp_port))
            self.listener_sock.setblocking(0)
        except OSError as error:
            QMessageBox.critical(self, "PyYama error",
                                 "Error in setting up UDP listener: " + str(error))
            exit(1)
        for attempt in range(10):
            try:
                if not autoconnect or host == '':
                    host=self.ask_for_hostname(host)
                    if host == '':
                        exit(1);
                self.yama = Yama(host)
            except YamaError as error:
                QMessageBox.critical(self, "PyYama error", str(error))
                autoconnect = False
            else:
                break
        else:
            exit(1)
        settings.setValue('hostname', host)
        self.make_zone_list()
        self.zone = self.ui.zoneComboBox.currentText()
        self.yama.set_listener_port(self.listener_sock.getsockname()[1])

        self.ui.actionExit.triggered.connect(self.exit)
        self.ui.playPauseToolButton.clicked.connect(self.pause)
        self.ui.stopToolButton.clicked.connect(self.stop)
        self.ui.nextToolButton.clicked.connect(self.next)
        self.ui.previousToolButton.clicked.connect(self.previous)
        self.ui.muteToolButton.clicked.connect(self.mute_toggle)
        self.ui.modelNameLabel.setText(self.yama.model_name)
        self.ui.zoneComboBox.currentIndexChanged.connect(self.change_zone)
        self.ui.inputComboBox.currentIndexChanged.connect(self.change_input)
        self.ui.volumeSpinBox.valueChanged.connect(self.set_volume)
        self.ui.actionAbout_PyYama.triggered.connect(self.about)
        self.ui.powerToolButton.clicked.connect(self.power)
        self.greetingstage = 0
        self.greetingtimer = QTimer()
        self.greetingtimer.setSingleShot(True)
        self.greetingtimer.timeout.connect(self.greeting)
        self.greetingtimer.start(2000)

        self.refreshtimer = QTimer()
        self.refreshtimer.timeout.connect(self.refresh)
        self.status = {}
        self.refresh()

        self.make_input_list()
        self.update_nowplaying()

        self.udptimer = QTimer()
        self.udptimer.setSingleShot(True)
        self.udpinterval = 100
        self.udptimer.setInterval(self.udpinterval)
        self.udptimer.timeout.connect(self.listen_UDP)
        self.udptimer.start()


    def exit(self):
        QCoreApplication.exit()

    def ask_for_hostname(self, host='') -> str:
        host, ok_pressed = QInputDialog.getText(self, "PyYama Connect", "Hostname of device:", QLineEdit.Normal, host)
        if ok_pressed:
            return host
        else:
            return ''

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

    def refresh(self):
        print("Refresh called!")
        try:
            self.update_status() # This can generate YamaErrors (if we have connection issues etc)
        except YamaError as error:
            self.ui.statusbar.showMessage(str(error))
            self.ui.tabWidget.widget(0).setEnabled(False)
            self.refreshtimer.stop()
            self.refreshtimer.setSingleShot(True)
            self.refreshtimer.start(5000) # In case of errors, try again. Note this is delay, not interval.
            return
        self.update_input(provide=False)
        self.update_volume(provide=False)
        self.update_mute(provide=False)
        self.update_power(provide=False)
        self.ui.statusbar.showMessage("")
        if not self.ui.tabWidget.widget(0).isEnabled():
            self.ui.tabWidget.widget(0).setEnabled(True)
        self.refreshtimer.setSingleShot(False)
        self.refreshtimer.setInterval(60000) # Normal refresh every 60 seconds
        if not self.refreshtimer.isActive():
            self.refreshtimer.start()


    def update_status(self):
        print("Update status called!")
        self.status = self.yama.get_status(self.zone)

    def update_volume(self, provide=False, volume=0):  # If you provide a volume, set provide to True.
        if provide:
            self.status['volume'] = volume
        else:
            volume = self.status['volume']
        maxvolume = self.yama.get_volume_max(self.zone)
        volume_dB = (volume - maxvolume) * 0.5
        # print("Volume as reported by device is " + str(volume) + " and in dB this probably is " + str(volume_dB))
        if volume_dB != self.ui.volumeSpinBox.value():
            self.ui.volumeSpinBox.blockSignals(True)
            self.ui.volumeSpinBox.setValue(volume_dB)
            self.ui.volumeSpinBox.blockSignals(False)
        self.ui.volumeSpinBox.setEnabled(True)

    def update_mute(self, provide=False, muted=False):
        self.ui.muteToolButton.blockSignals(True)
        if provide:
            self.status['mute'] = muted
        else:
            muted = self.status['mute']
        if muted:
            self.ui.muteToolButton.setIcon(QtGui.QIcon(":/icons/icons32/volume-high-4x.png"))
        else:
            self.ui.muteToolButton.setIcon(QtGui.QIcon(":/icons/icons32/volume-off-4x.png"))
        self.ui.muteToolButton.blockSignals(False)

    def update_power(self, provide=False, power=False):
        if provide:
            self.status['power'] = power
        else:
            power = self.status['power']
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

    def update_input(self, provide=False, input_source=''):
        if provide:
            self.status['input'] = input_source
        else:
            input_source = self.status['input']
        if input_source != self.ui.inputComboBox.currentText():
            self.make_input_list()

    def make_zone_list(self):
        self.ui.zoneComboBox.blockSignals(True)
        self.ui.zoneComboBox.clear()
        for zone in self.yama.zones:
            self.ui.zoneComboBox.addItem(zone)
        self.ui.inputComboBox.setCurrentIndex(0)
        self.ui.zoneComboBox.blockSignals(False)

    def change_zone(self):
        self.zone = self.ui.zoneComboBox.currentText()
        self.make_input_list()
        self.refresh()

    def make_input_list(self):  # Call update_status() first
        self.ui.inputComboBox.blockSignals(True)
        self.ui.inputComboBox.clear()
        current_input = self.status['input']
        index = 0
        current_index = 0
        for input in self.yama.get_input_list(self.zone):
            self.ui.inputComboBox.addItem(input)
            if input == current_input:
                current_index = index
            index += 1
        self.ui.inputComboBox.setCurrentIndex(current_index)
        self.ui.inputComboBox.blockSignals(False)

    def change_input(self):
        self.yama.change_input(self.zone, self.ui.inputComboBox.currentText())

    def mute_toggle(self):
        if not self.status['mute']:
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
            self.ui.tabWidget.widget(0).setEnabled(False)
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
        if self.status['power']:
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
                    if 'signal_info_updated' in msg[self.zone] and msg[self.zone]['signal_info_updated'] == 'true':
                        # TODO
                        pass
                    if 'power' in msg[self.zone]:
                        self.update_power(provide=True, power=(msg[self.zone]['power'] == 'on'))
                    if 'volume' in msg[self.zone]:
                        self.update_volume(provide=True, volume=int(msg[self.zone]['volume']))
                    if 'mute' in msg[self.zone]:
                        self.update_mute(provide=True, muted=bool(msg[self.zone]['mute']))
                    if 'input' in msg[self.zone]:
                        self.update_input(provide=True, input_source=msg[self.zone]['input'])
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
