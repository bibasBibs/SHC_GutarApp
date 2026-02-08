# note_detecter.py
import numpy as np

class NoteDetector:
    def __init__(self):
        # все ноты с частотой
        self.guitar_frequencies = {
            'E2': 82.41, 'F2': 87.31, 'F#2': 92.50, 'G2': 98.00,
            'G#2': 103.83, 'A2': 110.00, 'A#2': 116.54, 'B2': 123.47,
            'C3': 130.81, 'C#3': 138.59, 'D3': 146.83, 'D#3': 155.56,
            'E3': 164.81, 'F3': 174.61, 'F#3': 185.00, 'G3': 196.00,
            'G#3': 207.65, 'A3': 220.00, 'A#3': 233.08, 'B3': 246.94,
            'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13,
            'E4': 329.63, 'F4': 349.23, 'F#4': 369.99, 'G4': 392.00,
            'G#4': 415.30, 'A4': 440.00, 'A#4': 466.16, 'B4': 493.88,
            'C5': 523.25, 'C#5': 554.37, 'D5': 587.33, 'D#5': 622.25,
            'E5': 659.25
        }

    def detect(self, freq):
        if freq <= 0:
            return None
        # ищем ближайшую ноту с проверкой ±1 октаву
        min_diff = float('inf')
        closest_note = None
        for note, note_freq in self.guitar_frequencies.items():
            # коррекция октав
            while note_freq * 2 < freq:
                note_freq *= 2
            while note_freq / 2 > freq:
                note_freq /= 2

            diff = abs(freq - note_freq)
            if diff < min_diff and diff < 10:  # tolerance в Гц
                min_diff = diff
                closest_note = note
        return closest_note

    def get_target_frequency_for_measured(self, note: str, measured_freq: float) -> float:
        """
        Возвращает частоту этой ноты, подогнанную по октаве так,
        чтобы она была ближе всего к measured_freq.
        """
        if not note or measured_freq <= 0:
            return 0.0

        base = float(self.guitar_frequencies.get(note, 0.0))
        if base <= 0:
            return 0.0

        f = base
        # подгоняем по октаве к измеренной частоте
        while f * 2.0 <= measured_freq:
            f *= 2.0
        while f / 2.0 >= measured_freq:
            f /= 2.0

        # теперь f рядом, но бывает что соседняя октава ещё ближе
        cand = [f, f * 2.0, f / 2.0]
        cand = [c for c in cand if c > 0]
        best = min(cand, key=lambda c: abs(measured_freq - c))
        return float(best)

    def detect_full(self, freq):
        """
        Полная детекция для тюнера.
        Возвращает dict: {"note": str, "cents": float, "confidence": float}
        """
        note = self.detect(freq)
        if not note:
            return None

        target = self.get_target_frequency_for_measured(note, float(freq))
        if target <= 0:
            return None

        cents = 1200 * np.log2(float(freq) / float(target))

        confidence = max(0.0, 1.0 - (abs(cents) / 50.0))
        confidence = min(1.0, confidence)

        return {"note": note, "cents": float(cents), "confidence": float(confidence)}

    def detect_for_game(self, freq):
        """
        Для игры используем тот же результат, что и для тюнера:
        ближайшая нота + cents.
        """
        return self.detect_full(freq)
