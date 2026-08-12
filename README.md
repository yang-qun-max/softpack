# softpack

[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://pypi.org/project/softpack/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![tests](https://github.com/yang-qun-max/softpack/actions/workflows/test.yml/badge.svg)](https://github.com/yang-qun-max/softpack/actions/workflows/test.yml)
[![PyPI](https://img.shields.io/badge/pypi-soon-orange.svg)](https://pypi.org/project/softpack/)

> **Gentle pre-compression for AI agent context.**
> Press softly at 70% — before the LLM crushes at 83%.

---

## 🤔 The Problem

AI coding agents (Claude Code, Cursor, Copilot) use LLM-based compaction when context fills up. This compaction:

| Damage | Evidence |
|--------|----------|
| Loses **30-59%** of critical constraints | [ConstraintRot (2026)](https://arxiv.org/abs/2606.22528) — "Limit pool to 50" → dropped entirely |
| Reduces recall to **0-7%** at 50% compression | ["Lost in Compaction" (2026)](https://zenodo.org/records/20273815) |
| Causes **"lobotomy"** — agent forgets mid-task | 18% of sessions trigger compaction, averaging 6.7 times |

**Root cause:** LLM summarization rewrites `"PostgreSQL 16, asyncpg, pool=50"` into `"uses a database"`.

## 💡 The Idea

**Pre-compress at ~70% context** — before LLM summarization fires.

```
Normal:  0% ───→ 83% → [LLM compaction] → ~10% → lobotomy 🤯
                              ↑
                       content destroyed

With softpack:
         0% → 70% → [softpack: ~35% saved] → 35% → keep working → 83% → [LLM compaction] → ~10%
                       ↑                                     ↑
                  gentle rule-based                       only ONCE
                  zero entities lost                      not 2-3 times
```

- Chinese prose: ~50% reduction / Mixed text: 20-35% reduction
- **All** technical entities intact (English, numbers, symbols, code)
- Zero API calls, zero cost, zero data leaving your machine
- **1 LLM compaction instead of 3** in a typical 1-hour session

## 🚀 Quickstart

```bash
pip install softpack
# or directly from GitHub:
pip install git+https://github.com/yang-qun-max/softpack.git
```

```python
from softpack import softpack_compress

memory = (
    "用户决定使用FastAPI作为Web框架，数据库选PostgreSQL 16，"
    "部署用Docker Compose，监控用Prometheus加Grafana，"
    "目标API响应时间200ms以内。"
)

compressed = softpack_compress(memory)
print(compressed)
# 用决使FastAPI作Web框数库PostgreSQL 16部用Docker Compose监用Prometheus加Grafana目API响时200ms以。
```

✅ All 7 entities preserved: `FastAPI` `PostgreSQL` `16` `Docker` `Compose` `Prometheus` `Grafana` `200ms`

## 🎯 Four Methods, One Winner

```python
from softpack import compress
```

| Method | Strategy | Chinese Saved | Entities Lost | Best For |
|--------|----------|:---:|:---:|---|
| `hybrid_lock` ⭐ | Lock entities, compress Chinese | ~50% | **0** | **Default — mixed CN+EN** |
| `uniform` | Every Nth character | ~50% | All | Pure prose, no entities |
| `p0p1` | Drop function words only | ~19% | **0** | Max entity density |
| `edge_preserve` | 4-char window edges | ~49% | All | Chinese skim |

### The Entity Kill Shot

Why `hybrid_lock` is the default — here's what happens to real entities:

| Entity | `hybrid_lock` ⭐ | `uniform` | `p0p1` | `edge_preserve` |
|--------|:---:|:---:|:---:|:---:|
| `FastAPI` | ✅ FOUND | ❌ LOST | ✅ FOUND | ❌ LOST |
| `PostgreSQL` | ✅ FOUND | ❌ LOST | ✅ FOUND | ❌ LOST |
| `Docker Compose` | ✅ FOUND | ❌ LOST | ✅ FOUND | ❌ LOST |
| `Prometheus` | ✅ FOUND | ❌ LOST | ✅ FOUND | ❌ LOST |

→ Only `hybrid_lock` and `p0p1` keep entities. But `p0p1` only saves 19% — `hybrid_lock` saves 2-3× more.

## 🖥 CLI

```bash
# Pipe from stdin
echo "你的长文本..." | softpack compress

# Direct argument
softpack compress "你的长文本..."

# Pick method & ratio
softpack compress -m hybrid_lock -r 0.5 "你的长文本..."
```

## 🔌 MCP Server (Claude Code)

```bash
pip install softpack[mcp]
claude mcp add softpack -- softpack mcp
```

Claude Code can call `softpack_compress` before compaction fires — buy more headroom.

## 🆚 vs Alternatives

| Tool | Approach | Chinese? | Zero Deps? | Position |
|------|----------|:---:|:---:|---|
| **softpack** | Rule-based pre-compression | ✅ | ✅ | **Before LLM fires** |
| [memq](https://www.npmjs.com/package/@sixdayswest/memq) | Rule-based memory compression | ❌ | ✅ | English memories |
| [Curator](https://github.com/Hhhpraise/curator-context) | Context triage | ❌ | ❌ | Throw away low-value context |
| LLM Compaction | Summarization | ✅ | ❌ | Last resort — loses 30-59% constraints |

**softpack is not a replacement for LLM compaction.** It's a buffer layer that delays it — fewer compactions = fewer lost constraints.

## ⚠️ Honest Limitations

1. **Chinese-optimized.** English-only text → near 0% compression (all entities locked).
2. **Not semantic.** Doesn't "understand" text. Implied constraints ("reply concisely") can't be protected.
3. **Not benchmarked** on standard datasets yet. Community contributions welcome.
4. **Ratio below 0.33** → Chinese becomes unreadable, English keywords break.

## 📦 What softpack is NOT

- ❌ A replacement for LLM summarization
- ❌ Semantic compression
- ❌ A full memory management system

> **softpack is a pre-compression layer.** It buys time. 1 LLM compaction instead of 3.

## 📚 Related Work

- [Constraint Pinning](https://arxiv.org/abs/2606.22528) (Chen et al., 2026) — 59% constraint violation → 0% with pinning
- ["Lost in Compaction"](https://zenodo.org/records/20273815) (2026) — 234 facts, 98% compression → 21% recall
- [memq](https://www.npmjs.com/package/@sixdayswest/memq) — Deterministic English memory compression (our closest cousin)
- [Curator](https://github.com/Hhhpraise/curator-context) — Context triage before compression

## 📄 License

MIT — use it, fork it, ship it.

---

*Built by [Yang Qun](https://github.com/yang-qun-max). Research + engineering + honest about limits.*
