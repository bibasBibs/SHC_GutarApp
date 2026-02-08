from PyQt5 import QtWidgets
from audio_devices import AudioDeviceManager


class SettingsWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Audio Settings")
        self.setFixedSize(400, 300)

        self.manager = AudioDeviceManager()

        layout = QtWidgets.QVBoxLayout(self)

        self.device_combo = QtWidgets.QComboBox()
        layout.addWidget(QtWidgets.QLabel("Input device:"))
        layout.addWidget(self.device_combo)

        self.reload_btn = QtWidgets.QPushButton("Reload devices")
        layout.addWidget(self.reload_btn)

        self.ok_btn = QtWidgets.QPushButton("Apply")
        layout.addWidget(self.ok_btn)

        self.reload_btn.clicked.connect(self.load_devices)
        self.ok_btn.clicked.connect(self.accept)

        self.load_devices()

    def load_devices(self):
        self.device_combo.clear()

        for d in self.manager.list_input_devices():
            text = f"{d['name']} [{d['hostApi']}]"
            self.device_combo.addItem(text, d)

    def get_selected_device(self):
        return self.device_combo.currentData()
