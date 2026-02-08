from PyQt5 import QtWidgets, QtCore
from PyQt5 import QtGui
from note_detecter import NoteDetector
import random
import time


class GameWindow(QtWidgets.QWidget):
    exit_requested = QtCore.pyqtSignal()  # сигнал выхода в меню

    def __init__(self, frequency_source=None, parent=None):
        super().__init__(parent)

        # Источник частоты назначается позже (из main.py) или через аргумент frequency_source
        self.frequency_source = None
        self.detector = NoteDetector()

        self.last_note_time = 0
        self.player_lives_count = 3
        self.enemy_lives_count = 3
        self.current_level = 1
        self.game_active = False
        self.target_notes = []
        self.current_target_index = 0
        self.note_tolerance_cents = 50
        self.waiting_for_player = False

        self.setup_ui()
        self.timer = None

        # Если при создании передали анализатор — подключаем и запускаем таймер
        if frequency_source:
            self.set_frequency_source(frequency_source)

    def load_level(self, level_index):
        self.current_level = level_index

        self.target_notes = self.generate_notes_for_level(level_index)
        self.enemy_lives_count = len(self.target_notes)

        self.enemy_lives.setText(f"ENEMY HP: {self.enemy_lives_count}")

        enemy_pixmap = QtGui.QPixmap(f"rs/enemy{level_index + 1}.png")
        self.enemy_label.setPixmap(enemy_pixmap.scaled(
            self.enemy_label.size(),
            QtCore.Qt.KeepAspectRatio,
            QtCore.Qt.SmoothTransformation
        ))

        self.current_target_index = 0

        self.game_active = False
        self.waiting_for_player = False

        self.target_note.setText("TARGET NOTE: --")
        self.played_note.setText("YOUR NOTE: --")
        self.confirm_btn.setEnabled(False)

    def set_frequency_source(self, source):
        """Устанавливаем источник частоты и запускаем таймер"""
        self.frequency_source = source
        if not self.timer:
            self.timer = QtCore.QTimer()
            self.timer.timeout.connect(self.update_note)
            self.timer.start(100)
        print("[GameWindow] Frequency source установлен")

    # ================= UI =================
    def setup_ui(self):
        self.setStyleSheet("""
            QWidget { background-color: rgb(61, 61, 61); color: rgb(0, 170, 0); font-family: Fixedsys; }
            QLabel { background-color: rgb(36,36,36); border: 3px solid #00aa00; padding: 6px; }
            QPushButton { background-color: rgb(36,36,36); border: 3px solid #00aa00; padding: 8px; }
            QPushButton:hover { background-color: rgb(53,53,53); }
        """)

        self.stack = QtWidgets.QStackedLayout(self)

        # Меню выбора уровня
        self.menu_widget = self.create_level_menu()
        # Экран уровня
        self.level_widget = self.create_level_ui()

        self.stack.addWidget(self.menu_widget)
        self.stack.addWidget(self.level_widget)
        self.stack.setCurrentIndex(0)

    # ================= MENU =================
    def create_level_menu(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)

        title = QtWidgets.QLabel("SELECT LEVEL")
        title.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(title)

        for lvl in range(1, 7):
            btn = QtWidgets.QPushButton(f"LEVEL {lvl}")
            btn.clicked.connect(lambda _, l=lvl: self.select_level(l))
            layout.addWidget(btn)

        # ✅ Сюжет под списком уровней
        story = QtWidgets.QLabel(
            "БРИФИНГ\n\n"
            "Ты — гитарист в королевстве, где музыка объявлена вне закона.\n"
            "Злой Король ненавидит звук струн и охотится на музыкантов.\n\n"
            "Чтобы собрать рок-группу и добраться до замка, где тебя найдут союзники,\n"
            "нужно пройти 6 регионов королевства.\n\n"
            "В каждом регионе тебя поджидают приспешники Короля.\n"
            "Побеждай их, играя правильные ноты — и докажи, что музыку не запретить."
        )
        story.setWordWrap(True)
        story.setAlignment(QtCore.Qt.AlignCenter)
        story.setStyleSheet(
            "QLabel { background-color: rgb(36,36,36); border: 2px dashed #00aa00; padding: 10px; }"
        )
        layout.addWidget(story)

        # Выход в главное меню приложения
        exit_btn = QtWidgets.QPushButton("EXIT TO MAIN MENU")
        exit_btn.clicked.connect(lambda: self.exit_requested.emit())
        layout.addWidget(exit_btn)

        layout.addStretch()
        return w

    # ================= LEVEL UI =================
    def create_level_ui(self):
        w = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(w)

        # ---------- ENEMY HP ----------
        self.enemy_lives = QtWidgets.QLabel("ENEMY HP: 0")
        self.enemy_lives.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.enemy_lives)

        # ---------- NOTES ----------
        self.target_note = QtWidgets.QLabel("TARGET NOTE: --")
        self.played_note = QtWidgets.QLabel("YOUR NOTE: --")
        self.target_note.setAlignment(QtCore.Qt.AlignCenter)
        self.played_note.setAlignment(QtCore.Qt.AlignCenter)
        layout.addWidget(self.target_note)
        layout.addWidget(self.played_note)

        # ---------- DAMAGE MESSAGE ----------
        self.damage_label = QtWidgets.QLabel("")
        self.damage_label.setAlignment(QtCore.Qt.AlignCenter)
        self.damage_label.setStyleSheet(
            "QLabel { background-color: rgb(36,36,36); "
            "border: 2px solid #aa0000; color: rgb(255,80,80); "
            "padding: 6px; font-size: 12pt; }"
        )
        self.damage_label.hide()
        layout.addWidget(self.damage_label)

        # ---------- GAME AREA WITH GREEN BORDER ----------
        self.game_area = QtWidgets.QFrame()
        self.game_area.setFixedSize(500, 220)
        self.game_area.setStyleSheet(
            "QFrame { border: 3px solid #00aa00; background-color: black; }"
        )

        # ---------- BACKGROUND ----------
        self.background_label = QtWidgets.QLabel(self.game_area)
        self.background_label.setGeometry(0, 0, 500, 220)
        self.background_label.setScaledContents(True)
        self.background_label.setStyleSheet("border: none; background: transparent;")

        # ---------- ENEMY ----------
        self.enemy_label = QtWidgets.QLabel(self.game_area)
        self.enemy_label.setGeometry(180, 20, 140, 180)
        self.enemy_label.setAlignment(QtCore.Qt.AlignCenter)
        self.enemy_label.setStyleSheet("border: none; background: transparent;")
        self.enemy_label.raise_()

        layout.addWidget(self.game_area, alignment=QtCore.Qt.AlignCenter)

        # ---------- CONFIRM ----------
        self.confirm_btn = QtWidgets.QPushButton("CONFIRM NOTE")
        self.confirm_btn.setEnabled(False)
        self.confirm_btn.clicked.connect(self.confirm_note)
        layout.addWidget(self.confirm_btn, alignment=QtCore.Qt.AlignCenter)

        # ---------- START ----------
        self.start_battle_btn = QtWidgets.QPushButton("START LEVEL")
        self.start_battle_btn.clicked.connect(self.start_battle)
        layout.addWidget(self.start_battle_btn, alignment=QtCore.Qt.AlignCenter)

        # ---------- EXIT ----------
        exit_btn = QtWidgets.QPushButton("EXIT LEVEL")
        exit_btn.clicked.connect(self.exit_level)
        layout.addWidget(exit_btn, alignment=QtCore.Qt.AlignCenter)

        layout.addStretch()
        return w

    def load_level_background(self, level: int):
        path = f"rs/background{level}.png"
        pix = QtGui.QPixmap(path)

        if pix.isNull():
            self.background_label.clear()
            return

        self.background_label.setPixmap(
            pix.scaled(
                self.background_label.size(),
                QtCore.Qt.IgnoreAspectRatio,
                QtCore.Qt.SmoothTransformation
            )
        )

    def _show_damage_message(self, text: str, ms: int = 1200):
        self.damage_label.setText(text)
        self.damage_label.show()
        QtCore.QTimer.singleShot(ms, lambda: self.damage_label.hide())

    # ================= GAME LOGIC =================
    def select_level(self, level):
        self.stop_game()

        self.current_level = level
        self.target_notes = self.generate_notes_for_level(level)
        self.enemy_lives_count = 7

        self.game_active = False
        self.waiting_for_player = False

        self.enemy_lives.setText(f"ENEMY HP: {self.enemy_lives_count}")
        self.current_target_index = 0

        if self.target_notes:
            self.target_note.setText(
                f"LEVEL {level} - TARGET NOTE: {self._pitch_class(self.target_notes[0])}"
            )
        else:
            self.target_note.setText(f"LEVEL {level} - TARGET NOTE: --")

        self.played_note.setText("YOUR NOTE: --")

        self.confirm_btn.setEnabled(False)
        self.start_battle_btn.setEnabled(True)
        self.start_battle_btn.setText("START LEVEL")

        # ✅ скрываем полоску урона
        self.damage_label.hide()
        self.damage_label.setText("")

        self.stack.setCurrentIndex(1)

        # ✅ фон и враг для уровня
        self.load_level_background(level)
        self.load_enemy_model()

    def _chromatic_notes_sorted(self):
        """
        Возвращает список нот, отсортированный по частоте (в порядке хроматики).
        Нужен, чтобы брать "следующие 12 полутонов" = лады 1..12.
        """
        items = list(self.detector.guitar_frequencies.items())
        items.sort(key=lambda kv: kv[1])  # по частоте
        return [name for name, _ in items]

    def generate_notes_for_level(self, level_index):
        levels = [
            ("E4", "E5"),
            ("A3", "A4"),
            ("D3", "D4"),
            ("G3", "G4"),
            ("B3", "B4"),
            ("E4", "E5"),
        ]

        start_note, end_note = levels[(level_index - 1) % len(levels)]
        all_notes = list(self.detector.guitar_frequencies.keys())

        start_idx = all_notes.index(start_note)
        end_idx = all_notes.index(end_note)

        note_pool = all_notes[start_idx:end_idx + 1]

        # ✅ всегда 7 целей (если в пуле меньше — возьмём сколько есть)
        k = min(7, len(note_pool))
        return random.sample(note_pool, k=k)

    def _pitch_class(self, note: str) -> str:
        """
        'E4' -> 'E'
        'F#3' -> 'F#'
        'A2' -> 'A'
        """
        if not note:
            return ""
        while note and note[-1].isdigit():
            note = note[:-1]
        return note

    def note_on_allowed_string(self, note, strings):
        """Проверка: нота принадлежит выбранным струнам и до 12 лада"""
        if note[0] not in ''.join(strings):  # простой фильтр
            return any(note.startswith(s[0]) for s in strings)
        # Проверка лада
        # Получаем число из имени ноты, если есть
        try:
            fret_number = int(note[-1])
            if fret_number <= 12:
                return True
            else:
                return False
        except:
            return True

    def start_battle(self):
        self.game_active = True
        self.waiting_for_player = False
        self.current_target_index = 0

        self.enemy_lives.setText(f"ENEMY HP: {self.enemy_lives_count}")

        self.played_note.setText("YOUR NOTE: --")
        self.update_target_display()

    def stop_game(self):
        self.game_active = False
        self.current_target_index = 0
        self.waiting_for_player = False

    def update_target_display(self):
        if self.current_target_index < len(self.target_notes):
            target = self.target_notes[self.current_target_index]
            self.target_note.setText(
                f"LEVEL {self.current_level} - TARGET NOTE: {self._pitch_class(target)}"
            )
        else:
            self.game_win()

    def check_note(self, played_note, played_cents=0.0):
        if not self.game_active:
            return
        if self.waiting_for_player:
            return
        if not self.target_notes:
            return

        target_note = self.target_notes[self.current_target_index]

        played_pc = self._pitch_class(played_note)
        target_pc = self._pitch_class(target_note)

        if played_pc and played_pc == target_pc:
            self.played_note.setText(f"YOUR NOTE: {played_pc} ({played_cents:+.0f}c) ✔")

            # ✅ урон
            self.enemy_lives_count -= 1
            self.enemy_lives.setText(f"ENEMY HP: {self.enemy_lives_count}")

            # ✅ сообщение об уроне
            self._show_damage_message("Враг получил урон: -1 HP")

            if self.enemy_lives_count <= 0:
                self.game_win()
                return

            # цель меняется сразу после урона
            self.current_target_index += 1
            if self.current_target_index >= len(self.target_notes):
                self.current_target_index = 0
            self.update_target_display()
        else:
            shown = played_pc if played_pc else "--"
            self.played_note.setText(f"YOUR NOTE: {shown} ({played_cents:+.0f}c) ✖")

        self.waiting_for_player = True
        self.confirm_btn.setEnabled(True)

    def confirm_note(self):
        self.waiting_for_player = False
        self.confirm_btn.setEnabled(False)
        self.played_note.setText("YOUR NOTE: --")

    def update_lives(self):
        self.player_lives.setText(f"PLAYER HP: {self.player_lives_count}")
        self.enemy_lives.setText(f"ENEMY HP: {self.enemy_lives_count}")

    def game_win(self):
        self.game_active = False
        self.waiting_for_player = False

        self.target_note.setText("VICTORY!")
        self.played_note.setText("Регион зачищен")

        # небольшая пауза, чтобы игрок понял, что победил
        QtCore.QTimer.singleShot(
            1500,
            self.return_to_level_menu
        )

    def return_to_level_menu(self):
        self.stop_game()
        self.stack.setCurrentIndex(0)  # меню выбора уровней

    def exit_level(self):
        self.stop_game()
        self.stack.setCurrentIndex(0)
        self.exit_requested.emit()

    # ================= AUDIO =================
    def setup_timer(self):
        if not self.frequency_source:
            return
        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_note)
        self.timer.start(100)  # 10 раз в секунду

    def load_enemy_model(self):
        try:
            path = f"rs/enemy{self.current_level}.png"
            pixmap = QtGui.QPixmap(path)

            if pixmap.isNull():
                print(f"[WARN] enemy model not found: {path}")
                self.enemy_label.clear()
                return

            self.enemy_label.setPixmap(
                pixmap.scaled(
                    self.enemy_label.size(),
                    QtCore.Qt.KeepAspectRatio,
                    QtCore.Qt.SmoothTransformation
                )
            )
        except Exception as e:
            print(f"[ERROR] load_enemy_model: {e}")

    def update_note(self):
        # игра не активна или ждём подтверждения
        if not self.game_active or self.waiting_for_player:
            return

        if not self.frequency_source:
            return

        try:
            freq = self.frequency_source.get_frequency()
            if freq <= 0:
                return

            now = time.time()
            if now - self.last_note_time < 0.25:
                return

            data = self.detector.detect_for_game(freq)
            if not data:
                return

            self.last_note_time = now

            note = data["note"]
            cents = float(data.get("cents", 0.0))

            # Передаём и ноту, и cents (cents пока только для отображения, не для строгой проверки)
            self.check_note(note, cents)

        except Exception as e:
            print(f"[ERROR] update_note: {e}")

