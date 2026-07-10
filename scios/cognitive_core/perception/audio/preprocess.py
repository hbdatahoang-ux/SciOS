# preprocess.py
# Audio Preprocessor cho SciOS Cognitive Core

import numpy as np
from typing import Dict

class AudioPreprocessor:
    """
    AudioPreprocessor chịu trách nhiệm xử lý tín hiệu âm thanh:
    - Resample về tần số chuẩn (ví dụ 16kHz)
    - Normalize biên độ
    - Noise reduction (có thể mở rộng)
    """

    def __init__(self, target_rate: int = 16000, normalize: bool = True):
        self.target_rate = target_rate
        self.normalize = normalize

    def resample(self, audio: np.ndarray, original_rate: int) -> np.ndarray:
        """Resample tín hiệu về target_rate (placeholder đơn giản)."""
        factor = int(original_rate / self.target_rate)
        return audio[::factor] if factor > 1 else audio

    def normalize_audio(self, audio: np.ndarray) -> np.ndarray:
        """Chuẩn hóa biên độ tín hiệu."""
        if not self.normalize:
            return audio
        return audio / np.max(np.abs(audio))

    def preprocess(self, audio: np.ndarray, sample_rate: int) -> Dict:
        """Thực hiện toàn bộ pipeline preprocess."""
        resampled = self.resample(audio, sample_rate)
        normalized = self.normalize_audio(resampled)
        return {"preprocessed_audio": normalized, "sample_rate": self.target_rate}
