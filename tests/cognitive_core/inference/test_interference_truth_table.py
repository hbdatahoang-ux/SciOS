import pytest

_inference = pytest.importorskip("scios.cognitive_core.inference")
interference = _inference.interference


@pytest.mark.parametrize(
    ("compatibility", "cos_phase", "expected"),
    [
        # Case 1: compatible + aligned -> constructive
        (1.0, 1.0, 0.8),

        # Case 2: compatible + opposed -> destructive
        (1.0, -1.0, -0.8),

        # Case 3: conflicting + aligned -> destructive
        (-1.0, 1.0, -0.8),

        # Case 4: conflicting + opposed -> constructive
        (-1.0, -1.0, 0.8),
    ],
)
def test_interference_truth_table(
    compatibility,
    cos_phase,
    expected,
):
    result = interference(
        amplitude_i=0.5,
        amplitude_j=0.8,
        coupling=1.0,
        compatibility=compatibility,
        cos_phase=cos_phase,
    )

    assert result == pytest.approx(expected)


def test_compatible_aligned_is_constructive():
    result = interference(
        amplitude_i=0.5,
        amplitude_j=0.8,
        coupling=1.0,
        compatibility=1.0,
        cos_phase=1.0,
    )

    assert result > 0


def test_compatible_opposed_is_destructive():
    result = interference(
        amplitude_i=0.5,
        amplitude_j=0.8,
        coupling=1.0,
        compatibility=1.0,
        cos_phase=-1.0,
    )

    assert result < 0


def test_conflicting_aligned_is_destructive():
    result = interference(
        amplitude_i=0.5,
        amplitude_j=0.8,
        coupling=1.0,
        compatibility=-1.0,
        cos_phase=1.0,
    )

    assert result < 0


def test_conflicting_opposed_is_constructive():
    result = interference(
        amplitude_i=0.5,
        amplitude_j=0.8,
        coupling=1.0,
        compatibility=-1.0,
        cos_phase=-1.0,
    )

    assert result > 0


def test_zero_compatibility_produces_zero_interference():
    result = interference(
        amplitude_i=0.5,
        amplitude_j=0.8,
        coupling=1.0,
        compatibility=0.0,
        cos_phase=1.0,
    )

    assert result == pytest.approx(0.0)


def test_quadrature_phase_produces_zero_interference():
    result = interference(
        amplitude_i=0.5,
        amplitude_j=0.8,
        coupling=1.0,
        compatibility=1.0,
        cos_phase=0.0,
    )

    assert result == pytest.approx(0.0)


def test_zero_coupling_produces_zero_interference():
    result = interference(
        amplitude_i=0.5,
        amplitude_j=0.8,
        coupling=0.0,
        compatibility=1.0,
        cos_phase=1.0,
    )

    assert result == pytest.approx(0.0)


def test_zero_amplitude_produces_zero_interference():
    result = interference(
        amplitude_i=0.0,
        amplitude_j=0.8,
        coupling=1.0,
        compatibility=1.0,
        cos_phase=1.0,
    )

    assert result == pytest.approx(0.0)


def test_interference_uses_canonical_equation():
    amplitude_i = 0.6
    amplitude_j = 0.7
    coupling = 0.9
    compatibility = -0.4
    cos_phase = -0.75

    expected = (
        2
        * coupling
        * amplitude_i
        * amplitude_j
        * compatibility
        * cos_phase
    )

    result = interference(
        amplitude_i=amplitude_i,
        amplitude_j=amplitude_j,
        coupling=coupling,
        compatibility=compatibility,
        cos_phase=cos_phase,
    )

    assert result == pytest.approx(expected)
