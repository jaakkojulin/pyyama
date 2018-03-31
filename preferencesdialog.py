from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import Qt, QSettings, QTimer, pyqtSlot
from ui_preferencesdialog import Ui_PreferencesDialog


class  PreferencesDialog(QtWidgets.QDialog):
    def __init__(self, host=''):
        """

        """
        super(PreferencesDialog, self).__init__()
        self.ui = Ui_PreferencesDialog()
        self.ui.setupUi(self)
        self.settings = QSettings()
        self.ui.autoconnectGroupBox.setChecked(self.settings.value("autoconnect", False, type=bool))
        self.ui.hostLineEdit.setText(self.settings.value("autoconnect_host", '', type=str))
        self.ui.defaultzoneLineEdit.setText(self.settings.value("default_zone", 'main', type=str))

    def accept(self):
        self.settings.setValue("autoconnect", self.ui.autoconnectGroupBox.isChecked())
        self.settings.setValue("autoconnect_host", self.ui.hostLineEdit.text())
        self.settings.setValue("default_zone", self.ui.defaultzoneLineEdit.text())

        super(PreferencesDialog, self).accept()
