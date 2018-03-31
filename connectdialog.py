from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import Qt, QSettings, QTimer, pyqtSlot, QThread, pyqtSignal
from ui_connectdialog import Ui_ConnectDialog
from find_yama import find_yamas


class YamaFinder(QtCore.QThread):
    device_found = pyqtSignal(str, str, str, name='deviceFound')

    def __init__(self):
        super(YamaFinder, self).__init__()
        self.exiting = False

    def __del__(self):
        print("Thread received del")
        self.exiting = True
        self.wait()

    def run(self):
        for yama in find_yamas():
            if self.exiting:
                print("Aborting.'")
                break
            self.device_found.emit(yama['name'], yama['model'],yama['hostname'])


class  ConnectDialog(QtWidgets.QDialog):
    def __init__(self, host=''):
        """

        """
        super(ConnectDialog, self).__init__()
        self.ui = Ui_ConnectDialog()
        self.ui.setupUi(self)
        self.setWindowModality(Qt.ApplicationModal)
        self.hostname=''
        self.ui.tableWidget.itemSelectionChanged.connect(self.on_selection_change)
        self.show()
        self.count=0
        self.ui.hostnameLineEdit.setText(host)
        self.thread=YamaFinder()
        self.thread.finished.connect(self.refresh_finished)
        self.thread.device_found.connect(self.add_device)
        QTimer.singleShot(100, self.refresh)

    def __del__(self):
        self.thread.exiting=True

    def accept(self):
        self.hostname=self.ui.hostnameLineEdit.text()
        return super(ConnectDialog, self).accept()

    @property
    def hostname(self):
        return self._hostname

    @hostname.setter
    def hostname(self, host):
        self._hostname = host


    @pyqtSlot()
    def on_selection_change(self):
        for index in self.ui.tableWidget.selectedIndexes():
            if index.column() == 2:
                self.ui.hostnameLineEdit.setText(self.ui.tableWidget.itemFromIndex(index).text())

    @pyqtSlot()
    def refresh(self):
        self.count=0
        self.ui.mainLabel.setText("Searching...")
        self.thread.start()
        self.ui.tableWidget.setRowCount(0)

    @pyqtSlot(str, str, str)
    def add_device(self, arg1, arg2, arg3):
        self.count += 1
        pos = self.ui.tableWidget.rowCount()
        self.ui.tableWidget.insertRow(pos)
        self.ui.tableWidget.setItem(pos, 0, QtWidgets.QTableWidgetItem(arg1))
        self.ui.tableWidget.setItem(pos, 1, QtWidgets.QTableWidgetItem(arg2))
        self.ui.tableWidget.setItem(pos, 2, QtWidgets.QTableWidgetItem(arg3))
        self.update_mainlabel()

    @pyqtSlot()
    def refresh_finished(self):
        print("Finished, back in UI")
        self.update_mainlabel(finished=True)

    def update_mainlabel(self, finished=False):
        self.ui.mainLabel.setText(("Finished search." if finished else "Searching...") +
                                  " Found " + str(self.count) + (" device" if self.count==1 else " devices"))