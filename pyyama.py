#!/usr/bin/python3
import sys
import socket
import json
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QCoreApplication, QSettings, QTimer
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QMessageBox
from pyyamamainwindow import Ui_PyYamaMainWindow
from yama import Yama, YamaError

ORGANIZATION_DOMAIN = 'kuuks.iki.fi'
APPLICATION_NAME = 'PyYama'

VERSION = "0.1.0"

class PyYamaMainWindow(QtWidgets.QMainWindow):
    def __init__(self, host=''):
        super(PyYamaMainWindow, self).__init__()
        self.ui = Ui_PyYamaMainWindow()
        self.ui.setupUi(self)
        self.setWindowIcon(QtGui.QIcon('pyyama.png'))
        settings = QSettings()
        if host == '':
            host = settings.value('hostname', type=str)
            autoconnect = settings.value('autoconnect', False, type=bool)
        else:
            autoconnect = True
        self.listener_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listener_sock.bind(('', 0))
        self.listener_sock.setblocking(0)
        for attempt in range(10):
            try:
                if autoconnect and host != '':
                    self.yama = Yama(host)
                else:
                    text, ok_pressed = QInputDialog.getText(self, "PyYama Connect", "Hostname of device:",
                                                            QLineEdit.Normal, host)
                    if ok_pressed:
                        host = text
                    else:
                        exit(1)
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
        self.zone=self.ui.zoneComboBox.currentText()
        self.yama.set_listener_port(self.listener_sock.getsockname()[1])
        self.ui.actionExit.triggered.connect(self.exit)
        self.ui.pauseToolButton.clicked.connect(self.pause)
        self.ui.nextToolButton.clicked.connect(self.next)
        self.ui.previousToolButton.clicked.connect(self.previous)
        self.ui.muteToolButton.clicked.connect(self.muteToggle)
        self.ui.modelNameLabel.setText(self.yama.model_name)
        self.ui.zoneComboBox.currentIndexChanged.connect(self.change_zone)
        self.ui.inputComboBox.currentIndexChanged.connect(self.change_input)
        self.ui.volumeSpinBox.valueChanged.connect(self.set_volume)
        self.ui.actionAbout_PyYama.triggered.connect(self.about)

        self.status={}
        self.refresh()

        self.make_input_list()
        self.update_nowplaying()
        self.udptimer = QTimer()
        self.udptimer.setSingleShot(True)
        self.udpinterval=100
        self.udptimer.setInterval(self.udpinterval)
        self.udptimer.timeout.connect(self.listen_UDP)
        self.udptimer.start()



    def connect(self):
        self.yama = Yama(self.host)

    def exit(self):
        QCoreApplication.exit()

    def about(self):
        QMessageBox.about(self, "PyYama", "PyYama " + VERSION + "\n\nby Jaakko Julin\n\nPyYama is a Python and PyQt5 based software that can control some devices manufactured by a certain Japanese corporation. This program is not supported, endorsed or authorized by that or any other corporation. No warranty.")
        

    def refresh(self):
        self.update_status()
        self.update_volume(provide=False)
        self.update_mute(provide=False)

    def update_status(self):
        self.status=self.yama.get_status(self.zone)

    def update_volume(self, provide=False, volume=0): # If you provide a volume, set provide to True.
        # Else make sure internal state is ok or update_status() is called before us.
        self.ui.volumeSpinBox.blockSignals(True)
        if provide:
            self.status['volume']=volume
        else:
            volume=self.status['volume']
        maxvolume=self.yama.get_volume_max(self.zone)
        volume_dB=(volume-maxvolume)*0.5
        # print("Volume as reported by device is " + str(volume) + " and in dB this probably is " + str(volume_dB))
        if volume_dB != self.ui.volumeSpinBox.value():
            self.ui.volumeSpinBox.setValue(volume_dB)
        self.ui.volumeSpinBox.blockSignals(False)

    def update_mute(self, provide=False, muted=False):
        self.ui.muteToolButton.blockSignals(True)
        if provide:
            self.status['mute'] = muted
        else:
            muted=self.status['mute']
        if muted:
            self.ui.muteToolButton.setIcon(QtGui.QIcon.fromTheme("audio-volume-high"))
        else:
            self.ui.muteToolButton.setIcon(QtGui.QIcon.fromTheme("audio-volume-muted"))
        self.ui.muteToolButton.blockSignals(False)
    def make_zone_list(self):
        self.ui.zoneComboBox.blockSignals(True)
        self.ui.zoneComboBox.clear()
        for zone in self.yama.zones:
            self.ui.zoneComboBox.addItem(zone)
        self.ui.inputComboBox.setCurrentIndex(0)
        self.ui.zoneComboBox.blockSignals(False)

    def change_zone(self):
        self.zone=self.ui.zoneComboBox.currentText()
        self.make_input_list()

    def make_input_list(self):
        self.ui.inputComboBox.blockSignals(True)
        self.ui.inputComboBox.clear()
        current_input=self.yama.get_current_input(self.zone)
        index=0
        current_index=0
        for input in self.yama.get_input_list(self.zone):
            self.ui.inputComboBox.addItem(input)
            if input == current_input:
                current_index=index
            index += 1
        self.ui.inputComboBox.setCurrentIndex(current_index)
        self.ui.inputComboBox.blockSignals(False)

    def change_input(self):
        self.yama.change_input(self.zone, self.ui.inputComboBox.currentText())

    def muteToggle(self):
        if self.status['mute'] == False:
            self.yama.mute(self.zone)
        else:
            self.yama.unmute(self.zone)

    def pause(self):
        self.yama.pause()

    def previous(self):
        self.yama.previous()

    def next(self):
        self.yama.next()

    def set_volume(self):
        self.yama.set_volume_dB(self.zone, self.ui.volumeSpinBox.value())

    def update_nowplaying(self):
        response = self.yama.get_nowplaying()
        try:
            if response['playback'] == 'pause':
                self.ui.nowplayingGroupBox.setTitle('Now playing (paused)')
                self.ui.pauseToolButton.setIcon(QtGui.QIcon.fromTheme("media-playback-start"))
            else:
                self.ui.nowplayingGroupBox.setTitle('Now playing')
                self.ui.pauseToolButton.setIcon(QtGui.QIcon.fromTheme("media-playback-pause"))
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
            if(self.udpinterval > 100):
                self.udpinterval=100
            self.udptimer.start(self.udpinterval)
            pass
        else:
            if len(data) > 0:
                msg=json.loads(data.decode("utf-8"))
                if msg['device_id'] == self.yama.device_id:
                    self.ui.plainTextEdit.appendPlainText(data.decode("utf-8"))
                if self.zone in msg:
                    if 'signal_info_updated' in msg[self.zone] and msg[self.zone]['signal_info_updated']=='true':
                        #TODO
                        pass
                    if 'volume' in msg[self.zone]:
                        self.update_volume(provide=True, volume=int(msg[self.zone]['volume']))
                    if 'mute' in msg[self.zone]:
                        self.update_mute(provide=True, muted=bool(msg[self.zone]['mute']))
                    if 'input' in msg[self.zone] and msg[self.zone]['input'] != self.ui.inputComboBox.currentText():
                    #TODO: make this NOT depend on the actual text. Maybe store the current (assumed) input source name elsewhere?
                        self.make_input_list()
                        self.refresh()
                if 'netusb' in msg and 'play_info_updated' in msg['netusb']: #TODO: only for netusb?
                    self.update_nowplaying()
            self.udpinterval=1
            self.udptimer.start(0)

if __name__ == '__main__':
    QCoreApplication.setOrganizationDomain(ORGANIZATION_DOMAIN)
    QCoreApplication.setApplicationName(APPLICATION_NAME)
    app = QtWidgets.QApplication(sys.argv)
    if len(sys.argv) > 1:
        host=sys.argv[1]
    else:
        host=''
    w = PyYamaMainWindow(host)
    w.show()
    sys.exit(app.exec_())
