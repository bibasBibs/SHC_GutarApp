from PyQt5 import QtCore, QtGui, QtWidgets


class TuningWindow(QtWidgets.QDialog):
    def __init__(self, db_manager, user_id, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.user_id = user_id
        self.current_tuning = None
        self.setupUi()
        self.load_tunings()

    def setupUi(self):
        self.setObjectName("TuningWindow")
        self.resize(800, 700)
        self.setFixedSize(800, 700)

        self.setWindowFlags(
            self.windowFlags() & ~QtCore.Qt.WindowContextHelpButtonHint)

        self.setStyleSheet("""
            font: 8pt "Fixedsys";
            background-color: rgb(61, 61, 61);
        """)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        title_label = QtWidgets.QLabel("Выбор гитарного строя")
        font = QtGui.QFont()
        font.setFamily("MS Serif")
        font.setPointSize(20)
        font.setBold(False)
        font.setItalic(False)
        font.setWeight(50)
        title_label.setFont(font)
        title_label.setAlignment(QtCore.Qt.AlignCenter)
        title_label.setStyleSheet("""
            color: rgb(0, 170, 0);
            background-color: rgb(53, 53, 53);
            font: 20pt "MS Serif";
            border-width: 3px;
            border-style: dashed;
            border-color: #00aa00;
            padding: 10px;
        """)
        main_layout.addWidget(title_label)

        container_layout = QtWidgets.QHBoxLayout()

        left_layout = QtWidgets.QVBoxLayout()

        list_label = QtWidgets.QLabel("Доступные строи:")
        list_label.setStyleSheet("""
            color: rgb(0, 170, 0);
            font: 14pt "MS Serif";
            background-color: transparent;
        """)
        left_layout.addWidget(list_label)

        self.tunings_list = QtWidgets.QListWidget()
        self.tunings_list.setStyleSheet("""
            QListWidget {
                color: rgb(0, 170, 0);
                background-color: rgb(157, 157, 157);
                font: 12pt "MS Serif";
                border-width: 3px;
                border-style: solid;
                border-color: #00aa00;
                padding: 5px;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #555555;
            }
            QListWidget::item:selected {
                background-color: #00aa00;
                color: white;
            }
        """)
        self.tunings_list.itemClicked.connect(self.on_tuning_selected)
        left_layout.addWidget(self.tunings_list)

        container_layout.addLayout(left_layout)

        right_layout = QtWidgets.QVBoxLayout()

        create_label = QtWidgets.QLabel("Создать новый строй:")
        create_label.setStyleSheet("""
            color: rgb(0, 170, 0);
            font: 14pt "MS Serif";
            background-color: transparent;
        """)
        right_layout.addWidget(create_label)

        self.string_edits = []
        string_names = ["6 струна (толстая)", "5 струна", "4 струна",
                        "3 струна", "2 струна", "1 струна (тонкая)"]

        for i, name in enumerate(string_names):
            string_layout = QtWidgets.QHBoxLayout()

            name_label = QtWidgets.QLabel(name)
            name_label.setStyleSheet("""
                color: rgb(0, 170, 0);
                font: 10pt "MS Serif";
                min-width: 120px;
            """)
            string_layout.addWidget(name_label)

            string_edit = QtWidgets.QLineEdit()
            string_edit.setPlaceholderText("Например: E2")
            string_edit.setStyleSheet("""
                color: rgb(0, 170, 0);
                background-color: rgb(157, 157, 157);
                font: 10pt "MS Serif";
                border-width: 2px;
                border-style: solid;
                border-color: #00aa00;
                padding: 5px;
            """)
            self.string_edits.append(string_edit)
            string_layout.addWidget(string_edit)

            right_layout.addLayout(string_layout)

        name_layout = QtWidgets.QHBoxLayout()
        name_label = QtWidgets.QLabel("Название строя:")
        name_label.setStyleSheet("""
            color: rgb(0, 170, 0);
            font: 12pt "MS Serif";
            min-width: 120px;
        """)
        name_layout.addWidget(name_label)

        self.tuning_name_edit = QtWidgets.QLineEdit()
        self.tuning_name_edit.setPlaceholderText("Мой строй")
        self.tuning_name_edit.setStyleSheet("""
            color: rgb(0, 170, 0);
            background-color: rgb(157, 157, 157);
            font: 12pt "MS Serif";
            border-width: 2px;
            border-style: solid;
            border-color: #00aa00;
            padding: 5px;
        """)
        name_layout.addWidget(self.tuning_name_edit)
        right_layout.addLayout(name_layout)

        # Кнопка создания строя
        self.create_btn = QtWidgets.QPushButton("Создать строй")
        self.create_btn.setStyleSheet("""
            QPushButton {
                color: rgb(0, 170, 0);
                background-color: rgb(36, 36, 36);
                font: 12pt "MS Serif";
                border-width: 3px;
                border-style: solid;
                border-color: #00aa00;
                padding: 8px;
                margin-top: 10px;
            }
            QPushButton:hover {
                background-color: rgb(50, 50, 50);
            }
            QPushButton:pressed {
                background-color: rgb(70, 70, 70);
            }
        """)
        self.create_btn.clicked.connect(self.create_tuning)
        right_layout.addWidget(self.create_btn)

        container_layout.addLayout(right_layout)
        main_layout.addLayout(container_layout)

        display_frame = QtWidgets.QFrame()
        display_frame.setStyleSheet("""
            background-color: rgb(53, 53, 53);
            border: 2px solid #00aa00;
            padding: 10px;
        """)

        display_layout = QtWidgets.QVBoxLayout()

        display_label = QtWidgets.QLabel("Выбранный строй:")
        display_label.setStyleSheet("""
            color: rgb(0, 170, 0);
            font: 14pt "MS Serif";
            background-color: transparent;
        """)
        display_layout.addWidget(display_label)

        self.tuning_display = QtWidgets.QLabel("Выберите строй из списка")
        self.tuning_display.setAlignment(QtCore.Qt.AlignCenter)
        self.tuning_display.setStyleSheet("""
            color: rgb(0, 170, 0);
            background-color: rgb(157, 157, 157);
            font: 16pt "MS Serif";
            border-width: 3px;
            border-style: solid;
            border-color: #00aa00;
            padding: 15px;
            min-height: 40px;
        """)
        display_layout.addWidget(self.tuning_display)

        display_frame.setLayout(display_layout)
        main_layout.addWidget(display_frame)

        buttons_layout = QtWidgets.QHBoxLayout()

        self.delete_btn = QtWidgets.QPushButton("Удалить строй")
        self.delete_btn.setStyleSheet("""
            QPushButton {
                color: rgb(255, 255, 255);
                background-color: rgb(170, 0, 0);
                font: 12pt "MS Serif";
                border-width: 3px;
                border-style: solid;
                border-color: #aa0000;
                padding: 8px;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: rgb(200, 0, 0);
            }
            QPushButton:pressed {
                background-color: rgb(140, 0, 0);
            }
            QPushButton:disabled {
                background-color: rgb(100, 100, 100);
                color: rgb(150, 150, 150);
            }
        """)
        self.delete_btn.clicked.connect(self.delete_tuning)
        self.delete_btn.setEnabled(False)
        buttons_layout.addWidget(self.delete_btn)

        close_btn = QtWidgets.QPushButton("Закрыть")
        close_btn.setStyleSheet("""
            QPushButton {
                color: rgb(0, 170, 0);
                background-color: rgb(36, 36, 36);
                font: 12pt "MS Serif";
                border-width: 3px;
                border-style: solid;
                border-color: #00aa00;
                padding: 8px;
                min-width: 140px;
            }
            QPushButton:hover {
                background-color: rgb(50, 50, 50);
            }
            QPushButton:pressed {
                background-color: rgb(70, 70, 70);
            }
        """)
        close_btn.clicked.connect(self.close)
        buttons_layout.addWidget(close_btn)

        main_layout.addLayout(buttons_layout)

        self.setLayout(main_layout)

    def load_tunings(self):
        self.tunings_list.clear()
        tunings = self.db_manager.get_user_tunings(self.user_id)

        for tuning in tunings:
            item = QtWidgets.QListWidgetItem(tuning['name'])
            item.setData(QtCore.Qt.UserRole, tuning)
            self.tunings_list.addItem(item)

    def on_tuning_selected(self, item):
        tuning_data = item.data(QtCore.Qt.UserRole)
        self.current_tuning = tuning_data

        strings_text = " - ".join(tuning_data['strings'])
        self.tuning_display.setText(f"{tuning_data['name']}: {strings_text}")

        is_standard = tuning_data['name'] in ["Стандартный", "Drop D",
                                              "Open G", "Полутон ниже"]
        self.delete_btn.setEnabled(not is_standard)

    def create_tuning(self):
        tuning_name = self.tuning_name_edit.text().strip()
        if not tuning_name:
            self.show_message("Введите название строя!", "error")
            return

        existing_tunings = self.db_manager.get_user_tunings(self.user_id)
        for tuning in existing_tunings:
            if tuning['name'].lower() == tuning_name.lower():
                self.show_message("Строй с таким названием уже существует!",
                                  "error")
                return

        strings = []
        for edit in self.string_edits:
            note = edit.text().strip().upper()
            if note:
                strings.append(note)
            else:
                self.show_message("Заполните все поля струн!", "error")
                return

        if len(strings) != 6:
            self.show_message("Должно быть 6 струн!", "error")
            return

        success, message = self.db_manager.save_tuning(self.user_id,
                                                       tuning_name, strings)

        if success:
            self.show_message("Строй успешно создан!", "success")
            self.load_tunings()
            self.clear_form()
        else:
            self.show_message(message, "error")

    def delete_tuning(self):
        if not self.current_tuning:
            return

        # Проверяем, не стандартный ли это строй
        if self.current_tuning['name'] in ["Стандартный", "Drop D", "Open G",
                                           "Полутон ниже"]:
            self.show_message("Нельзя удалить стандартный строй!", "error")
            return

        reply = QtWidgets.QMessageBox.question(
            self,
            "Подтверждение удаления",
            f"Вы уверены, что хотите удалить строй '{self.current_tuning['name']}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No,
            QtWidgets.QMessageBox.No
        )

        if reply == QtWidgets.QMessageBox.Yes:
            success, message = self.db_manager.delete_tuning(self.user_id,
                                                             self.current_tuning[
                                                                 'name'])

            if success:
                self.show_message("Строй успешно удален!", "success")
                self.load_tunings()
                self.current_tuning = None
                self.tuning_display.setText("Выберите строй из списка")
                self.delete_btn.setEnabled(False)
            else:
                self.show_message(message, "error")

    def clear_form(self):
        self.tuning_name_edit.clear()
        for edit in self.string_edits:
            edit.clear()

    def show_message(self, message, message_type):
        msg = QtWidgets.QMessageBox(self)
        msg.setStyleSheet("""
            QMessageBox {
                font: 8pt "Fixedsys";
                background-color: rgb(61, 61, 61);
            }
            QMessageBox QLabel {
                color: rgb(0, 170, 0);
                font: 12pt "MS Serif";
            }
            QMessageBox QPushButton {
                color: rgb(0, 170, 0);
                background-color: rgb(36, 36, 36);
                font: 12pt "MS Serif";
                border-width: 2px;
                border-style: solid;
                border-color: #00aa00;
                padding: 5px 15px;
                min-width: 80px;
            }
        """)

        if message_type == "success":
            msg.setWindowTitle("Успех")
            msg.setText(message)
        else:
            msg.setWindowTitle("Ошибка")
            msg.setText(message)

        msg.exec_()