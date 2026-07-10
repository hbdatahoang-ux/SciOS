# test_pipeline.py
# Integration tests cho SciOS Cognitive Core - Perception Pipeline

import unittest
import numpy as np

from scios.cognitive_core.perception.video.loader import VideoLoader
from scios.cognitive_core.perception.video.frames import VideoFrames
from scios.cognitive_core.perception.video.preprocess import VideoPreprocessor
from scios.cognitive_core.perception.video.extractor import VideoExtractor
from scios.cognitive_core.perception.video.encoder import VideoEncoder

from scios.cognitive_core.perception.documents.markdown import MarkdownProcessor
from scios.cognitive_core.perception.sensors.simulator import SensorSimulator

class TestVideoPipeline(unittest.TestCase):
    def test_video_flow(self):
        loader = VideoLoader()
        frames_handler = VideoFrames(step=5)
        preprocessor = VideoPreprocessor(target_size=(64, 64), target_fps=10)
        extractor = VideoExtractor(method="histogram")
        encoder = VideoEncoder(method="simple")

        # giả lập: thay vì mở file thật, tạo frame giả
        frames = [np.random.randint(0, 255, (64, 64, 3), dtype=np.uint8) for _ in range(5)]
        processed = preprocessor.preprocess(frames, original_fps=30)
        features = extractor.extract_features(processed["frames"])
        embedding = encoder.encode(processed["frames"])

        self.assertIsInstance(features, np.ndarray)
        self.assertEqual(len(embedding), 2)

class TestDocumentPipeline(unittest.TestCase):
    def test_markdown_flow(self):
        processor = MarkdownProcessor()
        md_text = "# Hello\nThis is a test."
        html = processor.to_html(md_text)
        plain = processor.to_text(md_text)
        self.assertIn("Hello", plain)
        self.assertIn("<h1>", html)

class TestSensorPipeline(unittest.TestCase):
    def test_sensor_flow(self):
        sim = SensorSimulator(sensor_type="temperature", interval=0.1)
        sim.start()
        data = sim.read()
        sim.stop()
        self.assertIn("data", data)
        self.assertEqual(data["sensor_type"], "temperature")

if __name__ == "__main__":
    unittest.main()
