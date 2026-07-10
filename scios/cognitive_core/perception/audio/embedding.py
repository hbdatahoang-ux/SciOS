# embedding.py
# Audio Embedding cho SciOS Cognitive Core

import numpy as np
from typing import Dict

class AudioEmbedder:
    """
    AudioEmbedder chịu trách nhiệm chuyển tín hiệu âm thanh thành embedding vector.
    Có thể mở rộng bằng mô hình học sâu (Wav2Vec2, Whisper, HuBERT).
    """

    def __init__(self, method: str = "mfcc"):
        self.method = method

    def compute_embedding(self, audio: np.ndarray, sample_rate: int) -> np.ndarray:
        """
        Tính toán embedding từ tín hiệu âm thanh.

        Args:
            audio (np.ndarray): tín hiệu âm thanh
            sample_rate (int): tần số lấy mẫu

        Returns:
            np.ndarray: vector embedding
        """
        if self.method == "mfcc":
            # Placeholder: embedding đơn giản dựa trên mean & std
            mean = np.mean(audio)
            std = np.std(audio)
            length = len(audio) / sample_rate
            return np.array([mean, std, length])
        else:
            # Có thể mở rộng sang các phương pháp khác
            return np.array([0.0])

    def to_dict(self, audio: np.ndarray, sample_rate: int) -> Dict:
        """
        Chuẩn hóa output dưới dạng dict.
        """
        embedding = self.compute_embedding(audio, sample_rate)
        return {"audio_embedding": embedding.tolist()}
