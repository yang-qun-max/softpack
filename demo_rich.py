#!/usr/bin/env python3
"""
softpack terminal demo — beautiful rich output for screenshots/GIF.
Run: python demo_rich.py
"""

import sys
import time
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich import box
from rich.layout import Layout
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn

from softpack import compress, softpack_compress

console = Console(width=90)

# ── Test data ──
TECH_TEXT = (
    "用户决定使用FastAPI作为Web框架，数据库选PostgreSQL 16，"
    "部署用Docker Compose，监控用Prometheus加Grafana，"
    "目标API响应时间200ms以内。"
)

ENTITIES = ["FastAPI", "PostgreSQL", "16", "Docker", "Compose", "Prometheus", "Grafana", "200ms"]

LONG_TEXT = (
    "用户提出：我们的后端服务目前用Flask，但QPS一上去就扛不住了。"
    "调研了一下，FastAPI的异步支持更好，而且Pydantic做数据验证很香。"
    "数据库这块，PostgreSQL 16的JSONB查询性能确实碾压MySQL。"
    "关键问题是部署——之前手动ssh上去改配置太痛苦了，"
    "现在想用Docker Compose统一管理所有环境。"
    "监控方面，Prometheus + Grafana的方案很成熟，AlertManager还能配置告警规则。"
    "还有一个担心：如果压到50%ratio，中文可读性会不会崩？"
    "目标API响应时间200ms以内。实测发现保留关键词后，剩下的中文虽然像电报但能懂。"
)


def main():
    console.clear()

    # ═══════════════════════════════════════════
    # Title
    # ═══════════════════════════════════════════
    title = Text()
    title.append("softpack", style="bold white on blue")
    title.append("  — gentle pre-compression for AI context", style="dim cyan")
    console.print()
    console.print(Panel(title, box=box.HEAVY, border_style="blue"))
    time.sleep(0.4)

    # ═══════════════════════════════════════════
    # Step 1: The Problem
    # ═══════════════════════════════════════════
    console.print()
    console.print("[bold]📋 场景：[/bold]你的 AI coding agent 上下文快满了...")
    time.sleep(0.3)

    console.print()
    console.print(Panel(
        LONG_TEXT,
        title="你的对话上下文",
        border_style="yellow",
        padding=(1, 2),
    ))
    time.sleep(0.5)
    console.print(f"[dim]原始长度: {len(LONG_TEXT)} 字符 | 含 {len(ENTITIES)} 个技术实体[/dim]")

    # ═══════════════════════════════════════════
    # Step 2: Four Methods Comparison
    # ═══════════════════════════════════════════
    console.print()
    console.print("[bold]🔬 四种方法对比：[/bold]")
    time.sleep(0.3)

    methods = [
        ("hybrid_lock", "hybrid_lock ⭐ (推荐)", 0.5),
        ("uniform", "uniform (均匀采样)", 0.5),
        ("p0p1", "p0p1 (去虚词)", None),
        ("edge_preserve", "edge_preserve (窗口边缘)", None),
    ]

    table = Table(title="压缩结果对比", box=box.ROUNDED, border_style="blue")
    table.add_column("方法", style="cyan", width=20)
    table.add_column("压缩后", style="white", width=50)
    table.add_column("节省", style="green", width=10)
    table.add_column("实体丢失", style="red", width=10)

    for method_key, method_label, ratio in methods:
        if ratio is not None:
            result = compress(LONG_TEXT, method=method_key, ratio=ratio)
        else:
            result = compress(LONG_TEXT, method=method_key)
        saved = f"{100 - len(result) / len(LONG_TEXT) * 100:.0f}%"
        lost_count = sum(1 for e in ENTITIES if e not in result)
        lost_str = f"{lost_count}/{len(ENTITIES)}" if lost_count > 0 else "0 ✅"
        table.add_row(method_label, result[:72] + "...", saved, lost_str)

    console.print(table)
    time.sleep(0.5)

    # ═══════════════════════════════════════════
    # Step 3: Entity Kill Shot
    # ═══════════════════════════════════════════
    console.print()
    console.print("[bold]🎯 实体保护对比（关键！）：[/bold]")
    time.sleep(0.3)

    etable = Table(box=box.ROUNDED, border_style="magenta")
    etable.add_column("Entity", style="bold white")
    etable.add_column("hybrid_lock ⭐", style="green")
    etable.add_column("uniform", style="red")
    etable.add_column("p0p1", style="yellow")
    etable.add_column("edge_preserve", style="red")

    for entity in ENTITIES:
        row = [entity]
        for method_key in ["hybrid_lock", "uniform", "p0p1", "edge_preserve"]:
            if method_key in ("uniform",):
                result = compress(LONG_TEXT, method=method_key, ratio=0.5)
            else:
                result = compress(LONG_TEXT, method=method_key)
            if entity in result:
                row.append("[green]FOUND[/green]")
            else:
                row.append("[red]LOST[/red]")
        etable.add_row(*row)
    console.print(etable)
    time.sleep(0.5)

    # ═══════════════════════════════════════════
    # Step 4: CLI Demo
    # ═══════════════════════════════════════════
    console.print()
    console.print("[bold]🖥 CLI 用法：[/bold]")
    console.print()
    console.print(Panel(
        "[white]$ [cyan]softpack compress[/cyan] -m hybrid_lock [dim]\"你的长文本...\"[/dim][/white]",
        border_style="green",
        padding=(1, 2),
    ))
    time.sleep(0.3)

    # ═══════════════════════════════════════════
    # Step 5: MCP for Claude Code
    # ═══════════════════════════════════════════
    console.print()
    console.print("[bold]🔌 Claude Code MCP 集成：[/bold]")
    console.print()
    code = """[white]$ [cyan]claude mcp add softpack[/cyan] -- softpack mcp[/white]
[dim]# Claude Code can now call softpack_compress automatically
# when context reaches ~70%[/dim]"""
    console.print(Panel(code, border_style="green", padding=(1, 2)))
    time.sleep(0.4)

    # ═══════════════════════════════════════════
    # Summary
    # ═══════════════════════════════════════════
    console.print()
    summary = Table(box=box.SIMPLE, show_header=False)
    summary.add_column(style="dim")
    summary.add_column(style="white")
    summary.add_row("📦 安装", "pip install softpack")
    summary.add_row("⚡ 依赖", "零！纯 Python 标准库")
    summary.add_row("🔒 隐私", "数据不出机器，无 API 调用")
    summary.add_row("🎯 定位", "LLM 压缩前的预压缩缓冲层")
    summary.add_row("📜 协议", "MIT — 随便用")
    console.print(Panel(summary, title="[bold]softpack 总结[/bold]", border_style="blue"))

    console.print()
    console.print("[dim]github.com/yang-qun-max/softpack[/dim]")


if __name__ == "__main__":
    main()
