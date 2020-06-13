# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'shortcutsUI.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(636, 133)
        self.verticalLayout = QtWidgets.QVBoxLayout(Dialog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.groupBox_4 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_4.setStyleSheet("font: 10pt \"Arial\";")
        self.groupBox_4.setObjectName("groupBox_4")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.groupBox_4)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.highlightShortcutEdit = QtWidgets.QKeySequenceEdit(self.groupBox_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.highlightShortcutEdit.sizePolicy().hasHeightForWidth())
        self.highlightShortcutEdit.setSizePolicy(sizePolicy)
        self.highlightShortcutEdit.setObjectName("highlightShortcutEdit")
        self.gridLayout_3.addWidget(self.highlightShortcutEdit, 0, 0, 1, 1)
        self.redefineShortcutEdit = QtWidgets.QKeySequenceEdit(self.groupBox_4)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.redefineShortcutEdit.sizePolicy().hasHeightForWidth())
        self.redefineShortcutEdit.setSizePolicy(sizePolicy)
        self.redefineShortcutEdit.setKeySequence("")
        self.redefineShortcutEdit.setObjectName("redefineShortcutEdit")
        self.gridLayout_3.addWidget(self.redefineShortcutEdit, 1, 0, 1, 1)
        self.redefineShortcutLabel = QtWidgets.QLabel(self.groupBox_4)
        self.redefineShortcutLabel.setObjectName("redefineShortcutLabel")
        self.gridLayout_3.addWidget(self.redefineShortcutLabel, 1, 1, 1, 1)
        self.highlightShortcutLabel = QtWidgets.QLabel(self.groupBox_4)
        self.highlightShortcutLabel.setObjectName("highlightShortcutLabel")
        self.gridLayout_3.addWidget(self.highlightShortcutLabel, 0, 1, 1, 1)
        self.verticalLayout.addWidget(self.groupBox_4)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setCenterButtons(True)
        self.buttonBox.setObjectName("buttonBox")
        self.verticalLayout.addWidget(self.buttonBox)

        self.retranslateUi(Dialog)
        self.buttonBox.accepted.connect(Dialog.accept)
        self.buttonBox.rejected.connect(Dialog.reject)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.groupBox_4.setTitle(_translate("Dialog", "Set Shortcuts"))
        self.redefineShortcutLabel.setText(_translate("Dialog", "Redefine Shortcut: Press [S] to use a definition of the selected word instead."))
        self.highlightShortcutLabel.setText(_translate("Dialog", "Highlight Shortcut: Press [S] to highlight the selected text."))

