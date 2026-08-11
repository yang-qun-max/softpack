"""Tests for softpack compression methods."""

import pytest
from softpack import compress, softpack_compress


# -- Test data --

CHINESE_TECH = (
    "用户决定使用FastAPI作为Web框架，数据库选PostgreSQL 16，"
    "部署用Docker Compose，监控用Prometheus加Grafana，"
    "目标API响应时间200ms以内。"
)

CRITICAL_ENTITIES = [
    "FastAPI", "PostgreSQL", "16", "Docker", "Compose",
    "Prometheus", "Grafana", "200ms",
]

PURE_CHINESE = "今天天气很好我们去公园散步吧"


# -- Basic functionality --

def test_compress_returns_string():
    result = compress("hello world")
    assert isinstance(result, str)


def test_compress_empty_string():
    assert compress("") == ""


def test_compress_short_text():
    assert len(compress("你好")) <= 2


def test_invalid_method_raises():
    with pytest.raises(ValueError):
        compress("hello", method="nonexistent")


# -- Ratio validation --

def test_ratio_zero_raises():
    with pytest.raises(ValueError):
        compress("hello", ratio=0.0)


def test_ratio_negative_raises():
    with pytest.raises(ValueError):
        compress("hello", ratio=-1.0)


def test_ratio_over_one_raises():
    with pytest.raises(ValueError):
        compress("hello", ratio=1.5)


def test_ratio_boundary_ok():
    assert compress("hello", ratio=0.01) is not None
    assert compress("hello", ratio=1.0) == "hello"


# -- Uniform method --

def test_uniform_basic():
    result = compress("abcdefgh", method="uniform", ratio=0.5)
    assert result == "aceg"


def test_uniform_ratio_one():
    assert compress("hello", method="uniform", ratio=1.0) == "hello"


def test_uniform_ratio_min():
    result = compress("hello world", method="uniform", ratio=0.01)
    assert len(result) >= 1


# -- Hybrid lock method --

def test_hybrid_lock_preserves_entities():
    result = compress(CHINESE_TECH, method="hybrid_lock", ratio=0.5)
    for entity in CRITICAL_ENTITIES:
        assert entity in result, f"Entity '{entity}' lost in hybrid_lock"


def test_hybrid_lock_reduces_size():
    result = compress(CHINESE_TECH, method="hybrid_lock", ratio=0.5)
    assert len(result) < len(CHINESE_TECH)


def test_hybrid_lock_compresses_chinese():
    mixed = "用户说这个FastAPI框架真的很好用啊"
    result = compress(mixed, method="hybrid_lock", ratio=0.5)
    assert "FastAPI" in result
    assert len(result) < len(mixed)


# -- P0+P1 method --

def test_p0p1_preserves_entities():
    result = compress(CHINESE_TECH, method="p0p1")
    for entity in CRITICAL_ENTITIES:
        assert entity in result, f"Entity '{entity}' lost in p0p1"


def test_p0p1_drops_function_words():
    result = compress("这是一个非常好的框架", method="p0p1")
    for word in ['的', '是']:
        assert word not in result


def test_p0p1_keeps_content():
    result = compress("用户选了框架", method="p0p1")
    assert "用户" in result
    assert "框架" in result


def test_p0p1_negation_preserved():
    """Negation must never be dropped - it would reverse meaning."""
    result = compress("不用PostgreSQL", method="p0p1")
    assert "不" in result
    assert "用" in result


def test_p0p1_pronouns_preserved():
    """Pronouns carry agent/patient info."""
    result = compress("我确定他说可以", method="p0p1")
    assert "我" in result
    assert "他" in result


def test_p0p1_place_name_preserved():
    """Ha must not be dropped - destroys place names like Harbin."""
    result = compress("哈尔滨的天气", method="p0p1")
    assert "哈尔滨" in result


def test_p0p1_single_char_not_empty():
    """Single CJK content char should survive p0p1."""
    result = compress("我", method="p0p1")
    assert len(result) >= 1


# -- Edge preserve method --

def test_edge_preserve_basic():
    result = compress("今天天气很好", method="edge_preserve")
    assert len(result) <= 6
    assert result != "今天天气很好"


# -- softpack_compress convenience --

def test_softpack_compress_returns_string():
    result = softpack_compress(CHINESE_TECH)
    assert isinstance(result, str)
    assert len(result) < len(CHINESE_TECH)


def test_softpack_compress_preserves_entities():
    result = softpack_compress(CHINESE_TECH)
    for entity in CRITICAL_ENTITIES:
        assert entity in result, f"Entity '{entity}' lost"


# -- Edge cases --

def test_only_english():
    result = compress("FastAPI PostgreSQL Docker Compose", method="hybrid_lock")
    assert "FastAPI" in result


def test_only_chinese():
    result = compress(PURE_CHINESE, method="uniform", ratio=0.5)
    assert len(result) >= len(PURE_CHINESE) // 2 - 1


def test_mixed_unicode():
    result = compress("测试test123数据", method="hybrid_lock", ratio=0.5)
    assert "test123" in result


def test_numbers_preserved():
    result = compress("版本3.14.0 端口8080 超时30s", method="hybrid_lock", ratio=0.5)
    assert "3.14.0" in result
    assert "8080" in result
    assert "30" in result


def test_whitespace_only_not_crash():
    """Whitespace-only input should not crash."""
    result = compress("   \n\t  ", method="hybrid_lock")
    assert isinstance(result, str)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
