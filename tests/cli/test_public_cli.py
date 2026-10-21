import scios.cli as cli


def test_public_cli_exports_main():
    assert callable(cli.main)


def test_public_cli_help(capsys):
    assert cli.main(["--help"]) == 0
    output = capsys.readouterr().out
    assert "scios" in output


def test_public_cli_without_task_shows_help(capsys):
    assert cli.main([]) == 0
    output = capsys.readouterr().out
    assert "usage:" in output


def test_public_cli_executes_task(monkeypatch):
    class FakeResult:
        status = "success"
        value = {"command": "Analyze this system", "status": "accepted"}

    class FakeSciOS:
        def __init__(self):
            self.booted = False

        def boot(self):
            self.booted = True
            return True

        def run(self, task):
            assert self.booted is True
            assert task == "Analyze this system"
            return FakeResult()

        def shutdown(self):
            return True

    monkeypatch.setattr(cli, "SciOS", FakeSciOS)

    assert cli.main(["Analyze this system"]) == 0


def test_public_cli_returns_nonzero_on_execution_failure(monkeypatch, capsys):
    class FakeResult:
        status = "failed"
        value = {"error": "execution failed"}

    class FakeSciOS:
        def boot(self):
            return True

        def run(self, task):
            return FakeResult()

        def shutdown(self):
            return True

    monkeypatch.setattr(cli, "SciOS", FakeSciOS)

    assert cli.main(["test task"]) != 0


def test_public_cli_does_not_define_legacy_options(capsys):
    for argv in (
        ["--json"],
        ["--config", "config.yaml"],
        ["--debug"],
    ):
        assert cli.main(argv) != 0

    capsys.readouterr()
