# Changelog

## [0.1.0] — 2026-08-11

### Added
- 4 compression methods: `uniform`, `hybrid_lock`, `p0p1`, `edge_preserve`
- `hybrid_lock` — lock ASCII/tech entities, uniformly compress Chinese prose
- CLI: `softpack compress` with pipe and argument support
- MCP Server for Claude Code integration
- PreCompact hook: save compressed snapshot before LLM compaction
- SessionStart(compact) hook: restore preserved context after compaction
- `softpack hook install` — one-command setup for Claude Code hooks
- `softpack_compress` convenience function (hybrid_lock at 50%)
- Rich terminal demo (`demo_rich.py`)
- 29 tests, all passing
- Ratio validation: (0, 1], rejects 0.0 and >1.0
- Structured error handling in CLI and MCP server

### Fixed
- Docstring restoration: ratio validation moved after docstring
- p0p1 DROP set: removed 不/我/你/他/哈 to prevent semantic corruption
- CLI help text: ratio range shown as (0, 1]
