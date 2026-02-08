import sys
import math
from PyQt5 import QtWidgets, QtCore
from audio_settings_window import AudioSettingsWindow
from library import LibraryController


try:
    from front import Ui_MainWindow
    from analisator import Analisador
    from note_detecter import NoteDetector
    from database import UserDatabase
    from login_window import LoginWindow
    from tuning_window import TuningWindow
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


class GuitarTunerApp(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()

        try:
            # Инициализация базы данных
            self.db_manager = UserDatabase()

            # Показываем окно логина
            if not self.show_login():
                sys.exit(0)

            # Инициализация интерфейса
            self.ui = Ui_MainWindow()
            self.ui.setupUi(self)
            self.init_library()
            # Устанавливаем имя пользователя в интерфейсе
            self.set_user_in_interface()

            # Инициализация аудио анализатора
            try:
                print("Инициализация аудио анализатора...")
                self.frequency_analisator = Analisador()
                self.note_detecter = NoteDetector()
                self.frequency_analisator.start()
                print("Анализатор частоты запущен")
            except Exception as e:
                print(f"Ошибка инициализации аудио: {e}")
                self.frequency_analisator = None
                self.note_detecter = None

            # ПЕРЕДАЕМ АНАЛИЗАТОР В GameWindow через атрибут
            if hasattr(self.ui, 'game_window'):
                print(f"Найден game_window в UI, передаю анализатор...")
                if self.frequency_analisator:
                    self.ui.game_window.set_frequency_source(
                        self.frequency_analisator)
                    self.ui.game_window.exit_requested.connect(
                        lambda: self.ui.stacked_widget.setCurrentIndex(0)
                    )
            else:
                print(f"✗ game_window не найден в UI")

            # Настраиваем тунерские полосы
            self.setup_tuner_bars()

            # Настраиваем соединения кнопок
            self.setup_connections()

            # Настраиваем переключение окон
            self.setup_window_switching()

            # Таймер для обновления интерфейса тюнера
            if self.frequency_analisator:
                self.timer = QtCore.QTimer(self)
                self.timer.timeout.connect(self.update_ui)
                self.timer.start(100)  # 10 раз в секунду
                print("Таймер тюнера запущен")

        except Exception as e:
            print(f"Ошибка инициализации приложения: {e}")
            raise

    def on_account_clicked(self):
        print("[UI] Account clicked")

        try:
            # если по какой-то причине нет user_id
            if not hasattr(self, "user_id") or self.user_id is None:
                QtWidgets.QMessageBox.warning(self, "Ошибка", "Пользователь не авторизован")
                return

            dialog = TuningWindow(self.db_manager, self.user_id, self)
            dialog.exec_()

        except Exception as e:
            print(f"Ошибка открытия окна строя: {e}")

    def init_library(self):
        """
        Подключаем LibraryController к library_ui.
        Кнопка в библиотеке работает как "Назад".
        """
        self.library_controller = LibraryController(
            self.ui.library_ui,
            on_exit=lambda: self.ui.stacked_widget.setCurrentIndex(0)  # назад из разделов -> тюнер
        )

    def setup_exit_door(self):
        """
        Дверь в главном меню тюнера — это label_5 (QLabel с pixmap).
        Делаем её кликабельной: клик = выход из программы.
        """
        try:
            door = getattr(self.ui, "label_5", None)
            if door is None:
                print("[UI] label_5 (door) не найден")
                return

            # чтобы курсор показывал "можно нажать"
            door.setCursor(QtCore.Qt.PointingHandCursor)

            # делаем QLabel кликабельным
            def _door_click(event):
                QtWidgets.QApplication.quit()

            door.mousePressEvent = _door_click
            print("[UI] Door (label_5) wired to quit")

        except Exception as e:
            print(f"[UI] Ошибка привязки двери к выходу: {e}")

    def show_login(self):
        try:
            login_window = LoginWindow(self.db_manager)
            result = login_window.exec_()

            if result == QtWidgets.QDialog.Accepted:
                self.current_user = login_window.get_current_user()
                self.user_id = login_window.get_user_id()
                print(f"Пользователь авторизован: {self.current_user}")
                return True
            return False
        except Exception as e:
            print(f"Ошибка входа: {e}")
            return False

    def set_user_in_interface(self):
        if hasattr(self, 'current_user') and self.current_user:
            try:
                self.ui.Accaunt_bnt.setText(f"{self.current_user}")
                print(f"Имя пользователя установлено: {self.current_user}")
            except Exception as e:
                print(f"Ошибка установки имени пользователя: {e}")

    def setup_window_switching(self):
        self.ui.mode_list.itemClicked.connect(self.on_mode_selected)
        self.ui.library_ui.mode_list.itemClicked.connect(self.on_mode_selected)
        print("Переключение окон настроено")

    def on_mode_selected(self, item):
        mode = item.text()
        print(f"Выбран режим: {mode}")

        if mode == "Tuner":
            self.ui.stacked_widget.setCurrentIndex(0)

        elif mode == "Library":
            self.ui.stacked_widget.setCurrentIndex(1)
            # всегда показываем разделы при входе в библиотеку
            if hasattr(self, "library_controller"):
                self.library_controller.show_sections()

        elif mode == "Game":
            self.ui.stacked_widget.setCurrentIndex(2)
            if hasattr(self.ui, 'game_window'):
                if self.ui.game_window.frequency_source:
                    print("✓ GameWindow имеет доступ к анализатору")
                else:
                    print("✗ GameWindow не имеет доступа к анализатору")

    def setup_tuner_bars(self):
        try:
            self.ui.tunerBar_low.setMinimum(0)
            self.ui.tunerBar_low.setMaximum(50)
            self.ui.tunerBar_high.setMinimum(0)
            self.ui.tunerBar_high.setMaximum(50)
            print("Полосы тюнера настроены")
        except Exception as e:
            print(f"Ошибка настройки полос тюнера: {e}")

    def setup_connections(self):
        """
        pushButton (иконка сверху слева) = открыть настройки аудио
        Accaunt_bnt = открыть окно строя
        label_5 (дверь снизу) = выход
        """
        try:
            # ✅ НАСТРОЙКИ (pushButton сверху слева)
            try:
                self.ui.pushButton.clicked.disconnect()
            except Exception:
                pass
            self.ui.pushButton.clicked.connect(self.on_settings_clicked)

            # ✅ ACCOUNT
            try:
                self.ui.Accaunt_bnt.clicked.disconnect()
            except Exception:
                pass
            self.ui.Accaunt_bnt.clicked.connect(self.on_account_clicked)

            # ✅ ДВЕРЬ = ВЫХОД
            self.setup_exit_door()

            print("Соединения кнопок настроены")

        except Exception as e:
            print(f"Ошибка настройки соединений кнопок: {e}")

    def on_settings_clicked(self):
        dialog = AudioSettingsWindow(self)
        result = dialog.exec_()

        if result != QtWidgets.QDialog.Accepted:
            return

        device = dialog.get_selected_device()
        ch_index = dialog.get_selected_channel_index()

        print(f"[SETTINGS] sounddevice device={device}, channel_index={ch_index}")

        if device is None:
            return

        if getattr(self, "note_detecter", None) is None:
            self.note_detecter = NoteDetector()

        if getattr(self, "frequency_analisator", None) is None:
            self.frequency_analisator = Analisador(device=device, channel_index=ch_index)
            self.frequency_analisator.start()
        else:
            self.frequency_analisator.reconfigure(device=device, channel_index=ch_index)

        if hasattr(self.ui, "game_window"):
            self.ui.game_window.set_frequency_source(self.frequency_analisator)

    def frequency_to_cents(self, current_freq, target_freq):
        if current_freq <= 0 or target_freq <= 0:
            return 0
        try:
            ratio = current_freq / target_freq
            cents = 1200 * math.log2(ratio)
            return cents
        except:
            return 0

    def update_ui(self):
        try:
            if not self.frequency_analisator:
                return

            frequency = self.frequency_analisator.get_frequency()

            if frequency > 0:
                data = self.note_detecter.detect_full(frequency)
                if not data:
                    self.show_no_signal()
                    return

                note = data["note"]
                cents_diff = data["cents"]

                if note:
                    # cents уже корректный, с учётом октавы
                    try:
                        self.ui.label_4.setText(note)
                    except:
                        pass

                    GREEN_ZONE = 12
                    YELLOW_ZONE = 30

                    if abs(cents_diff) <= GREEN_ZONE:
                        self.update_bars(0, 0, "rgb(0, 255, 0)")
                    elif cents_diff < 0:
                        cents_value = min(50, abs(int(cents_diff)))
                        self.update_bars(
                            cents_value, 0,
                            "rgb(255, 255, 0)" if abs(cents_diff) <= YELLOW_ZONE else "rgb(255, 69, 0)"
                        )
                    else:
                        cents_value = min(50, abs(int(cents_diff)))
                        self.update_bars(
                            0, cents_value,
                            "rgb(255, 255, 0)" if abs(cents_diff) <= YELLOW_ZONE else "rgb(255, 69, 0)"
                        )
                else:
                    self.show_no_signal()
            else:
                self.show_no_signal()

        except Exception as e:
            print(f"Ошибка обновления UI тюнера: {e}")
            self.show_no_signal()

    def update_bars(self, low_value, high_value, color):
        try:
            self.ui.tunerBar_low.setValue(low_value)
            self.ui.tunerBar_high.setValue(high_value)
            self.ui.label_4.setStyleSheet(f"color: {color}; background-color: rgb(157, 157, 157); font: 20pt 'MS Serif'; border: 5px solid #00aa00;")
        except Exception as e:
            print(f"Ошибка обновления полос: {e}")

    def show_no_signal(self):
        try:
            self.ui.label_4.setText("--")
            self.ui.tunerBar_low.setValue(0)
            self.ui.tunerBar_high.setValue(0)
            self.ui.label_4.setStyleSheet("color: rgb(0, 170, 0); background-color: rgb(157, 157, 157); font: 20pt 'MS Serif'; border: 5px solid #00aa00;")
        except Exception as e:
            print(f"Ошибка показа 'нет сигнала': {e}")

    def closeEvent(self, event):
        try:
            if self.frequency_analisator:
                print("Останавливаю анализ частоты...")
                self.frequency_analisator.stop_analysis()
            if hasattr(self, 'timer'):
                print("Останавливаю таймер...")
                self.timer.stop()
        except Exception as e:
            print(f"Ошибка при закрытии: {e}")
        event.accept()


def main():
    try:
        app = QtWidgets.QApplication(sys.argv)
        app.setApplicationName("Гитарный тюнер")
        print("Приложение запускается...")

        window = GuitarTunerApp()
        window.show()
        print("Окно показано")

        result = app.exec_()
        print(f"Приложение завершено с кодом: {result}")
        sys.exit(result)

    except Exception as e:
        print(f"Критическая ошибка при запуске: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
