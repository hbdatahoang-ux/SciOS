# ==============================================================================
# Part 1. Imports
# ==============================================================================

import json

import pytest

from scios.runtime.observability.metrics.runtime.cache import (
    RuntimeCache,
    DEFAULT_NAME,
    DEFAULT_ENABLED,
    DEFAULT_MAX_SIZE,
    DEFAULT_TTL,
    DEFAULT_CLEAN_INTERVAL,
    DEFAULT_HITS,
    DEFAULT_MISSES,
)


# ==============================================================================
# Part 2. Helpers
# ==============================================================================

def create_cache() -> RuntimeCache:

    cache = RuntimeCache(
        name="demo",
    )

    cache.put(
        "a",
        1,
    )

    cache.put(
        "b",
        2,
    )

    cache.record_hit()

    cache.record_miss()

    return cache


# ==============================================================================
# Part 3. Constructor
# ==============================================================================

def test_default_constructor():

    cache = RuntimeCache()

    assert cache.name == DEFAULT_NAME
    assert cache.enabled is DEFAULT_ENABLED
    assert cache.max_size == DEFAULT_MAX_SIZE
    assert cache.ttl == DEFAULT_TTL

    assert cache.hits == DEFAULT_HITS
    assert cache.misses == DEFAULT_MISSES

    assert cache.hit_rate == pytest.approx(0.0)
    assert cache.miss_rate == pytest.approx(0.0)

    assert len(cache.entries) == 0


def test_custom_constructor():

    cache = RuntimeCache(
        name="cache",
        enabled=False,
        max_size=256,
        ttl=30.0,
        clean_interval=5.0,
    )

    assert cache.name == "cache"
    assert cache.enabled is False
    assert cache.max_size == 256
    assert cache.ttl == 30.0

    assert cache.hits == DEFAULT_HITS
    assert cache.misses == DEFAULT_MISSES

    assert cache.hit_rate == pytest.approx(0.0)
    assert cache.miss_rate == pytest.approx(0.0)

    assert cache._clean_interval == 5.0


def test_slots():

    assert hasattr(
        RuntimeCache,
        "__slots__",
    )

# ==============================================================================
# Part 4. Properties
# ==============================================================================

def test_properties():

    cache = create_cache()

    assert cache.name == "demo"
    assert cache.enabled is True
    assert cache.max_size == DEFAULT_MAX_SIZE
    assert cache.ttl == DEFAULT_TTL
    assert cache.entries
    assert cache.hits == 1
    assert cache.misses == 1
    assert cache.size == 2
    assert cache.utilization > 0.0


def test_name_property():

    assert create_cache().name == "demo"


def test_enabled_property():

    assert create_cache().enabled is True


def test_max_size_property():

    assert create_cache().max_size == DEFAULT_MAX_SIZE


def test_ttl_property():

    assert create_cache().ttl == DEFAULT_TTL


def test_entries_property():

    cache = create_cache()

    assert isinstance(
        cache.entries,
        dict,
    )

    assert len(cache.entries) == 2


def test_hits_property():

    assert create_cache().hits == 1


def test_misses_property():

    assert create_cache().misses == 1


def test_size_property():

    assert create_cache().size == 2


def test_utilization_property():

    cache = create_cache()

    assert cache.utilization == pytest.approx(
        2 / cache.max_size,
    )


# ==============================================================================
# Part 5. Lifecycle
# ==============================================================================

def test_enable():

    cache = RuntimeCache(
        enabled=False,
    )

    cache.enable()

    assert cache.enabled is True


def test_disable():

    cache = RuntimeCache()

    cache.disable()

    assert cache.enabled is False


def test_clear():

    cache = create_cache()

    cache.clear()

    assert cache.size == 0


def test_reset():

    cache = create_cache()

    cache.reset()

    assert cache.enabled == DEFAULT_ENABLED
    assert cache.size == 0
    assert cache.hits == DEFAULT_HITS
    assert cache.misses == DEFAULT_MISSES


def test_cleanup():

    cache = create_cache()

    cache.cleanup()

    assert isinstance(
        cache.entries,
        dict,
    )


def test_expire():

    cache = create_cache()

    cache.expire()

    assert isinstance(
        cache.entries,
        dict,
    )


def test_enable_disable():

    cache = RuntimeCache()

    cache.disable()

    assert not cache.enabled

    cache.enable()

    assert cache.enabled


# ==============================================================================
# Part 6. Cache API
# ==============================================================================

def test_put():

    cache = RuntimeCache()

    cache.put(
        "x",
        100,
    )

    assert cache.has("x")


def test_get():

    cache = RuntimeCache()

    cache.put(
        "x",
        10,
    )

    assert cache.get("x") == 10


def test_remove():

    cache = RuntimeCache()

    cache.put(
        "x",
        1,
    )

    cache.remove("x")

    assert not cache.has("x")


def test_has():

    cache = RuntimeCache()

    cache.put(
        "x",
        1,
    )

    assert cache.has("x")


def test_touch():

    cache = RuntimeCache()

    cache.put(
        "x",
        1,
    )

    cache.touch("x")

    assert cache.has("x")


def test_pop():

    cache = RuntimeCache()

    cache.put(
        "x",
        5,
    )

    assert cache.pop("x") == 5

    assert not cache.has("x")


