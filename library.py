# library.py
# Самодостаточный модуль библиотеки:
# - Ui_Form: строит UI библиотеки (без .ui файла)
# - LibraryController: управляет навигацией Разделы -> Темы -> Текст
#
# Важно: front.py ожидает "from library import Ui_Form", поэтому Ui_Form здесь обязателен.

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    """
    Самостоятельный UI библиотеки.
    Ожидаемые наружу поля (используются в front.py / main.py):
      - mode_list : QListWidget (Tuner/Library/Game)
      - listWidget: QListWidget (контент: разделы/темы/текст)
      - pushButton: QPushButton (кнопка "Back"/"Назад")
    """

    def setupUi(self, Form):
        Form.setObjectName("LibraryForm")
        Form.resize(800, 540)
        Form.setStyleSheet(
            "background-color: rgb(61, 61, 61);\n"
            "font: 10pt \"MS Serif\";\n"
        )

        # --- root layout ---
        self.horizontalLayout = QtWidgets.QHBoxLayout(Form)
        self.horizontalLayout.setContentsMargins(8, 8, 8, 8)
        self.horizontalLayout.setSpacing(8)

        # --- left panel (mode list) ---
        self.leftPanel = QtWidgets.QFrame(Form)
        self.leftPanel.setMinimumWidth(160)
        self.leftPanel.setStyleSheet(
            "QFrame { background-color: rgb(53, 53, 53); border: 3px dashed #00aa00; }"
        )
        self.leftLayout = QtWidgets.QVBoxLayout(self.leftPanel)
        self.leftLayout.setContentsMargins(8, 8, 8, 8)
        self.leftLayout.setSpacing(8)

        self.modeTitle = QtWidgets.QLabel(self.leftPanel)
        self.modeTitle.setAlignment(QtCore.Qt.AlignCenter)
        self.modeTitle.setStyleSheet(
            "color: rgb(0, 170, 0);\n"
            "font: 18pt \"MS Serif\";\n"
            "background-color: transparent;"
        )
        self.modeTitle.setText("MENU")

        self.mode_list = QtWidgets.QListWidget(self.leftPanel)
        self.mode_list.setObjectName("mode_list")
        self.mode_list.setStyleSheet(
            "QListWidget { color: rgb(0, 170, 0); background-color: rgb(61, 61, 61); "
            "border: 2px solid #00aa00; }"
            "QListWidget::item { padding: 10px; }"
            "QListWidget::item:selected { background-color: rgb(80, 80, 80); }"
        )
        self.mode_list.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.mode_list.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)

        # items
        self.mode_list.addItem("Tuner")
        self.mode_list.addItem("Library")
        self.mode_list.addItem("Game")

        self.leftLayout.addWidget(self.modeTitle)
        self.leftLayout.addWidget(self.mode_list)

        # --- right panel (content + back) ---
        self.rightPanel = QtWidgets.QFrame(Form)
        self.rightPanel.setStyleSheet(
            "QFrame { background-color: rgb(53, 53, 53); border: 3px dashed #00aa00; }"
        )
        self.rightLayout = QtWidgets.QVBoxLayout(self.rightPanel)
        self.rightLayout.setContentsMargins(8, 8, 8, 8)
        self.rightLayout.setSpacing(8)

        self.header = QtWidgets.QLabel(self.rightPanel)
        self.header.setAlignment(QtCore.Qt.AlignCenter)
        self.header.setStyleSheet(
            "color: rgb(0, 170, 0);\n"
            "font: 22pt \"MS Serif\";\n"
            "background-color: transparent;"
        )
        self.header.setText("Library")

        self.listWidget = QtWidgets.QListWidget(self.rightPanel)
        self.listWidget.setObjectName("listWidget")
        self.listWidget.setStyleSheet(
            "QListWidget { color: rgb(0, 170, 0); background-color: rgb(61, 61, 61); "
            "border: 2px solid #00aa00; }"
            "QListWidget::item { padding: 10px; }"
            "QListWidget::item:selected { background-color: rgb(80, 80, 80); }"
        )
        self.listWidget.setWordWrap(True)

        self.pushButton = QtWidgets.QPushButton(self.rightPanel)
        self.pushButton.setObjectName("pushButton")
        self.pushButton.setText("Back")
        self.pushButton.setStyleSheet(
            "QPushButton { color: rgb(0, 170, 0); background-color: rgb(61, 61, 61); "
            "border: 2px solid #00aa00; padding: 10px; font: 14pt \"MS Serif\"; }"
            "QPushButton:hover { background-color: rgb(80, 80, 80); }"
            "QPushButton:pressed { background-color: rgb(90, 90, 90); }"
        )

        self.rightLayout.addWidget(self.header)
        self.rightLayout.addWidget(self.listWidget, 1)
        self.rightLayout.addWidget(self.pushButton)

        # --- compose ---
        self.horizontalLayout.addWidget(self.leftPanel)
        self.horizontalLayout.addWidget(self.rightPanel, 1)

        QtCore.QMetaObject.connectSlotsByName(Form)


