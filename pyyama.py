#!/usr/bin/python3
import sys
import socket
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QCoreApplication, QSettings, QTimer
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QMessageBox
from pyyamamainwindow import Ui_PyYamaMainWindow
from yamaha import Yamaha, YamahaError
import json

ORGANIZATION_DOMAIN = 'kuuks.iki.fi'
APPLICATION_NAME = 'PyYama'


class PyYamaMainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super(PyYamaMainWindow, self).__init__()
        self.ui = Ui_PyYamaMainWindow()
        self.ui.setupUi(self)
        settings = QSettings()
        host = settings.value('hostname', type=str)
        autoconnect = settings.value('autoconnect', False, type=bool)
        self.listener_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.listener_sock.bind(('', 0))
        self.listener_sock.setblocking(0)
        for attempt in range(10):
            try:
                if autoconnect and host != '':
                    self.yamaha = Yamaha(host)
                else:
                    text, ok_pressed = QInputDialog.getText(self, "PyYama Connect", "Hostname of Yamaha device:",
                                                            QLineEdit.Normal, host)
                    if ok_pressed:
                        host = text
                    else:
                        exit(1)
                self.yamaha = Yamaha(host)
            except YamahaError as error:
                QMessageBox.critical(self, "PyYama error", str(error))
                autoconnect = False
            else:
                break
        else:
            exit(1)
        settings.setValue('hostname', host)
        self.make_zone_list()
        self.zone=self.ui.zoneComboBox.currentText()
        self.yamaha.set_listener_port(self.listener_sock.getsockname()[1])
        self.ui.muteCheckBox.stateChanged.connect(self.muteChange)
        self.ui.actionExit.triggered.connect(self.exit)
        self.ui.pauseToolButton.clicked.connect(self.pause)
        self.ui.modelNameLabel.setText(self.yamaha.model_name)
        self.ui.zoneComboBox.currentIndexChanged.connect(self.change_zone)
        self.ui.inputComboBox.currentIndexChanged.connect(self.change_input)
        self.make_input_list()
        self.update_nowplaying()
        self.udptimer = QTimer()
        self.udptimer.setSingleShot(False)
        self.udptimer.setInterval(100)
        self.udptimer.timeout.connect(self.listen_UDP)
        self.udptimer.start()

    def connect(self):
        self.yamaha = Yamaha(self.host)

    def exit(self):
        QCoreApplication.exit()

    def make_zone_list(self):
        self.ui.zoneComboBox.blockSignals(True)
        self.ui.zoneComboBox.clear()
        for zone in self.yamaha.zones:
            self.ui.zoneComboBox.addItem(zone)
        self.ui.inputComboBox.setCurrentIndex(0)
        self.ui.zoneComboBox.blockSignals(False)

    def change_zone(self):
        self.zone=self.ui.zoneComboBox.currentText()
        self.make_input_list()

    def make_input_list(self):
        self.ui.inputComboBox.blockSignals(True)
        self.ui.inputComboBox.clear()
        current_input=self.yamaha.get_current_input(self.zone)
        index=0
        current_index=0
        for input in self.yamaha.get_input_list(self.zone):
            self.ui.inputComboBox.addItem(input)
            if input == current_input:
                current_index=index
            index += 1
        self.ui.inputComboBox.setCurrentIndex(current_index)
        self.ui.inputComboBox.blockSignals(False)

    def change_input(self):
        self.yamaha.change_input(self.zone, self.ui.inputComboBox.currentText())

    def muteChange(self, state):
        if state == Qt.Checked:
            self.yamaha.mute(self.zone)
        else:
            self.yamaha.unmute(self.zone)

    def pause(self):
        self.yamaha.pause(self.zone)


    def update_nowplaying(self):
        response = self.yamaha.get_nowplaying()
        try:
            if response['playback'] == 'pause':
                self.ui.nowplayingGroupBox.setTitle('Now playing (paused)')
            else:
                self.ui.nowplayingGroupBox.setTitle('Now playing')
            self.ui.artistLabel.setText(response['artist'])
            self.ui.albumLabel.setText(response['album'])
            self.ui.trackLabel.setText(response['track'])
        except KeyError:
            pass

    def listen_UDP(self):
        try:
            data, address = self.listener_sock.recvfrom(10000)
        except BlockingIOError:
            pass
        else:
            if len(data) > 0:
                msg=json.loads(data.decode("utf-8"))
                if msg['device_id'] == self.yamaha.device_id:
                    self.ui.plainTextEdit.appendPlainText(data.decode("utf-8"))
                if self.zone in msg:
                    if 'signal_info_updated' in msg[self.zone] and msg[self.zone]['signal_info_updated']=='true':
                        #TODO
                        pass
                    if 'input' in msg[self.zone] and msg[self.zone]['input'] != self.ui.inputComboBox.currentText():
                    #TODO: make this NOT depend on the actual text. Maybe store the current (assumed) input source name elsewhere?
                        self.make_input_list()
                if 'netusb' in msg and 'play_info_updated' in msg['netusb']: #TODO: only for netusb?
                    self.update_nowplaying()

if __name__ == '__main__':
    QCoreApplication.setOrganizationDomain(ORGANIZATION_DOMAIN)
    QCoreApplication.setApplicationName(APPLICATION_NAME)
    app = QtWidgets.QApplication(sys.argv)
    w = PyYamaMainWindow()
    w.show()
    sys.exit(app.exec_())
