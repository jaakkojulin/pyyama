# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'pyyamamainwindow.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_PyYamaMainWindow(object):
    def setupUi(self, PyYamaMainWindow):
        PyYamaMainWindow.setObjectName("PyYamaMainWindow")
        PyYamaMainWindow.resize(323, 522)
        self.centralwidget = QtWidgets.QWidget(PyYamaMainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtWidgets.QGridLayout(self.centralwidget)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.tabWidget = QtWidgets.QTabWidget(self.centralwidget)
        self.tabWidget.setObjectName("tabWidget")
        self.tab = QtWidgets.QWidget()
        self.tab.setObjectName("tab")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.tab)
        self.verticalLayout.setObjectName("verticalLayout")
        self.nowplayingGroupBox = QtWidgets.QGroupBox(self.tab)
        self.nowplayingGroupBox.setObjectName("nowplayingGroupBox")
        self.formLayout_2 = QtWidgets.QFormLayout(self.nowplayingGroupBox)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_2 = QtWidgets.QLabel(self.nowplayingGroupBox)
        self.label_2.setObjectName("label_2")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.label_3 = QtWidgets.QLabel(self.nowplayingGroupBox)
        self.label_3.setObjectName("label_3")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.label_4 = QtWidgets.QLabel(self.nowplayingGroupBox)
        self.label_4.setObjectName("label_4")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.artistLabel = QtWidgets.QLabel(self.nowplayingGroupBox)
        self.artistLabel.setObjectName("artistLabel")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.artistLabel)
        self.trackLabel = QtWidgets.QLabel(self.nowplayingGroupBox)
        self.trackLabel.setObjectName("trackLabel")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.trackLabel)
        self.albumLabel = QtWidgets.QLabel(self.nowplayingGroupBox)
        self.albumLabel.setObjectName("albumLabel")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.albumLabel)
        self.verticalLayout.addWidget(self.nowplayingGroupBox)
        self.groupBox_2 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_2.setObjectName("groupBox_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.volumeSpinBox = QtWidgets.QDoubleSpinBox(self.groupBox_2)
        self.volumeSpinBox.setButtonSymbols(QtWidgets.QAbstractSpinBox.PlusMinus)
        self.volumeSpinBox.setKeyboardTracking(False)
        self.volumeSpinBox.setDecimals(1)
        self.volumeSpinBox.setMinimum(-255.0)
        self.volumeSpinBox.setMaximum(0.0)
        self.volumeSpinBox.setSingleStep(0.5)
        self.volumeSpinBox.setProperty("value", -80.0)
        self.volumeSpinBox.setObjectName("volumeSpinBox")
        self.gridLayout_3.addWidget(self.volumeSpinBox, 1, 1, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.groupBox_2)
        self.label_6.setObjectName("label_6")
        self.gridLayout_3.addWidget(self.label_6, 1, 0, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_2)
        self.groupBox_3 = QtWidgets.QGroupBox(self.tab)
        self.groupBox_3.setTitle("")
        self.groupBox_3.setObjectName("groupBox_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.groupBox_3)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.previousToolButton = QtWidgets.QToolButton(self.groupBox_3)
        icon = QtGui.QIcon.fromTheme("media-skip-backward")
        self.previousToolButton.setIcon(icon)
        self.previousToolButton.setIconSize(QtCore.QSize(32, 32))
        self.previousToolButton.setObjectName("previousToolButton")
        self.horizontalLayout.addWidget(self.previousToolButton)
        self.pauseToolButton = QtWidgets.QToolButton(self.groupBox_3)
        icon = QtGui.QIcon.fromTheme("media-playback-pause")
        self.pauseToolButton.setIcon(icon)
        self.pauseToolButton.setIconSize(QtCore.QSize(32, 32))
        self.pauseToolButton.setObjectName("pauseToolButton")
        self.horizontalLayout.addWidget(self.pauseToolButton)
        self.nextToolButton = QtWidgets.QToolButton(self.groupBox_3)
        icon = QtGui.QIcon.fromTheme("media-skip-forward")
        self.nextToolButton.setIcon(icon)
        self.nextToolButton.setIconSize(QtCore.QSize(32, 32))
        self.nextToolButton.setObjectName("nextToolButton")
        self.horizontalLayout.addWidget(self.nextToolButton)
        self.muteToolButton = QtWidgets.QToolButton(self.groupBox_3)
        icon = QtGui.QIcon.fromTheme("audio-volume-muted")
        self.muteToolButton.setIcon(icon)
        self.muteToolButton.setIconSize(QtCore.QSize(32, 32))
        self.muteToolButton.setObjectName("muteToolButton")
        self.horizontalLayout.addWidget(self.muteToolButton)
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.verticalLayout.addWidget(self.groupBox_3)
        self.groupBox = QtWidgets.QGroupBox(self.tab)
        self.groupBox.setObjectName("groupBox")
        self.formLayout = QtWidgets.QFormLayout(self.groupBox)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.groupBox)
        self.label.setObjectName("label")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label)
        self.inputComboBox = QtWidgets.QComboBox(self.groupBox)
        self.inputComboBox.setObjectName("inputComboBox")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.inputComboBox)
        self.label_5 = QtWidgets.QLabel(self.groupBox)
        self.label_5.setObjectName("label_5")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.zoneComboBox = QtWidgets.QComboBox(self.groupBox)
        self.zoneComboBox.setObjectName("zoneComboBox")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.zoneComboBox)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.formLayout.setItem(2, QtWidgets.QFormLayout.FieldRole, spacerItem1)
        self.verticalLayout.addWidget(self.groupBox)
        self.tabWidget.addTab(self.tab, "")
        self.tab_2 = QtWidgets.QWidget()
        self.tab_2.setObjectName("tab_2")
        self.gridLayout = QtWidgets.QGridLayout(self.tab_2)
        self.gridLayout.setObjectName("gridLayout")
        self.plainTextEdit = QtWidgets.QPlainTextEdit(self.tab_2)
        self.plainTextEdit.setObjectName("plainTextEdit")
        self.gridLayout.addWidget(self.plainTextEdit, 0, 0, 1, 1)
        self.modelNameLabel = QtWidgets.QLabel(self.tab_2)
        self.modelNameLabel.setObjectName("modelNameLabel")
        self.gridLayout.addWidget(self.modelNameLabel, 1, 0, 1, 1)
        self.tabWidget.addTab(self.tab_2, "")
        self.gridLayout_2.addWidget(self.tabWidget, 0, 0, 1, 1)
        PyYamaMainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(PyYamaMainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 323, 26))
        self.menubar.setObjectName("menubar")
        self.menu_File = QtWidgets.QMenu(self.menubar)
        self.menu_File.setObjectName("menu_File")
        self.menuHelp = QtWidgets.QMenu(self.menubar)
        self.menuHelp.setObjectName("menuHelp")
        PyYamaMainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(PyYamaMainWindow)
        self.statusbar.setObjectName("statusbar")
        PyYamaMainWindow.setStatusBar(self.statusbar)
        self.actionExit = QtWidgets.QAction(PyYamaMainWindow)
        self.actionExit.setObjectName("actionExit")
        self.actionAbout_PyYama = QtWidgets.QAction(PyYamaMainWindow)
        self.actionAbout_PyYama.setObjectName("actionAbout_PyYama")
        self.menu_File.addAction(self.actionExit)
        self.menuHelp.addAction(self.actionAbout_PyYama)
        self.menubar.addAction(self.menu_File.menuAction())
        self.menubar.addAction(self.menuHelp.menuAction())

        self.retranslateUi(PyYamaMainWindow)
        self.tabWidget.setCurrentIndex(0)
        QtCore.QMetaObject.connectSlotsByName(PyYamaMainWindow)

    def retranslateUi(self, PyYamaMainWindow):
        _translate = QtCore.QCoreApplication.translate
        PyYamaMainWindow.setWindowTitle(_translate("PyYamaMainWindow", "PyYama"))
        self.nowplayingGroupBox.setTitle(_translate("PyYamaMainWindow", "Now playing"))
        self.label_2.setText(_translate("PyYamaMainWindow", "Artist"))
        self.label_3.setText(_translate("PyYamaMainWindow", "Track"))
        self.label_4.setText(_translate("PyYamaMainWindow", "Album"))
        self.artistLabel.setText(_translate("PyYamaMainWindow", "TextLabel"))
        self.trackLabel.setText(_translate("PyYamaMainWindow", "TextLabel"))
        self.albumLabel.setText(_translate("PyYamaMainWindow", "TextLabel"))
        self.groupBox_2.setTitle(_translate("PyYamaMainWindow", "Control"))
        self.volumeSpinBox.setSuffix(_translate("PyYamaMainWindow", " dB"))
        self.label_6.setText(_translate("PyYamaMainWindow", "Volume"))
        self.previousToolButton.setText(_translate("PyYamaMainWindow", "..."))
        self.pauseToolButton.setText(_translate("PyYamaMainWindow", "..."))
        self.nextToolButton.setText(_translate("PyYamaMainWindow", "..."))
        self.muteToolButton.setText(_translate("PyYamaMainWindow", "..."))
        self.groupBox.setTitle(_translate("PyYamaMainWindow", "Input"))
        self.label.setText(_translate("PyYamaMainWindow", "Source"))
        self.label_5.setText(_translate("PyYamaMainWindow", "Zone"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab), _translate("PyYamaMainWindow", "Main"))
        self.modelNameLabel.setText(_translate("PyYamaMainWindow", "Model name"))
        self.tabWidget.setTabText(self.tabWidget.indexOf(self.tab_2), _translate("PyYamaMainWindow", "Debug"))
        self.menu_File.setTitle(_translate("PyYamaMainWindow", "&File"))
        self.menuHelp.setTitle(_translate("PyYamaMainWindow", "&Help"))
        self.actionExit.setText(_translate("PyYamaMainWindow", "E&xit"))
        self.actionAbout_PyYama.setText(_translate("PyYamaMainWindow", "&About PyYama..."))

