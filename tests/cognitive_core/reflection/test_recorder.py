from scios.cognitive_core.reflection.recorder import ReflectionRecorder


def test_recorder_initialization():
    recorder = ReflectionRecorder()

    assert recorder.latest() is None
    assert recorder.all() == []


def test_recorder_log_and_latest():
    recorder = ReflectionRecorder()

    recorder.log("Reflection started")
    recorder.log("Reflection completed")

    assert recorder.latest() == "Reflection completed"
    assert recorder.all() == [
        "Reflection started",
        "Reflection completed",
    ]


def test_recorder_all_returns_copy():
    recorder = ReflectionRecorder()
    recorder.log("event")

    logs = recorder.all()
    logs.append("external")

    assert recorder.all() == ["event"]


def test_recorder_clear():
    recorder = ReflectionRecorder()
    recorder.log("event")

    recorder.clear()

    assert recorder.latest() is None
    assert recorder.all() == []


def test_recorder_repr():
    recorder = ReflectionRecorder()
    recorder.log("event")

    assert "ReflectionRecorder" in repr(recorder)
    assert "logs=1" in repr(recorder)
