"""
softpack demo — 30-second quickstart.
"""

from softpack import compress, softpack_compress

# Sample AI agent memory — mixed Chinese + English tech content
MEMORY = (
    "用户说：行那就FastAPI吧。不过我还是有一个担心，"
    "我们团队之前一直用Django，转FastAPI会有学习成本。"
    "而且目前数据库用的是PostgreSQL 16，FastAPI对这个支持怎么样？"
    "另外部署方面，我们希望用Docker Compose来管理环境，"
    "监控方面用Prometheus加Grafana，目标是把API响应时间控制在200ms以内。"
)

print("=" * 60)
print("softpack — Gentle Pre-Compression Demo")
print("=" * 60)
print()
print(f"Original ({len(MEMORY)} chars):")
print(f"  {MEMORY}")
print()

# Demo each method
methods = [
    ("hybrid_lock (推荐)", "hybrid_lock", 0.5),
    ("uniform 50%", "uniform", 0.5),
    ("p0p1 (去虚词)", "p0p1", 0.5),
    ("edge_preserve", "edge_preserve", 0.5),
]

for label, method, ratio in methods:
    result = compress(MEMORY, method=method, ratio=ratio)
    saved = len(MEMORY) - len(result)
    pct = saved / len(MEMORY) * 100

    print(f"{label} ({len(result)} chars, saved {pct:.0f}%):")
    print(f"  {result}")
    print()

# Entity preservation check
print("=" * 60)
print("Entity Preservation Check")
print("=" * 60)
entities = ["FastAPI", "Django", "PostgreSQL", "Docker", "Compose",
            "Prometheus", "Grafana", "200ms", "16"]

print(f"{'Entity':<15s} ", end="")
for label, method, _ in methods:
    print(f"{label:<18s} ", end="")
print()

for ent in entities:
    print(f"{ent:<15s} ", end="")
    for _, method, ratio in methods:
        result = compress(MEMORY, method=method, ratio=ratio)
        found = "FOUND" if ent.lower() in result.lower() else "LOST"
        print(f"{found:<18s} ", end="")
    print()

print()
print("=" * 60)
print("Quickstart (recommended default):")
print("=" * 60)
print()
print("  from softpack import softpack_compress")
print('  result = softpack_compress("你的长文本")')
print()
print(f"  Result: {softpack_compress(MEMORY)}")
