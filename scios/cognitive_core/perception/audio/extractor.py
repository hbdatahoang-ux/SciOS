# extractor.py
# Audio Feature Extractor cho SciOS Cognitive Core

import numpy as np
import librosa
from typing import Dict

class AudioExtractor:
    """
    AudioExtractor chịu trách nhiệm trích xuất đặc trưng từ tín hiệu âm thanh:
    - MFCC (Mel-Frequency Cepstral Coefficients)
    - Spectrogram
    - Pitch (cao độ)
    """

    def __init__(self, method: str = "mfcc", n_mfcc: int = 13):
        self.method = method
        self.n_mfcc = n_mfcc

    def extract_features(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Trích xuất đặc trưng từ tín hiệu âm thanh.

        Args:
            audio (np.ndarray): tín hiệu âm thanh
            sample_rate (int): tần số lấy mẫu

        Returns:
            np.ndarray: đặc trưng đã trích xuất
        """
        if self.method == "mfcc":
            mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=self.n_mfcc)
            return np.mean(mfccs.T, axis=0)
        elif self.method == "spectrogram":
            spec = np.abs(librosa.stft(audio))
            return np.mean(spec, axis=1)
        elif self.method == "pitch":
            pitches, magnitudes = librosa.piptrack(y=audio, sr=sample_rate)
            pitch_values = pitches[magnitudes > np.median(magnitudes)]
            return np.array([np.mean(pitch_values)]) if len(pitch_values) > 0 else np.array([0.0])
        else:
            return np.array([])

    def to_dict(self, audio: np.ndarray, sample_rate: int) -> Dict:
        """
        Chuẩn hóa output dưới dạng dict.
        """
        features = self.extract_features(audio, sample_rate)
        return {"audio_features": features.tolist()}
