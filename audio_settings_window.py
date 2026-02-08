# audio_settings_window.py
from PyQt5 import QtWidgets


class AudioSettingsWindow(QtWidgets.QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Audio Settings (sounddevice)")
        self.setFixedSize(520, 260)

        self.selected_device = None
        self.selected_channel_index = 0  # 0 -> Input 1, 1 -> Input 2

        layout = QtWidgets.QVBoxLayout(self)

        layout.addWidget(QtWidgets.QLabel("Input device"))
        self.device_combo = QtWidgets.QComboBox()
        layout.addWidget(self.device_combo)

        layout.addWidget(QtWidgets.QLabel("Guitar input (channel)"))
        self.channel_combo = QtWidgets.QComboBox()
        layout.addWidget(self.channel_combo)

        btn_layout = QtWidgets.QHBoxLayout()
        self.apply_btn = QtWidgets.QPushButton("Apply")
        self.cancel_btn = QtWidgets.QPushButton("Cancel")
        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.apply_btn.clicked.connect(self.apply)
        self.cancel_btn.clicked.connect(self.reject)

        self.device_combo.currentIndexChanged.connect(self._on_device_changed)

        self._load_devices()
        self._on_device_changed()

    def _load_devices(self):
        import sounddevice as sd

        self.device_combo.clear()

        try:
            devices = sd.query_devices()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Audio error", f"Cannot query devices:\n{e}")
            return

        # 1) пробуем показать только WASAPI input-девайсы
        added = 0
        for idx, d in enumerate(devices):
            max_in = int(d.get("max_input_channels", 0) or 0)
            if max_in <= 0:
                continue

            hostapi_idx = d.get("hostapi", None)
            try:
                api_name = sd.query_hostapis(hostapi_idx)["name"] if hostapi_idx is not None else ""
            except Exception:
                api_name = ""

            if "WASAPI" not in api_name:
                continue

            name = (d.get("name", f"Device {idx}") or f"Device {idx}").strip()
            self.device_combo.addItem(f"{name} [{api_name}] (inputs={max_in}) (id={idx})", idx)
            added += 1

        # 2) если WASAPI не найден — добавляем любые input-девайсы
        if added == 0:
            for idx, d in enumerate(devices):
                max_in = int(d.get("max_input_channels", 0) or 0)
                if max_in <= 0:
                    continue
                name = (d.get("name", f"Device {idx}") or f"Device {idx}").strip()
                self.device_combo.addItem(f"{name} (inputs={max_in}) (id={idx})", idx)

        if self.device_combo.count() > 0:
            self.selected_device = self.device_combo.currentData()

    def _on_device_changed(self):
        import sounddevice as sd

        dev = self.device_combo.currentData()
        self.selected_device = dev

        self.channel_combo.clear()

        if dev is None:
            self.channel_combo.setEnabled(False)
            self.channel_combo.addItem("Input 1", 0)
            self.selected_channel_index = 0
            return

        try:
            info = sd.query_devices(dev, "input")
            max_in = int(info.get("max_input_channels", 0) or 0)
        except Exception:
            max_in = 0

        max_in = max(1, max_in)

        for ch in range(max_in):
            self.channel_combo.addItem(f"Input {ch + 1}", ch)

        self.channel_combo.setEnabled(max_in >= 2)
        self.channel_combo.setCurrentIndex(0)
        self.selected_channel_index = 0

    def apply(self):
        self.selected_device = self.device_combo.currentData()
        self.selected_channel_index = int(self.channel_combo.currentIndex())  # 0 или 1
        self.accept()

    def get_selected_device(self):
        return self.selected_device

    def get_selected_channel_index(self):
        return int(self.selected_channel_index)
