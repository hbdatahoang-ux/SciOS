# test_perception.py
# Unit tests cho SciOS Cognitive Core - Perception modules

import unittest
import numpy as np

from scios.cognitive_core.perception.video.encoder import VideoEncoder
from scios.cognitive_core.perception.documents.pdf import PDFProcessor
from scios.cognitive_core.perception.sensors.simulator import SensorSimulator

class TestVideoEncoder(unittest.TestCase):
    def test_encode_simple(self):
        frames = np.random.randint(0, 255, (5, 64, 64, 3), dtype=np.uint8)
        encoder = VideoEncoder(method="simple")
        embedding = encoder.encode(frames)
        self.assertEqual(len(embedding), 2)  # mean + std

class TestPDFProcessor(unittest.TestCase):
    def test_load_pdf(self):
        processor = PDFProcessor()
        # giả lập: thay vì mở file thật, kiểm tra interface
        self.assertTrue(hasattr(processor, "to_dict"))

class TestSensorSimulator(unittest.TestCase):
    def test_temperature_simulation(self):
        sim = SensorSimulator(sensor_type="temperature", interval=0.1)
        sim.start()
        data = sim.read()
        sim.stop()
        self.assertIn("data", data)
        self.assertEqual(data["sensor_type"], "temperature")

if __name__ == "__main__":
    unittest.main()