class LibraryController:
    """
    Контроллер библиотеки: Разделы -> Темы -> Текст.
    Работает поверх Ui_Form (ui.listWidget, ui.pushButton).

    on_exit (опционально): вызывается, если пользователь нажал Back на уровне разделов.
    """

    def __init__(self, ui, on_exit=None):
        self.ui = ui
        self.on_exit = on_exit

        self.library_data = self.get_library_data()
        self._level = "sections"  # sections | topics | text
        self._section = None
        self._topic = None

        self._connect_ui()
        self.show_sections()

    # ---------- UI wiring ----------

    def _connect_ui(self):
        try:
            self.ui.listWidget.itemClicked.disconnect()
        except Exception:
            pass
        self.ui.listWidget.itemClicked.connect(self._on_item_clicked)

        try:
            self.ui.pushButton.clicked.disconnect()
        except Exception:
            pass
        self.ui.pushButton.clicked.connect(self._on_back_clicked)

    # ---------- Navigation ----------

    def show_sections(self):
        self._level = "sections"
        self._section = None
        self._topic = None

        lw = self.ui.listWidget
        lw.clear()

        for section_name in sorted(self.library_data.keys()):
            lw.addItem(section_name)

        lw.addItem("— выбери раздел —")

    def show_topics(self, section_name: str):
        self._level = "topics"
        self._section = section_name
        self._topic = None

        lw = self.ui.listWidget
        lw.clear()

        topics = self.library_data.get(section_name, {})
        for topic_name in sorted(topics.keys()):
            lw.addItem(topic_name)

        lw.addItem("— выбери тему —")

    def show_text(self, section_name: str, topic_name: str):
        self._level = "text"
        self._section = section_name
        self._topic = topic_name

        text = self.library_data.get(section_name, {}).get(topic_name, "")
        if not text:
            text = "Пусто."

        lw = self.ui.listWidget
        lw.clear()
        lw.addItem(text)

    def _on_item_clicked(self, item):
        title = (item.text() or "").strip()
        if not title or title.startswith("—"):
            return

        if self._level == "sections":
            if title in self.library_data:
                self.show_topics(title)
            return

        if self._level == "topics":
            section = self._section
            if section and title in self.library_data.get(section, {}):
                self.show_text(section, title)
            return

        # level == "text": клики игнорируем

    def _on_back_clicked(self):
        # текст -> темы
        if self._level == "text":
            if self._section:
                self.show_topics(self._section)
            else:
                self.show_sections()
            return

        # темы -> разделы
        if self._level == "topics":
            self.show_sections()
            return

        # разделы -> выход
        if callable(self.on_exit):
            self.on_exit()

    # ---------- Content ----------

    def get_library_data(self):
        """
        Раздел -> Тема -> Текст
        Можно дополнять сколько угодно — логика UI не меняется.
        """
        return {
            "Гриф и ноты": {
                "Ноты на грифе": (
                    "Ноты на грифе (стандартный строй: E A D G B E)\n\n"
                    "Главное правило:\n"
                    "• Каждый лад = +1 полутон.\n"
                    "• 12-й лад = та же нота, но октава выше.\n\n"
                    "Хроматика:\n"
                    "C → C# → D → D# → E → F → F# → G → G# → A → A# → B\n\n"
                    "Открытые струны:\n"
                    "6:E  5:A  4:D  3:G  2:B  1:E\n\n"
                    "Быстрые ориентиры:\n"
                    "• 5-й лад: 6→A, 5→D, 4→G, 3→C, 2→E, 1→A\n"
                    "• 7-й лад: 6→B, 5→E, 4→A, 3→D, 2→F#, 1→B\n"
                    "• 12-й лад: повтор открытой струны (октава)\n"
                ),
                "Октавы на грифе": (
                    "Октавы помогают быстро находить ту же ноту в другой позиции.\n\n"
                    "Правило:\n"
                    "• На 2 струны ниже и +2 лада (кроме перехода G↔B: там +3).\n\n"
                    "Пример:\n"
                    "6-я, 5 лад (A) → 4-я, 7 лад (A)\n"
                ),
                "Интервалы": (
                    "Интервалы — расстояния между нотами в полутонах.\n\n"
                    "Полезные:\n"
                    "• Кварта = 5\n"
                    "• Квинта = 7\n"
                    "• Октава = 12\n"
                ),
            },
            "Теория": {
                "Как работает тюнер": (
                    "Тюнер делает так:\n"
                    "1) Из звука оценивает частоту (Гц)\n"
                    "2) Находит ближайшую ноту\n"
                    "3) Показывает отклонение в cents (100 cents = 1 полутон)\n"
                ),
                "Мажор и минор": (
                    "Отличие в терции:\n"
                    "• Мажор: +4 полутона от тоники\n"
                    "• Минор: +3 полутона от тоники\n"
                ),
                "Как строятся аккорды": (
                    "Базовые трезвучия:\n"
                    "• Мажор: 0, +4, +7\n"
                    "• Минор: 0, +3, +7\n\n"
                    "Аккорд — это несколько нот одновременно.\n"
                ),
            },
            "Практика": {
                "Разминка на 5 минут": (
                    "1) Хроматика 1-2-3-4 по струнам\n"
                    "2) Легато на одной струне\n"
                    "3) Альтернативный штрих под метроном\n"
                ),
                "Почему нота прыгает": (
                    "Частота может прыгать из-за:\n"
                    "• сильной атаки (в начале нота часто выше)\n"
                    "• гармоник, которые громче фундамента\n"
                    "• шума/перегруза\n\n"
                    "Ориентируйся на «устоявшуюся» часть звука через 0.3–0.5 сек.\n"
                ),
            },
            "Звук и оборудование": {
                "Аудиокарта и входы": (
                    "Если у карты 2 входа, в настройках выбери правильный Input 1 / Input 2.\n"
                    "Если перепутать — сигнал будет слабым или не тем.\n"
                ),
            },
            "Игра": {
                "Как работает режим игры": (
                    "Игра использует ту же детекцию, что и тюнер: ближайшая нота определяется всегда.\n"
                    "В игре сравнение без октав, чтобы учить ноты, а не заставлять идеально строить.\n"
                ),
            },
        }
