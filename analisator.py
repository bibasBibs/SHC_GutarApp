# analisator.py
import pyaudio
import numpy as np
import threading
import time

class Analisador:
    def __init__(self, device=None, channel_index=0, volume_threshold=0.02, sample_rate=None, blocksize=4096):
        import threading

        self.device = device
        self.channel_index = int(channel_index)
        self.volume_threshold = float(volume_threshold)

        self.sample_rate = int(sample_rate) if sample_rate else None

        # Блок побольше для стабильности
        self.blocksize = int(blocksize) if blocksize else 4096

        self._frequency = 0.0
        self._lock = threading.Lock()

        self._stream = None
        self._running = False
        self._stream_lock = threading.Lock()

        # Стабилизация/кандидаты
        self._candidate_note_freq = 0.0
        self._candidate_hits = 0

        self._init_buffers()

    def _fft_peak_at(self, mono, sr, target_freq, bandwidth=8.0):
        """
        Возвращает максимальную амплитуду FFT в окне [target_freq-bandwidth, target_freq+bandwidth].
        mono: np.float32
        """
        import numpy as np

        f = float(target_freq)
        if f <= 0:
            return 0.0

        x = mono.astype(np.float32)
        n = x.size
        if n < 2048:
            return 0.0

        x = x - float(np.mean(x))
        xw = x * np.hanning(n)
        spec = np.fft.rfft(xw)
        mags = np.abs(spec)
        freqs = np.fft.rfftfreq(n, 1.0 / sr)

        lo = max(0.0, f - float(bandwidth))
        hi = f + float(bandwidth)
        mask = (freqs >= lo) & (freqs <= hi)
        if not np.any(mask):
            return 0.0

        return float(np.max(mags[mask]))

    def _octave_correct_by_harmonics(self, mono, sr, f_candidate, fmin=70.0, fmax=1200.0):
        """
        Возвращает частоту, скорректированную от октавных ошибок:
        выбираем среди f, f/2, 2f ту, у которой лучше "гармонический скор".
        """
        f = float(f_candidate)
        if f <= 0:
            return 0.0

        cands = []

        # f
        if fmin <= f <= fmax:
            cands.append(f)

        # f/2
        if fmin <= f / 2.0 <= fmax:
            cands.append(f / 2.0)

        # 2f
        if fmin <= f * 2.0 <= fmax:
            cands.append(f * 2.0)

        if not cands:
            return f

        def score(freq):
            # Смотрим пик на freq и на 2*freq (гармоника)
            p1 = self._fft_peak_at(mono, sr, freq, bandwidth=10.0)
            p2 = self._fft_peak_at(mono, sr, freq * 2.0, bandwidth=10.0) if freq * 2.0 <= fmax else 0.0
            p3 = self._fft_peak_at(mono, sr, freq * 3.0, bandwidth=12.0) if freq * 3.0 <= fmax else 0.0

            # У фундамента обычно есть и гармоники, но не должно быть так,
            # чтобы "фундамент" был слабым, а гармоники сильнее в разы.
            # Поэтому даём вес фундаменту, плюс небольшая поддержка гармоник.
            return (1.00 * p1) + (0.35 * p2) + (0.15 * p3)

        best_f = cands[0]
        best_s = score(best_f)

        for cf in cands[1:]:
            s = score(cf)
            if s > best_s:
                best_s = s
                best_f = cf

        return float(best_f)

    def _get_ring_window(self):
        import numpy as np

        # Достаточно, чтобы накопилось хотя бы 75% окна
        if not self._ring_filled and self._ring_pos < int(self._analysis_window * 0.75):
            return None

        w = self._analysis_window
        pos = self._ring_pos

        if pos == 0:
            return self._ring.copy()

        return np.concatenate((self._ring[pos:], self._ring[:pos])).astype(np.float32)

    def _push_ring(self, mono):
        import numpy as np

        x = mono.astype(np.float32)
        n = x.size
        if n == 0:
            return

        # пишем в кольцо
        w = self._analysis_window
        pos = self._ring_pos

        if n >= w:
            # если пришло больше окна — берём хвост
            self._ring[:] = x[-w:]
            self._ring_pos = 0
            self._ring_filled = True
            return

        end = pos + n
        if end < w:
            self._ring[pos:end] = x
            self._ring_pos = end
        else:
            first = w - pos
            self._ring[pos:] = x[:first]
            rest = n - first
            self._ring[:rest] = x[first:]
            self._ring_pos = rest
            self._ring_filled = True

    def _refine_fft_near(self, mono, sr, center_freq, bandwidth=40.0):
        import numpy as np

        x = mono.astype(np.float32)
        n = x.size
        if n < 2048 or center_freq <= 0:
            return 0.0

        # окно + FFT
        x = x - float(np.mean(x))
        xw = x * np.hanning(n)
        fft = np.fft.rfft(xw)
        mags = np.abs(fft)
        freqs = np.fft.rfftfreq(n, 1.0 / sr)

        lo = max(0.0, center_freq - bandwidth)
        hi = center_freq + bandwidth

        mask = (freqs >= lo) & (freqs <= hi)
        if not np.any(mask):
            return 0.0

        idx = int(np.argmax(mags[mask]))
        f0 = float(freqs[mask][idx])

        # параболическая интерполяция по спектру (если возможно)
        masked_idxs = np.where(mask)[0]
        k = masked_idxs[idx]
        if 1 <= k < len(mags) - 1:
            a, b, c = float(mags[k - 1]), float(mags[k]), float(mags[k + 1])
            denom = (a - 2 * b + c)
            if abs(denom) > 1e-12:
                delta = 0.5 * (a - c) / denom
                f0 = float(freqs[k] + delta * (freqs[1] - freqs[0]))

        return f0

    def _init_buffers(self):
        import numpy as np

        # Для точности достаточно 8192..16384.
        # 8192 быстрее "оживает" и стабильно работает на верхах при 48kHz.
        self._analysis_window = 8192
        self._ring = np.zeros(self._analysis_window, dtype=np.float32)
        self._ring_pos = 0
        self._ring_filled = False

    def start(self):
        with self._stream_lock:
            if self._running:
                return
            self._open_stream()
            self._running = True

    def _open_stream(self):
        import sounddevice as sd
        import numpy as np

        info = sd.query_devices(self.device, 'input')
        sr = int(self.sample_rate) if self.sample_rate else int(info.get('default_samplerate', 48000))

        max_in = int(info.get('max_input_channels', 1) or 1)

        # Открываем только столько каналов, сколько реально нужно:
        # если пользователь выбрал Input 2 (channel_index=1), нужно минимум 2 канала
        need_channels = min(max_in, max(1, int(self.channel_index) + 1))

        # Если скорость не важна — увеличим blocksize для устойчивости на верхах
        if not getattr(self, "blocksize", None):
            self.blocksize = 4096
        else:
            self.blocksize = int(self.blocksize)

        # Параметры устойчивости: делаем мягче, чтобы "ожило"
        conf_min_low = 0.45
        conf_min_high = 0.55
        split_high_hz = 350.0

        # ВАЖНО: если не прошли проверки — явно ставим 0, чтобы UI не "зависал" на старом
        def callback(indata, frames, time_info, status):
            try:
                if indata is None or indata.size == 0:
                    return

                # indata: (frames, channels)
                if indata.ndim == 1:
                    mono = indata.astype(np.float32)
                else:
                    ch = indata.shape[1]
                    idx = min(max(int(self.channel_index), 0), ch - 1)
                    mono = indata[:, idx].astype(np.float32)

                # noise gate
                if float(np.max(np.abs(mono))) < self.volume_threshold:
                    with self._lock:
                        self._frequency = 0.0
                    self._candidate_hits = 0
                    return

                # копим кольцо
                self._push_ring(mono)
                window = self._get_ring_window()
                if window is None:
                    return

                # 1) YIN
                raw_freq, conf = self._detect_pitch_yin(window, sr)
                if raw_freq <= 0:
                    with self._lock:
                        self._frequency = 0.0
                    self._candidate_hits = 0
                    return

                # 2) FFT уточнение рядом с кандидатом (но не душим, если FFT не сработал)
                refined = self._refine_fft_near(window, sr, raw_freq,
                                                bandwidth=60.0 if raw_freq >= split_high_hz else 40.0)
                freq = refined if refined > 0 else raw_freq

                # 3) стабилизация
                stable = self._stabilize_frequency(freq)
                if stable <= 0:
                    with self._lock:
                        self._frequency = 0.0
                    self._candidate_hits = 0
                    return

                # порог уверенности (мягкий)
                conf_min = conf_min_high if stable >= split_high_hz else conf_min_low
                if conf < conf_min:
                    with self._lock:
                        self._frequency = 0.0
                    self._candidate_hits = 0
                    return

                # гистерезис: меньше подтверждений, чтобы не "молчало"
                if self._candidate_note_freq <= 0:
                    self._candidate_note_freq = stable
                    self._candidate_hits = 1
                else:
                    base = self._candidate_note_freq
                    tol = 0.03 if stable >= split_high_hz else 0.04
                    if base > 0 and abs(stable - base) / base < tol:
                        self._candidate_hits += 1
                        self._candidate_note_freq = (base * 0.8) + (stable * 0.2)
                    else:
                        self._candidate_note_freq = stable
                        self._candidate_hits = 1

                need_hits = 2 if stable >= split_high_hz else 2
                if self._candidate_hits >= need_hits:
                    with self._lock:
                        self._frequency = float(self._candidate_note_freq)

            except Exception:
                return

        self._stream = sd.InputStream(
            device=self.device,
            channels=need_channels,
            samplerate=sr,
            blocksize=int(self.blocksize),
            dtype='float32',
            callback=callback
        )
        self._stream.start()

    def _stabilize_frequency(self, raw_freq):
        """
        Простая стабилизация:
        - хранит историю
        - берет медиану
        - отбрасывает выбросы, сильно отличающиеся от медианы
        """
        import numpy as np

        if not hasattr(self, "_freq_hist"):
            self._freq_hist = []
        if not hasattr(self, "_last_good_freq"):
            self._last_good_freq = 0.0

        f = float(raw_freq)

        if f <= 0:
            # если тишина — не рушим историю резко
            return 0.0

        self._freq_hist.append(f)
        if len(self._freq_hist) > 7:
            self._freq_hist.pop(0)

        med = float(np.median(self._freq_hist))

        # Если текущая частота слишком далеко от медианы — считаем выбросом
        # (15% — хороший старт для гитары)
        if med > 0 and abs(f - med) / med > 0.15:
            f = med

        # Мягко ограничим скачок относительно последнего принятого значения
        if self._last_good_freq > 0:
            if abs(f - self._last_good_freq) / self._last_good_freq > 0.20:
                f = med

        self._last_good_freq = float(f)
        return float(f)

    def _detect_pitch_yin(self, mono, sr, fmin=70.0, fmax=1200.0):
        """
        Улучшенный YIN: возвращает (freq, confidence)
        confidence ~ 0..1 (выше = лучше). Если уверенности нет -> (0.0, 0.0)
        """
        import numpy as np

        x = mono.astype(np.float32)
        n = x.size
        if n < 512:
            return 0.0, 0.0

        # Noise gate
        if float(np.max(np.abs(x))) < self.volume_threshold:
            return 0.0, 0.0

        # DC remove
        x = x - float(np.mean(x))

        tau_min = int(sr / fmax)
        tau_max = int(sr / fmin)
        tau_max = min(tau_max, n // 2)
        if tau_max <= tau_min + 2:
            return 0.0, 0.0

        d = np.zeros(tau_max + 1, dtype=np.float32)
        for tau in range(1, tau_max + 1):
            diff = x[:-tau] - x[tau:]
            d[tau] = float(np.dot(diff, diff))

        cmndf = np.zeros_like(d)
        cmndf[0] = 1.0
        running_sum = 0.0
        for tau in range(1, tau_max + 1):
            running_sum += float(d[tau])
            cmndf[tau] = d[tau] * tau / running_sum if running_sum > 0 else 1.0

        # Чем меньше cmndf в минимуме — тем лучше период
        threshold = 0.12
        tau = 0
        for t in range(tau_min, tau_max):
            if cmndf[t] < threshold:
                while t + 1 <= tau_max and cmndf[t + 1] < cmndf[t]:
                    t += 1
                tau = t
                break

        if tau == 0:
            tau = int(np.argmin(cmndf[tau_min:tau_max]) + tau_min)

        # confidence из качества минимума
        best = float(cmndf[tau]) if 0 <= tau < len(cmndf) else 1.0
        confidence = max(0.0, min(1.0, 1.0 - best))  # 0..1

        # Если минимум плохой — не принимаем
        if best > 0.30:  # можно подстроить 0.25..0.35
            return 0.0, 0.0

        # Интерполяция
        if 1 <= tau < tau_max:
            y0, y1, y2 = float(cmndf[tau - 1]), float(cmndf[tau]), float(cmndf[tau + 1])
            denom = (y0 - 2.0 * y1 + y2)
            if abs(denom) > 1e-12:
                better_tau = tau + 0.5 * (y0 - y2) / denom
            else:
                better_tau = float(tau)
        else:
            better_tau = float(tau)

        if better_tau <= 0:
            return 0.0, 0.0

        freq = float(sr / better_tau)
        if freq < fmin or freq > fmax:
            return 0.0, 0.0

        return freq, confidence

    def _close_stream(self):
        try:
            if self.stream is not None:
                try:
                    self.stream.abort_stream()
                except Exception:
                    pass
                try:
                    if self.stream.is_active():
                        self.stream.stop_stream()
                except Exception:
                    pass
                try:
                    self.stream.close()
                except Exception:
                    pass
        finally:
            self.stream = None

    def request_device_change(self, device_index, sample_rate=None):
        """
        Просим анализатор переключиться на другое устройство.
        Важно: stream будет закрыт/открыт ВНУТРИ потока анализатора, а не из UI.
        """
        with self._switch_lock:
            self._pending_device_index = int(device_index) if device_index is not None else None
            self._pending_sample_rate = int(sample_rate) if sample_rate else None

        self._switch_requested.set()

        # Разбудим read(), чтобы переключение произошло быстро
        try:
            if self.stream is not None:
                self.stream.abort_stream()
        except Exception:
            pass

    def reconfigure(self, device=None, channel_index=0, sample_rate=None, blocksize=None):
        with self._stream_lock:
            self.device = device
            self.channel_index = int(channel_index)
            if sample_rate:
                self.sample_rate = int(sample_rate)
            if blocksize:
                self.blocksize = int(blocksize)

            was_running = bool(self._running)

            # 1) аккуратно остановим текущий stream
            old = self._stream
            self._stream = None

            if old is not None:
                try:
                    # abort безопаснее, чем stop, если callback в процессе
                    try:
                        old.abort()
                    except Exception:
                        pass
                    try:
                        old.stop()
                    except Exception:
                        pass
                    try:
                        old.close()
                    except Exception:
                        pass
                except Exception:
                    pass

            # 2) сбросим внутреннюю стабилизацию, чтобы не "тащить хвост" старого устройства
            self._candidate_note_freq = 0.0
            self._candidate_hits = 0
            if hasattr(self, "_freq_hist"):
                self._freq_hist = []
            if hasattr(self, "_last_good_freq"):
                self._last_good_freq = 0.0
            self._init_buffers()
            with self._lock:
                self._frequency = 0.0

            # 3) откроем заново, если анализатор был запущен
            if was_running:
                self._open_stream()

    def stop_analysis(self):
        with self._stream_lock:
            self._running = False
            try:
                if self._stream is not None:
                    try:
                        self._stream.stop()
                    except Exception:
                        pass
                    try:
                        self._stream.close()
                    except Exception:
                        pass
            finally:
                self._stream = None

        with self._lock:
            self._frequency = 0.0

    def get_frequency(self):
        with self._lock:
            return float(self._frequency)

    # ================= INTERNAL =================
    def _loop(self):
        buffer_history = []
        history_len = 3

        while not self._stop_event.is_set():
            # Обработка запроса на переключение устройства (внутри этого потока!)
            if self._switch_requested.is_set():
                self._switch_requested.clear()

                with self._switch_lock:
                    new_idx = self._pending_device_index
                    new_sr = self._pending_sample_rate

                try:
                    self._close_stream()
                except Exception:
                    pass

                if new_idx is not None:
                    try:
                        self._open_stream(new_idx, new_sr or self.SAMPLE_RATE)
                    except Exception:
                        # Если открыть не удалось — остаёмся без потока, частота=0
                        with self._lock:
                            self._frequency = 0.0
                        continue

            # Если потока нет — ждём
            if self.stream is None:
                time.sleep(0.05)
                continue

            # Чтение аудио
            try:
                data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            except Exception:
                # если нас останавливают — выходим
                if self._stop_event.is_set():
                    break
                # иначе пробуем дальше (или ждём)
                time.sleep(0.01)
                continue

            if self._stop_event.is_set():
                break

            # Анализ частоты (твоя логика)
            try:
                audio = np.frombuffer(data, dtype=np.int16).astype(np.float32)

                if np.max(np.abs(audio)) < self.volume_threshold:
                    freq = 0.0
                else:
                    audio -= np.mean(audio)
                    windowed = audio * np.hanning(len(audio))
                    fft = np.fft.rfft(windowed)
                    mags = np.abs(fft)
                    freqs = np.fft.rfftfreq(len(windowed), 1 / self.SAMPLE_RATE)
                    mask = (freqs > 70) & (freqs < 1200)
                    if np.any(mask):
                        freq = freqs[mask][np.argmax(mags[mask])]
                    else:
                        freq = 0.0

                buffer_history.append(freq)
                if len(buffer_history) > history_len:
                    buffer_history.pop(0)

                smooth_freq = float(np.mean(buffer_history))

                with self._lock:
                    self._frequency = smooth_freq

            except Exception:
                continue
