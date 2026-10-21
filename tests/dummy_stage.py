# tests/dummy_stage.py
from scios.cognitive_core.kernel.stage import CognitiveStage

class DummyStage(CognitiveStage):
    def __init__(self, name: str = "dummy") -> None:
        super().__init__(name)

    def run(self, context):
        context.state[self.name] = f"Processed: {context.request.query}"
        context.trace.append(self.name)
        return context
