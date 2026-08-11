"""
Core compression methods — zero dependencies, pure Python.
"""

import re
from typing import Literal

METHODS = Literal["uniform", "hybrid_lock", "p0p1", "edge_preserve"]

# Characters that carry critical information in technical text
ALWAYS_KEEP = set(
    '0123456789'                          # Arabic digits
    'abcdefghijklmnopqrstuvwxyz'          # Latin lowercase
    'ABCDEFGHIJKLMNOPQRSTUVWXYZ'          # Latin uppercase
    '.-+/%#@_=:;'                          # Technical symbols
)

# Chinese numeric characters — important for quantities/dates
CN_DIGITS = set('一二三四五六七八九十百千万亿两零')


def compress(
    text: str,
    method: METHODS = "uniform",
    ratio: float = 0.5,
) -> str:
    """
    Compress text using a pure-rule method.

    Args:
        text: Input text (Chinese, English, or mixed).
        method: Compression strategy.
            - "uniform": Keep every Nth character. Simple, fast, 50% compression.
            - "hybrid_lock": Lock ASCII entities, uniformly compress Chinese parts.
            - "p0p1": Keep only content-bearing characters, drop function words.
            - "edge_preserve": In 4-char windows, keep first and last character.
        ratio: Target keep ratio (0.0–1.0). Only used by "uniform" and "hybrid_lock".

    Returns:
        Compressed text string.

    Example:
        >>> compress("用户选了FastAPI做后端框架", method="hybrid_lock")
        '用选FastAPI做端架'
    """
    if not (0.0 < ratio <= 1.0):
        raise ValueError(f"ratio must be in (0, 1], got {ratio}")

    if method == "uniform":
        return _uniform(text, ratio)
    elif method == "hybrid_lock":
        return _hybrid_lock(text, ratio)
    elif method == "p0p1":
        return _p0p1(text)
    elif method == "edge_preserve":
        return _edge_preserve(text)
    else:
        raise ValueError(f"Unknown method: {method}. Use one of: uniform, hybrid_lock, p0p1, edge_preserve")


def softpack_compress(text: str) -> str:
    """
    The recommended default: hybrid_lock at 50% ratio.

    This is the method designed for pre-compression at ~70% context usage.
    It preserves all technical entities (English words, numbers, symbols)
    while uniformly compressing Chinese prose by half.

    Args:
        text: Input text.

    Returns:
        Compressed text with critical entities intact.

    Example:
        >>> softpack_compress(
        ...     "用户决定使用FastAPI作为Web框架，数据库选PostgreSQL 16，"
        ...     "部署用Docker Compose，监控用Prometheus加Grafana"
        ... )
        '用决使FastAPI作Web框数库PostgreSQL 16部用Docker Compose监用Prometheus加Grafana'
    """
    return _hybrid_lock(text, 0.5)


# ═══════════════════════════════════════════════════════════════
# Internal implementations
# ═══════════════════════════════════════════════════════════════

def _uniform(text: str, keep_ratio: float) -> str:
    """Keep every Nth character uniformly."""
    if not text:
        return text
    step = max(1, int(1.0 / keep_ratio))
    return text[::step]


def _hybrid_lock(text: str, keep_ratio: float) -> str:
    """
    Lock ASCII/tech chars (keep ALL), uniformly compress Chinese parts.

    This solves the core problem: uniform compression destroys English
    keywords like "FastAPI" → "FsP". Hybrid lock prevents this.
    """
    if not text:
        return text

    step = max(1, int(1.0 / keep_ratio))
    result = []
    chinese_counter = 0

    for ch in text:
        if ch in ALWAYS_KEEP or ch in CN_DIGITS:
            # Lock critical characters — always keep
            result.append(ch)
            chinese_counter = 0  # reset counter after locked chars
        elif '一' <= ch <= '鿿' or '\u3000' <= ch <= '\u303f':
            # Chinese character — apply uniform sampling
            chinese_counter += 1
            if chinese_counter % step == 1:
                result.append(ch)
        else:
            # Punctuation, whitespace, other — drop most
            if ch in '，。！？；：、\n\r':
                # Keep sentence breaks (reduced frequency)
                if chinese_counter > 0 and chinese_counter % (step * 4) == 0:
                    result.append(ch)
            else:
                # Keep other Unicode chars at low rate
                chinese_counter += 1
                if chinese_counter % (step * 2) == 1:
                    result.append(ch)

    return ''.join(result)


def _p0p1(text: str) -> str:
    """
    Keep only content-bearing characters.

    Drops: function words (的/了/是/在...), modal particles (啊/吧/呢...),
           pure punctuation.
    Keeps: English, digits, Chinese content characters.
    """
    if not text:
        return text

    # Characters to drop (function words, particles, common structural words)
    # NOTE: 不(negation), 我/你/他(pronouns), 哈(place name char) excluded
    # because dropping them can reverse meaning or destroy entities.
    # Examples: "不用" -> "用" (meaning reversed), "哈尔滨" -> "尔滨" (entity destroyed)
    DROP = set(
        '的啊吧呢吗呀哦嘛嗯呃噢哟嘿嘻呵哇啦呐呢么呗'
        '了的是在有这也就会要能可以对还'
        '着过把被让给到从向和与及或而但所为之其'
        '很非常比较稍微特别极其'
        '哪什么怎么为什么'
        '，。！？；：、 '
    )

    result = []
    for ch in text:
        if ch in ALWAYS_KEEP or ch in CN_DIGITS:
            result.append(ch)
        elif ch not in DROP:
            result.append(ch)

    return ''.join(result)


def _edge_preserve(text: str) -> str:
    """
    In 4-character windows, keep first and last character.

    This preserves the "shape" of the text while dropping internal characters.
    Better for Chinese where character-pair edges often carry meaning.
    """
    if not text:
        return text

    # Split into Latin/CJK runs for separate handling
    result = []
    parts = re.split(r'([a-zA-Z0-9.\-+/%#@_=:;]+)', text)

    for part in parts:
        if re.match(r'[a-zA-Z0-9.\-+/%#@_=:;]+', part):
            # English/Latin: keep short words intact, abbreviate long ones
            if len(part) <= 3:
                result.append(part)
            elif len(part) <= 6:
                result.append(part[0] + part[-2:])
            else:
                result.append(part[0] + part[-1])
        else:
            # Chinese: 4-char sliding window, keep edges
            i = 0
            while i < len(part):
                if i + 4 <= len(part):
                    result.append(part[i])       # first
                    result.append(part[i + 3])   # last
                    i += 4
                elif i + 2 <= len(part):
                    result.append(part[i])
                    result.append(part[i + 1])
                    i += 2
                else:
                    result.append(part[i])
                    i += 1

    return ''.join(result)
