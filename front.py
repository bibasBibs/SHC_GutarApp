from PyQt5 import QtCore, QtGui, QtWidgets
from library import Ui_Form
from resources import *
from game_window import GameWindow


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 540)

        self.stacked_widget = QtWidgets.QStackedWidget()
        MainWindow.setCentralWidget(self.stacked_widget)

        self.main_window = self.create_tuner_window()
        self.library_window = self.create_library_window()

        # ВАЖНО: GameWindow должен создаваться, но frequency_source будет установлен позже
        # из main.py
        self.game_window = GameWindow()  # Без параметров
        print(f"Ui_MainWindow: создан GameWindow, id={id(self.game_window)}")

        self.stacked_widget.addWidget(self.main_window)
        self.stacked_widget.addWidget(self.library_window)
        self.stacked_widget.addWidget(self.game_window)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def create_tuner_window(self):
        window_widget = QtWidgets.QWidget()
        window_widget.setObjectName("main_window")

        window_widget.setStyleSheet("font: 8pt \"Fixedsys\";\n"
                                    "background-color: rgb(61, 61, 61);")

        self.Game_name = QtWidgets.QLabel(window_widget)
        self.Game_name.setGeometry(QtCore.QRect(140, 0, 521, 71))
        font = QtGui.QFont()
        font.setFamily("MS Serif")
        font.setPointSize(35)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        self.Game_name.setFont(font)
        self.Game_name.setFocusPolicy(QtCore.Qt.TabFocus)
        self.Game_name.setStyleSheet("color: rgb(0, 170, 0);\n"
                                     "background-color: rgb(53, 53, 53);\n"
                                     "font: 35pt \"MS Serif\";\n"
                                     "\n"
                                     "border-width: 3px;\n"
                                     "border-style: dashed;\n"
                                     "border-color: #00aa00;\n"
                                     "")
        self.Game_name.setAlignment(QtCore.Qt.AlignCenter)
        self.Game_name.setObjectName("Game_name")

        self.Accaunt_bnt = QtWidgets.QToolButton(window_widget)
        self.Accaunt_bnt.setGeometry(QtCore.QRect(670, 0, 131, 121))
        self.Accaunt_bnt.setStyleSheet("border-width: 5px;\n"
                                       "border-style: solid;\n"
                                       "border-color: #00aa00;\n"
                                       "")
        self.Accaunt_bnt.setObjectName("Accaunt_bnt")

        self.tunerBar_low = QtWidgets.QProgressBar(window_widget)
        self.tunerBar_low.setGeometry(QtCore.QRect(160, 80, 231, 61))
        self.tunerBar_low.setLayoutDirection(QtCore.Qt.RightToLeft)
        self.tunerBar_low.setStyleSheet("QProgressBar {\n"
                                        "    background-color: #3d3d3d;\n"
                                        "    border: 1px solid darkgray;\n"
                                        "    border-color: #3d3d3d;\n"
                                        "\n"
                                        "\n"
                                        "}\n"
                                        "\n"
                                        "QProgressBar::chunk {\n"
                                        "    background-color: #ffc533;\n"
                                        "    color: rgb(255, 197, 51);\n"
                                        "    border-width: 2px;\n"
                                        "    border-style: solid;\n"
                                        "    border-color: #00aa00;\n"
                                        "\n"
                                        "}\n"
                                        "")
        self.tunerBar_low.setMinimum(-100)
        self.tunerBar_low.setMaximum(-5)
        self.tunerBar_low.setProperty("value", 0)
        self.tunerBar_low.setAlignment(QtCore.Qt.AlignCenter)
        self.tunerBar_low.setOrientation(QtCore.Qt.Horizontal)
        self.tunerBar_low.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.tunerBar_low.setFormat("")
        self.tunerBar_low.setObjectName("tunerBar_low")

        self.tunerBar_high = QtWidgets.QProgressBar(window_widget)
        self.tunerBar_high.setGeometry(QtCore.QRect(420, 80, 231, 61))
        self.tunerBar_high.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tunerBar_high.setStyleSheet("QProgressBar {\n"
                                         "    background-color: #3d3d3d;\n"
                                         "    border: 1px solid darkgray;\n"
                                         "    border-color: #3d3d3d;\n"
                                         "}\n"
                                         "\n"
                                         "QProgressBar::chunk {\n"
                                         "    background-color: #ff5601;\n"
                                         "    color: rgb(255, 197, 51);\n"
                                         "    border-width: 2px;\n"
                                         "    border-style: solid;\n"
                                         "    border-color: #00aa00;\n"
                                         "\n"
                                         "}")
        self.tunerBar_high.setMinimum(5)
        self.tunerBar_high.setProperty("value", 0)
        self.tunerBar_high.setAlignment(QtCore.Qt.AlignCenter)
        self.tunerBar_high.setOrientation(QtCore.Qt.Horizontal)
        self.tunerBar_high.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.tunerBar_high.setFormat("")
        self.tunerBar_high.setObjectName("tunerBar_high")

        self.tunerBar_complite = QtWidgets.QProgressBar(window_widget)
        self.tunerBar_complite.setGeometry(QtCore.QRect(395, 80, 21, 61))
        self.tunerBar_complite.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.tunerBar_complite.setStyleSheet("color: rgb(0, 170, 0);\n"
                                             "background-color: rgb(157, 157, 157);\n"
                                             "\n"
                                             "border-color: rgb(157, 157, 157);")
        self.tunerBar_complite.setMinimum(0)
        self.tunerBar_complite.setMaximum(1)
        self.tunerBar_complite.setProperty("value", 1)
        self.tunerBar_complite.setAlignment(QtCore.Qt.AlignCenter)
        self.tunerBar_complite.setOrientation(QtCore.Qt.Horizontal)
        self.tunerBar_complite.setTextDirection(
            QtWidgets.QProgressBar.TopToBottom)
        self.tunerBar_complite.setFormat("")
        self.tunerBar_complite.setObjectName("tunerBar_complite")

        self.label = QtWidgets.QLabel(window_widget)
        self.label.setGeometry(QtCore.QRect(40, 210, 391, 291))
        self.label.setStyleSheet(
            "QLabel{background-color: rgba(255, 85, 127, 0);}")
        self.label.setText("")
        self.label.setPixmap(QtGui.QPixmap(":/__52230446.png"))
        self.label.setScaledContents(False)
        self.label.setObjectName("label")

        self.label_2 = QtWidgets.QLabel(window_widget)
        self.label_2.setGeometry(QtCore.QRect(400, 380, 181, 161))
        self.label_2.setStyleSheet(
            "QLabel{background-color: rgba(255, 85, 127, 0);}")
        self.label_2.setText("")
        self.label_2.setPixmap(QtGui.QPixmap(":/__38985132.png"))
        self.label_2.setScaledContents(True)
        self.label_2.setAlignment(
            QtCore.Qt.AlignRight | QtCore.Qt.AlignTrailing | QtCore.Qt.AlignVCenter)
        self.label_2.setObjectName("label_2")

        self.label_3 = QtWidgets.QLabel(window_widget)
        self.label_3.setGeometry(QtCore.QRect(670, 130, 131, 181))
        self.label_3.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_3.setStyleSheet(
            "QLabel{background-color: rgb(157, 157, 157);\n"
            "border-width: 5px;\n"
            "border-style: solid;\n"
            "border-color: #00aa00;\n"
            "}\n"
            "")
        self.label_3.setText("")
        self.label_3.setPixmap(QtGui.QPixmap(":/pixel-art__7ebd4e43.png"))
        self.label_3.setAlignment(QtCore.Qt.AlignCenter)
        self.label_3.setObjectName("label_3")

        self.label_4 = QtWidgets.QLabel(window_widget)
        self.label_4.setGeometry(QtCore.QRect(360, 150, 91, 61))
        self.label_4.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.label_4.setStyleSheet("color: rgb(0, 170, 0);\n"
                                   "background-color: rgb(157, 157, 157);\n"
                                   "font: 20pt \"MS Serif\";\n"
                                   "border-width: 5px;\n"
                                   "border-style: solid;\n"
                                   "border-color: #00aa00;\n"
                                   "")
        self.label_4.setAlignment(QtCore.Qt.AlignCenter)
        self.label_4.setObjectName("label_4")

        self.label_5 = QtWidgets.QLabel(window_widget)
        self.label_5.setGeometry(QtCore.QRect(130, 420, 711, 101))
        self.label_5.setStyleSheet("background-color: rgb(0, 170, 0, 0);")
        self.label_5.setText("")
        self.label_5.setPixmap(QtGui.QPixmap(":/pixil-frame-0 (2).png"))
        self.label_5.setScaledContents(True)
        self.label_5.setObjectName("label_5")

        self.label_6 = QtWidgets.QLabel(window_widget)
        self.label_6.setGeometry(QtCore.QRect(690, 350, 101, 161))
        self.label_6.setStyleSheet("background-color: rgb(255, 255, 255, 0);")
        self.label_6.setText("")
        self.label_6.setPixmap(QtGui.QPixmap(":/pixil-frame-0 (3).png"))
        self.label_6.setScaledContents(True)
        self.label_6.setObjectName("label_6")

        self.pushButton = QtWidgets.QPushButton(window_widget)
        self.pushButton.setEnabled(True)
        self.pushButton.setGeometry(QtCore.QRect(10, 0, 121, 121))
        self.pushButton.setStyleSheet("color: rgb(0, 170, 0);\n"
                                      "background-color: rgb(36, 36, 36);\n"
                                      "border-width: 5px;\n"
                                      "border-style: solid;\n"
                                      "border-color: #00aa00;\n"
                                      "")
        self.pushButton.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/__3ab4d38b.png"), QtGui.QIcon.Normal,
                       QtGui.QIcon.Off)
        self.pushButton.setIcon(icon)
        self.pushButton.setIconSize(QtCore.QSize(111, 116))
        self.pushButton.setFlat(True)
        self.pushButton.setObjectName("pushButton")

        self.mode_list = QtWidgets.QListWidget(window_widget)
        self.mode_list.setGeometry(QtCore.QRect(10, 130, 121, 390))
        self.mode_list.setMinimumSize(QtCore.QSize(0, 0))
        self.mode_list.setMaximumSize(QtCore.QSize(9999, 9999))
        self.mode_list.setStyleSheet("color: rgb(0, 170, 0);\n"
                                     "background-color: rgb(157, 157, 157);\n"
                                     "font: 20pt \"MS Serif\";\n"
                                     "border-width: 5px;\n"
                                     "border-style: solid;\n"
                                     "border-color: #00aa00;\n"
                                     "")
        self.mode_list.setObjectName("mode_list")
        item = QtWidgets.QListWidgetItem()
        self.mode_list.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.mode_list.addItem(item)
        item = QtWidgets.QListWidgetItem()
        self.mode_list.addItem(item)

        # Расстановка z-order
        self.label_5.raise_()
        self.Game_name.raise_()
        self.Accaunt_bnt.raise_()
        self.tunerBar_low.raise_()
        self.tunerBar_high.raise_()
        self.tunerBar_complite.raise_()
        self.label.raise_()
        self.label_2.raise_()
        self.label_3.raise_()
        self.label_4.raise_()
        self.label_6.raise_()

        return window_widget

    def create_library_window(self):
        library_widget = QtWidgets.QWidget()
        self.library_ui = Ui_Form()
        self.library_ui.setupUi(library_widget)

        self.library_ui.pushButton.clicked.connect(
            lambda: self.stacked_widget.setCurrentIndex(0))

        self.library_ui.mode_list.itemClicked.connect(
            self.on_library_mode_selected)
        self.Accaunt_bnt.raise_()

        return library_widget

    def on_library_mode_selected(self, item):
        mode = item.text()
        if mode == "Tuner":
            self.stacked_widget.setCurrentIndex(0)
        elif mode == "Library":
            pass
        elif mode == "Game":
            self.stacked_widget.setCurrentIndex(2)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.Game_name.setText(_translate("MainWindow", "Tuner"))
        self.Accaunt_bnt.setText(_translate("MainWindow", "Avatar"))
        self.label_4.setText(_translate("MainWindow", "Note"))
        __sortingEnabled = self.mode_list.isSortingEnabled()
        self.mode_list.setSortingEnabled(False)
        item = self.mode_list.item(0)
        item.setText(_translate("MainWindow", "Tuner"))
        item = self.mode_list.item(1)
        item.setText(_translate("MainWindow", "Library"))
        item = self.mode_list.item(2)
        item.setText(_translate("MainWindow", "Game"))
        self.mode_list.setSortingEnabled(__sortingEnabled)