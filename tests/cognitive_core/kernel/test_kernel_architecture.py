from scios.cognitive_core.kernel import CognitiveKernel as PackageKernel
from scios.cognitive_core.kernel.kernel import CognitiveKernel as ModuleKernel


def test_package_kernel_is_canonical_kernel() -> None:
    assert PackageKernel is ModuleKernel


def test_kernel_pipeline_shares_dispatcher() -> None:
    kernel = ModuleKernel()

    assert kernel.pipeline.dispatcher is kernel.dispatcher


def test_kernel_pipeline_shares_middleware() -> None:
    kernel = ModuleKernel()

    assert kernel.pipeline.middleware is kernel.middleware


def test_kernel_pipeline_shares_event_bus() -> None:
    kernel = ModuleKernel()

    assert kernel.pipeline.event_bus is kernel.event_bus


def test_public_package_kernel_can_be_created() -> None:
    kernel = PackageKernel()

    assert isinstance(kernel, ModuleKernel)
    assert kernel._booted is False


def test_public_package_kernel_reset_is_valid() -> None:
    kernel = PackageKernel()

    kernel.boot()
    kernel.reset()

    assert kernel.state.status.name == "IDLE"
