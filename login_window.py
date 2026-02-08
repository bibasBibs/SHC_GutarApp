from PyQt5 import QtCore, QtGui, QtWidgets


class LoginWindow(QtWidgets.QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.current_user = None
        self.user_id = None
        self.setupUi()

    def setupUi(self):
        self.setObjectName("LoginWindow")
        self.resize(400, 400)
        self.setFixedSize(400, 400)

        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)
        self.setStyleSheet("""
            font: 8pt "Fixedsys";
            background-color: rgb(61, 61, 61);
        """)

        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = QtWidgets.QLabel("Гитарный тюнер")
        title_label.setGeometry(QtCore.QRect(0, 0, 400, 60))
        font = QtGui.QFont()
        font.setFamily("MS Serif")
        font.setPointSize(24)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        title_label.setFont(font)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("""
            color: rgb(0, 170, 0);
            background-color: rgb(53, 53, 53);
            font: 24pt "MS Serif";
            border-width: 3px;
            border-style: dashed;
            border-color: #00aa00;
            padding: 10px;
        """)
        layout.addWidget(title_label)

        self.username_edit = QtWidgets.QLineEdit()
        self.username_edit.setPlaceholderText("Логин")
        self.username_edit.setStyleSheet("""
            color: rgb(0, 170, 0);
            background-color: rgb(157, 157, 157);
            font: 14pt "MS Serif";
            border-width: 3px;
            border-style: solid;
            border-color: #00aa00;
            padding: 8px;
        """)
        layout.addWidget(self.username_edit)

        self.password_edit = QtWidgets.QLineEdit()
        self.password_edit.setPlaceholderText("Пароль")
        self.password_edit.setEchoMode(QtWidgets.QLineEdit.Password)
        self.password_edit.setStyleSheet("""
            color: rgb(0, 170, 0);
            background-color: rgb(157, 157, 157);
            font: 14pt "MS Serif";
            border-width: 3px;
            border-style: solid;
            border-color: #00aa00;
            padding: 8px;
        """)
        layout.addWidget(self.password_edit)

        buttons_layout = QtWidgets.QHBoxLayout()

        self.login_btn = QtWidgets.QPushButton("Войти")
        self.login_btn.setStyleSheet("""
            QPushButton {
                color: rgb(0, 170, 0);
                background-color: rgb(36, 36, 36);
                font: 14pt "MS Serif";
                border-width: 3px;
                border-style: solid;
                border-color: #00aa00;
                padding: 10px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: rgb(50, 50, 50);
            }
            QPushButton:pressed {
                background-color: rgb(70, 70, 70);
            }
        """)
        self.login_btn.clicked.connect(self.login)
        buttons_layout.addWidget(self.login_btn)

        self.register_btn = QtWidgets.QPushButton("Регистрация")
        self.register_btn.setStyleSheet("""
            QPushButton {
                color: rgb(0, 170, 0);
                background-color: rgb(36, 36, 36);
                font: 14pt "MS Serif";
                border-width: 3px;
                border-style: solid;
                border-color: #00aa00;
                padding: 10px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: rgb(50, 50, 50);
            }
            QPushButton:pressed {
                background-color: rgb(70, 70, 70);
            }
        """)
        self.register_btn.clicked.connect(self.register)
        buttons_layout.addWidget(self.register_btn)

        layout.addLayout(buttons_layout)

        self.status_label = QtWidgets.QLabel("Введите логин и пароль")
        self.status_label.setAlignment(QtCore.Qt.AlignCenter)
        self.status_label.setStyleSheet("""
            color: rgb(0, 170, 0);
            font: 12pt "MS Serif";
            background-color: rgb(53, 53, 53);
            border: 1px solid #00aa00;
            padding: 8px;
        """)
        layout.addWidget(self.status_label)

        self.setLayout(layout)

        self.username_edit.returnPressed.connect(self.login)
        self.password_edit.returnPressed.connect(self.login)

    def login(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text()

        if not username or not password:
            self.show_status("Заполните все поля!", "error")
            return

        success, message, user_id, username = self.db_manager.login_user(
            username, password)

        if success:
            self.user_id = user_id
            self.current_user = username
            self.show_status(f"Добро пожаловать, {username}!", "success")
            QtCore.QTimer.singleShot(1000, self.accept)
        else:
            self.show_status(message, "error")

    def register(self):
        username = self.username_edit.text().strip()
        password = self.password_edit.text()

        if not username or not password:
            self.show_status("Заполните все поля!", "error")
            return

        if len(username) < 3:
            self.show_status("Логин должен содержать минимум 3 символа!",
                             "error")
            return

        if len(password) < 4:
            self.show_status("Пароль должен содержать минимум 4 символа!",
                             "error")
            return

        success, message = self.db_manager.register_user(username, password)

        if success:
            self.show_status("Регистрация успешна! Теперь войдите", "success")
            self.password_edit.clear()
        else:
            self.show_status(message, "error")

    def show_status(self, message, message_type):
        if message_type == "success":
            self.status_label.setStyleSheet("""
                color: rgb(0, 255, 0);
                font: 12pt "MS Serif";
                background-color: rgb(53, 53, 53);
                border: 1px solid #00ff00;
                padding: 8px;
            """)
        else:
            self.status_label.setStyleSheet("""
                color: rgb(255, 0, 0);
                font: 12pt "MS Serif";
                background-color: rgb(53, 53, 53);
                border: 1px solid #ff0000;
                padding: 8px;
            """)
        self.status_label.setText(message)

    def get_current_user(self):
        return self.current_user

    def get_user_id(self):
        return self.user_id
