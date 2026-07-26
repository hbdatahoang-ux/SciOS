from .base import BaseExporter


class MemoryExporter(BaseExporter):
    """
    In-memory trace exporter.
    """

    def __init__(self):
        self.records = []

    def export(self, data):
        self.records.append(data)
        return data

    def clear(self):
        self.records.clear()

    def items(self):
        return list(self.records)