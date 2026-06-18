import numpy as np
from pydub import AudioSegment
from pydub.playback import play

def create_sine_wave(frequency, duration_ms, sample_rate=44100):
    """指定した周波数・長さの正弦波を生成する"""
    num_samples = int(sample_rate * duration_ms / 1000)
    t = np.linspace(0, duration_ms / 1000, num_samples)
    wave = np.sin(2 * np.pi * frequency * t)
    wave = (wave * 32767).astype(np.int16)
    audio = AudioSegment(wave.tobytes(),
                         frame_rate=sample_rate,
                         sample_width=2,
                         channels=1)
    return audio

# ラの音（440Hz）を1秒鳴らす
la_sound = create_sine_wave(440, 1000)
play(la_sound)