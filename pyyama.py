#!/usr/bin/python3
import sys
import socket
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QCoreApplication, QSettings, QTimer
from PyQt5.QtWidgets import QInputDialog, QLineEdit, QMessageBox
from pyyamamainwindow import Ui_PyYamaMainWindow
from yamaha import Yamaha, YamahaError

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
        self.yamaha.set_listener_port(self.listener_sock.getsockname()[1])
        self.ui.muteCheckBox.stateChanged.connect(self.muteChange)
        self.ui.actionExit.triggered.connect(self.exit)
        self.ui.pauseToolButton.clicked.connect(self.pause)
        self.ui.modelNameLabel.setText(self.yamaha.get_model_name())
        self.udptimer = QTimer()
        self.udptimer.setSingleShot(False)
        self.udptimer.setInterval(100)
        self.udptimer.timeout.connect(self.listen_UDP)
        self.udptimer.start()

    def connect(self):
        self.yamaha = Yamaha(self.host)

    def exit(self):
        QCoreApplication.exit()

    def muteChange(self, state):
        if state == Qt.Checked:
            self.yamaha.mute()
        else:
            self.yamaha.unmute()

    def pause(self):
        self.yamaha.pause()

    def listen_UDP(self):
        try:
            data, address = self.listener_sock.recvfrom(10000)
        except BlockingIOError:
            pass
        else:
            if len(data) > 0:
                self.ui.plainTextEdit.appendPlainText(str(data))
                print(str(data))

if __name__ == '__main__':
    QCoreApplication.setOrganizationDomain(ORGANIZATION_DOMAIN)
    QCoreApplication.setApplicationName(APPLICATION_NAME)
    app = QtWidgets.QApplication(sys.argv)
    w = PyYamaMainWindow()
    w.show()
    sys.exit(app.exec_())
