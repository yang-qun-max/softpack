# softpack 推广文案

---

## 🇨🇳 中文版（V2EX / 掘金 / 知乎）

### 标题：你的 AI Coding Agent 干到一半就"失忆"？我写了个工具让它多撑 3 倍时间

---

**问题：AI Agent 的"脑叶切除"**

用 Claude Code / Cursor 写过代码的都知道：聊着聊着 agent 就开始忘事。

"数据库连接池改成 50" → 过半小时 → agent 当没说过。

这不是幻觉。这是 LLM 压缩（compaction）的副作用。当上下文满了，系统会调 LLM 做摘要——但 LLM 会把精确信息重写成模糊描述：

```
"PostgreSQL 16, asyncpg, pool=50" → "uses a database with performance tuning"
```

学术研究已证实：**30-59% 的关键约束在压缩后消失**（ConstraintRot 论文，2026）。

**一个小时的典型 session 触发 2-3 次压缩。** 每压一次，agent 就"笨"一点。

---

**思路：在 LLM 动手之前，先用规则预压一次**

我的想法很简单：

```
通常: 0% → 83%满了 → LLM压缩(丢30-59%约束) → 10% → 继续 → 83%满了 → LLM压缩(再丢) → ...
                            
加了 softpack:
      0% → 70% → [softpack规则压缩] → 35% → 继续 → 83% → LLM压缩(只触发1次)
                  ↑
           零成本, 零API调用
           技术实体一个不丢
```

**在 70% 上下文的时点加一层纯规则的预压缩。** 压中文保留英文/数字/符号——因为技术实体才是 agent 不能丢的东西。

---

**四种方法一目了然：**

| 方法 | 策略 | 中文省 | 实体丢 | 适合 |
|------|------|:---:|:---:|------|
| `hybrid_lock` ⭐ | 锁定ASCII实体, 均匀压中文 | ~50% | **0个** | **默认推荐** |
| `uniform` | 每N个字保留1个 | 50% | 全丢 | 纯中文无实体 |
| `p0p1` | 只去虚词 | 19% | **0个** | 实体密度最重要 |
| `edge_preserve` | 4字窗口保留首尾 | 49% | 全丢 | 中文速览 |

**实体保护效果（最直观的证明）：**

```
Entity          hybrid_lock ⭐    uniform 50%    
FastAPI         ✅ FOUND           ❌ LOST       
PostgreSQL      ✅ FOUND           ❌ LOST       
Docker Compose  ✅ FOUND           ❌ LOST       
Prometheus      ✅ FOUND           ❌ LOST       
Grafana         ✅ FOUND           ❌ LOST       
```

---

**特点：**

- 📦 `pip install softpack` 一行安装
- ⚡ **零依赖** — 纯 Python 标准库，不调 API
- 🔒 数据不出机器
- 🖥 CLI + MCP Server（直接接 Claude Code）
- 📜 MIT 协议 — 随便用

---

**诚实说：**

- ⚠️ 中文优化。纯英文文本压不了多少（英文全锁了）
- ⚠️ 不是语义压缩，不"理解"文本
- ⚠️ 不是替代 LLM 压缩，是**延迟**它
- ⚠️ 没做标准数据集 benchmark（欢迎贡献真实测评）

---

**GitHub: [github.com/yang-qun-max/softpack](https://github.com/yang-qun-max/softpack)**

欢迎 star / issue / PR。求职中，star 就是最好的推荐信 🙏

---

## 🇬🇧 English Version (Reddit r/Python, r/ClaudeAI)

### Title: Your AI coding agent goes dumb mid-session? I built a pre-compression tool that buys you 3× more time before the lobotomy

---

**The Problem: LLM Compaction Destroys Constraints**

If you've used Claude Code, Cursor, or Copilot for long sessions, you know the pattern:

"Set the connection pool to 50" → 30 minutes later → agent acts like you never said it.

This isn't hallucination. It's **LLM compaction** — when context fills up, the system asks an LLM to summarize. But LLMs rewrite precise values into vague prose:

```
"PostgreSQL 16, asyncpg, pool=50" → "uses a database with performance tuning"
```

Papers confirm: **30-59% of critical constraints are silently dropped** during compaction (ConstraintRot, 2026). And in a typical 1-hour session, compaction fires **2-3 times**. Each time, your agent gets slightly dumber.

---

**The Fix: Pre-Compress at 70%, Before the LLM Fires**

```
Normal:  0% → 83% → [LLM compaction, 30-59% constraints lost] → 10% → repeat 2-3×

With softpack:
         0% → 70% → [softpack rule-based] → 35% → 83% → [LLM compaction, only ONCE]
                    ↑
               Zero API calls
               All entities survive
```

**softpack compresses Chinese prose by ~50% while locking ALL ASCII tech entities** — English words, numbers, symbols, code. The LLM compaction fires later, fires fewer times.

---

**The Entity Kill Shot:**

```
Entity          hybrid_lock (default)    uniform 50%
FastAPI         ✅ FOUND                  ❌ LOST
PostgreSQL      ✅ FOUND                  ❌ LOST
Docker Compose  ✅ FOUND                  ❌ LOST
Prometheus      ✅ FOUND                  ❌ LOST
```

`uniform` destroys EVERYTHING. `hybrid_lock` preserves EVERYTHING.

---

**Install:**

```bash
pip install softpack
```

```python
from softpack import softpack_compress

memory = "用户决定使用FastAPI...PostgreSQL 16...Docker Compose..."
compressed = softpack_compress(memory)
# All entities intact, Chinese compressed by ~50%
```

- ⚡ Zero dependencies (pure stdlib)
- 🔒 Zero API calls, data never leaves your machine
- 🖥 CLI + MCP Server (Claude Code integration)
- 📜 MIT license

**Honest limits:** Chinese-optimized. English-only text barely compresses. Not a replacement for LLM compaction — it **delays** it.

---

**GitHub: [github.com/yang-qun-max/softpack](https://github.com/yang-qun-max/softpack)**

I'm job-hunting — every star helps more than you know ⭐
