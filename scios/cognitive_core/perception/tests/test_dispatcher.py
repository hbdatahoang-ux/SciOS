# test_dispatcher.py
# Unit tests cho SciOS Cognitive Core - Dispatcher

import unittest
from scios.cognitive_core.dispatcher import Dispatcher
from scios.cognitive_core.perception.video.loader import VideoLoader
from scios.cognitive_core.perception.documents.pdf import PDFProcessor
from scios.cognitive_core.perception.sensors.simulator import SensorSimulator

class TestDispatcher(unittest.TestCase):
    def setUp(self):
        self.dispatcher = Dispatcher()

    def test_dispatch_video(self):
        loader = VideoLoader()
        video_dict = loader.to_dict("example.mp4", source_type="file")
        result = self.dispatcher.route("video", video_dict)
        self.assertIn("frames", result)

    def test_dispatch_pdf(self):
        processor = PDFProcessor()
        pdf_dict = {"texts": ["Hello world"], "metadata": {"page_count": 1}}
        result = self.dispatcher.route("documents", pdf_dict)
        self.assertIn("texts", result)

    def test_dispatch_sensor(self):
        sim = SensorSimulator(sensor_type="temperature")
        sim.start()
        sensor_data = sim.read()
        sim.stop()
        result = self.dispatcher.route("sensors", sensor_data)
        self.assertIn("data", result)

    def test_invalid_modality(self):
        with self.assertRaises(ValueError):
            self.dispatcher.route("unknown", {"foo": "bar"})

if __name__ == "__main__":
    unittest.main()
