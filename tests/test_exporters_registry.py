from scios.metrics.exporters import (
    default_registry,
    create_exporter,
    JSONExporter,
)


def test_registry():

    exporters = (
        default_registry.available()
    )

    print(exporters)

    assert "json" in exporters



def test_create_json_exporter():

    exporter = create_exporter(
        "json",
        service_name="scios-kernel"
    )

    assert isinstance(
        exporter,
        JSONExporter
    )