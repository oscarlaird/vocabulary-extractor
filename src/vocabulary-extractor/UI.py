# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'UI.ui'
#
# Created by: PyQt5 UI code generator 5.9.2
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.setWindowModality(QtCore.Qt.ApplicationModal)
        Form.resize(420, 240)
        self.widget = QtWidgets.QWidget(Form)
        self.widget.setGeometry(QtCore.QRect(0, 0, 420, 240))
        self.widget.setMinimumSize(QtCore.QSize(401, 0))
        self.widget.setObjectName("widget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.widget)
        self.verticalLayout_3.setContentsMargins(5, 15, 5, 5)
        self.verticalLayout_3.setSpacing(5)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_2.setSizeConstraint(QtWidgets.QLayout.SetFixedSize)
        self.horizontalLayout_2.setContentsMargins(10, -1, 10, -1)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.stackedWidget = QtWidgets.QStackedWidget(self.widget)
        self.stackedWidget.setObjectName("stackedWidget")
        self.page = QtWidgets.QWidget()
        self.page.setMinimumSize(QtCore.QSize(0, 40))
        self.page.setObjectName("page")
        self.progressBar = QtWidgets.QProgressBar(self.page)
        self.progressBar.setGeometry(QtCore.QRect(7, 10, 305, 20))
        self.progressBar.setObjectName("progressBar")
        self.stackedWidget.addWidget(self.page)
        self.page_2 = QtWidgets.QWidget()
        self.page_2.setMinimumSize(QtCore.QSize(0, 40))
        self.page_2.setObjectName("page_2")
        self.bookbar = QtWidgets.QLineEdit(self.page_2)
        self.bookbar.setGeometry(QtCore.QRect(2, 10, 291, 20))
        self.bookbar.setMinimumSize(QtCore.QSize(40, 20))
        self.bookbar.setReadOnly(True)
        self.bookbar.setObjectName("bookbar")
        self.stackedWidget.addWidget(self.page_2)
        self.horizontalLayout_2.addWidget(self.stackedWidget)
        self.b1 = QtWidgets.QPushButton(self.widget)
        self.b1.setObjectName("b1")
        self.horizontalLayout_2.addWidget(self.b1)
        self.verticalLayout_3.addLayout(self.horizontalLayout_2)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setContentsMargins(10, 5, 10, 5)
        self.verticalLayout.setObjectName("verticalLayout")
        self.bigtext = QtWidgets.QLineEdit(self.widget)
        self.bigtext.setMinimumSize(QtCore.QSize(0, 30))
        self.bigtext.setStyleSheet("background-color: rgb(240, 240, 240);" "border-style: inset;" "font: 12pt \"Arial\";")
        self.bigtext.setDragEnabled(False)
        self.bigtext.setReadOnly(True)
        self.bigtext.setObjectName("bigtext")
        self.verticalLayout.addWidget(self.bigtext)
        self.smalltext = QtWidgets.QTextEdit(self.widget)
        self.smalltext.setMinimumSize(QtCore.QSize(0, 30))
        self.smalltext.setStyleSheet("background-color: rgb(240, 240, 240);" "border-style: inset;")
        self.smalltext.setReadOnly(True)
        self.smalltext.setObjectName("smalltext")
        self.verticalLayout.addWidget(self.smalltext)
        self.verticalLayout_3.addLayout(self.verticalLayout)
        self.horizontalLayout_4 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_4.setContentsMargins(20, 10, 20, 10)
        self.horizontalLayout_4.setSpacing(20)
        self.horizontalLayout_4.setObjectName("horizontalLayout_4")
        self.b4 = QtWidgets.QPushButton(self.widget)
        self.b4.setObjectName("b4")
        self.horizontalLayout_4.addWidget(self.b4)
        self.b3 = QtWidgets.QPushButton(self.widget)
        self.b3.setObjectName("b3")
        self.horizontalLayout_4.addWidget(self.b3)
        self.b2 = QtWidgets.QPushButton(self.widget)
        self.b2.setObjectName("b2")
        self.horizontalLayout_4.addWidget(self.b2)
        self.verticalLayout_3.addLayout(self.horizontalLayout_4)

        self.retranslateUi(Form)
        self.stackedWidget.setCurrentIndex(1)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Vocabulary Extractor"))
        self.b1.setText(_translate("Form", "browse"))
        self.b4.setText(_translate("Form", "help"))
        self.b3.setText(_translate("Form", "cancel"))
        self.b2.setText(_translate("Form", "next"))

