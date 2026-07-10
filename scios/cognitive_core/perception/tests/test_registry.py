# test_registry.py
# Unit tests cho SciOS Cognitive Core - Registry

import unittest
from scios.cognitive_core.registry import Registry
from scios.cognitive_core.perception.video.preprocess import VideoPreprocessor
from scios.cognitive_core.perception.documents.markdown import MarkdownProcessor
from scios.cognitive_core.perception.sensors.simulator import SensorSimulator

class TestRegistry(unittest.TestCase):
    def setUp(self):
        self.registry = Registry()

    def test_register_and_get_video(self):
        vp = VideoPreprocessor(target_size=(64, 64))
        self.registry.register("video_preprocessor", vp)
        retrieved = self.registry.get("video_preprocessor")
        self.assertIsInstance(retrieved, VideoPreprocessor)

    def test_register_and_get_document(self):
        md = MarkdownProcessor()
        self.registry.register("markdown_processor", md)
        retrieved = self.registry.get("markdown_processor")
        self.assertIsInstance(retrieved, MarkdownProcessor)

    def test_register_and_get_sensor(self):
        sim = SensorSimulator(sensor_type="temperature")
        self.registry.register("sensor_simulator", sim)
        retrieved = self.registry.get("sensor_simulator")
        self.assertIsInstance(retrieved, SensorSimulator)

    def test_invalid_key(self):
        with self.assertRaises(KeyError):
            self.registry.get("non_existent")

if __name__ == "__main__":
    unittest.main()