def test_keys():

    cache = create_cache()

    assert set(cache.keys()) == {
        "a",
        "b",
    }


def test_values():

    cache = create_cache()

    assert sorted(cache.values()) == [
        1,
        2,
    ]


def test_items():

    cache = create_cache()

    assert dict(cache.items()) == {
        "a": 1,
        "b": 2,
    }


def test_clear_entries():

    cache = create_cache()

    cache.clear_entries()

    assert cache.size == 0

# ==============================================================================
# Part 7. Statistics
# ==============================================================================

def test_record_hit():

    cache = RuntimeCache()

    cache.record_hit()

    assert cache.hits == 1


def test_record_miss():

    cache = RuntimeCache()

    cache.record_miss()

    assert cache.misses == 1


def test_hit_rate():

    cache = RuntimeCache()

    cache.record_hit()
    cache.record_hit()
    cache.record_miss()

    assert cache.hit_rate == pytest.approx(2 / 3)


def test_miss_rate():

    cache = RuntimeCache()

    cache.record_hit()
    cache.record_miss()

    assert cache.miss_rate == pytest.approx(0.5)


def test_stats():

    cache = create_cache()

    stats = cache.stats()

    assert stats["hits"] == 1
    assert stats["misses"] == 1


def test_reset_stats():

    cache = create_cache()

    cache.reset_stats()

    assert cache.hits == 0
    assert cache.misses == 0


# ==============================================================================
# Part 8. Operations
# ==============================================================================

def test_clone():

    cache = create_cache()

    clone = cache.clone()

    assert clone == cache
    assert clone is not cache
    assert clone.entries is not cache.entries

    clone.put(
        "c",
        3,
    )

    assert cache.get("c") is None


def test_copy():

    cache = create_cache()

    copy = cache.copy()

    assert copy == cache
    assert copy is not cache
    assert copy.entries is not cache.entries

    copy.put(
        "d",
        4,
    )

    assert cache.get("d") is None


def test_merge():

    a = RuntimeCache()

    b = RuntimeCache()

    b.put("x", 10)
    b.record_hit()

    a.merge(b)

    assert a.get("x") == 10
    assert "x" in a


def test_update():

    cache = RuntimeCache()

    cache.put("a", 1)
    cache.put("b", 2)

    assert cache.get("a") == 1
    assert cache.get("b") == 2


def test_snapshot():

    cache = create_cache()

    state = cache.snapshot()

    assert isinstance(
        state,
        dict,
    )

    assert state == cache.to_dict()
    assert state is not cache.to_dict()


def test_restore():

    original = create_cache()

    cache = RuntimeCache()

    cache.restore(
        original.snapshot()
    )

    assert cache == original
    assert cache is not original
    assert cache.get("a") == 1
    assert cache.get("b") == 2


# ==============================================================================
# Part 9. Validation
# ==============================================================================

def test_validate_name():

    assert create_cache().validate_name()


def test_validate_entries():

    assert create_cache().validate_entries()


def test_validate_limits():

    assert create_cache().validate_limits()


def test_validate():

    assert create_cache().validate()


def test_normalize():

    cache = RuntimeCache(
        name="  demo  ",
    )

    cache.normalize()

    assert cache.name == "demo"


# ==============================================================================
# Part 10. Serialization
# ==============================================================================

def test_to_dict():

    cache = create_cache()

    data = cache.to_dict()

    assert data["name"] == "demo"


def test_from_dict():

    cache = RuntimeCache.from_dict(
        create_cache().to_dict()
    )

    assert cache == create_cache()


def test_to_tuple():

    cache = create_cache()

    data = cache.to_tuple()

    assert isinstance(
        data,
        tuple,
    )


def test_from_tuple():

    cache = RuntimeCache.from_tuple(
        create_cache().to_tuple()
    )

    assert cache == create_cache()


def test_to_json():

    cache = create_cache()

    text = cache.to_json()

    assert json.loads(text)["name"] == "demo"


def test_from_json():

    cache = RuntimeCache.from_json(
        create_cache().to_json()
    )

    assert cache == create_cache()


# ==============================================================================
# Part 11. Diagnostics
# ==============================================================================

def test_summary():

    summary = create_cache().summary()

    assert summary["name"] == "demo"


def test_diagnostics():

    diagnostics = create_cache().diagnostics()

    assert diagnostics["valid"] is True


def test_report():

    report = create_cache().report()

    assert isinstance(
        report,
        dict,
    )


def test_status():

    cache = RuntimeCache()

    assert cache.status() in (
        "enabled",
        "disabled",
        "idle",
        "active",
    )


# ==============================================================================
# Part 12. Protocols
# ==============================================================================

def test_len():

    assert len(create_cache()) == 2


def test_contains():

    cache = create_cache()

    assert "a" in cache


def test_iter():

    cache = create_cache()

    assert len(list(cache)) == 2


def test_hash():

    assert isinstance(
        hash(create_cache()),
        int,
    )


def test_eq():

    assert create_cache() == create_cache()


def test_repr():

    assert "RuntimeCache" in repr(create_cache())


def test_str():

    assert str(create_cache()) == "demo"


def test_bool():

    assert bool(create_cache()) is True    