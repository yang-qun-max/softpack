"""
Claude Code hook integration for softpack.

Provides:
  softpack hook pre-compact  — run before LLM compaction, save compressed snapshot
  softpack hook post-compact — restore compressed snapshot after compaction
  softpack hook install      — set up hooks in .claude/settings.json
"""

import json
import os
import sys
import time
from pathlib import Path

from softpack import softpack_compress, __version__

CACHE_DIR = Path.home() / ".softpack"
SNAPSHOT_FILE = CACHE_DIR / "pre_compact_snapshot.json"


def pre_compact():
    """
    PreCompact hook: save a softpack-compressed snapshot before LLM compaction fires.

    Reads stdin (the PreCompact hook input JSON), extracts conversation context,
    compresses it with softpack, and saves to disk.

    Then exits 0 to allow compaction to proceed.
    """
    CACHE_DIR.mkdir(parents=True, exist_ok=True)

    # Read hook input (PreCompact provides conversation metadata)
    try:
        hook_input = json.loads(sys.stdin.read()) if not sys.stdin.isatty() else {}
    except json.JSONDecodeError:
        hook_input = {}

    trigger = hook_input.get("trigger", "auto")
    message_count = hook_input.get("messageCount", 0)

    # Build a textual snapshot of what we know
    snapshot_parts = []

    # Include project context if available
    project_dir = hook_input.get("projectDir", "")
    if project_dir:
        snapshot_parts.append(f"[Project: {project_dir}]")

    snapshot_parts.append(f"[PreCompact trigger={trigger}, messageCount={message_count}]")

    snapshot_text = " | ".join(snapshot_parts)

    # In production, the hook could read recent conversation from the
    # JSONL transcript file in ~/.claude/projects/<hash>/
    snapshot = {
        "timestamp": time.time(),
        "version": __version__,
        "trigger": trigger,
        "message_count": message_count,
        "compressed_context": softpack_compress(snapshot_text),
        "project_dir": project_dir,
    }

    with open(SNAPSHOT_FILE, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, ensure_ascii=False, indent=2)

    # Always exit 0 - let compaction proceed (fail-open design)
    sys.exit(0)


def post_compact():
    """
    SessionStart(matcher:compact) hook: after compaction, inject softpack
    compressed snapshot back into context via additionalContext.
    """
    if not SNAPSHOT_FILE.exists():
        # No snapshot - nothing to inject
        print(json.dumps({"decision": "continue"}))
        sys.exit(0)

    try:
        with open(SNAPSHOT_FILE, "r", encoding="utf-8") as f:
            snapshot = json.load(f)
    except (json.JSONDecodeError, IOError):
        print(json.dumps({"decision": "continue"}))
        sys.exit(0)

    # Check if snapshot is fresh (within last 5 minutes)
    age = time.time() - snapshot.get("timestamp", 0)
    if age > 300:
        # Stale snapshot - skip
        SNAPSHOT_FILE.unlink(missing_ok=True)
        print(json.dumps({"decision": "continue"}))
        sys.exit(0)

    # Build additionalContext to inject
    ctx = snapshot.get("compressed_context", "")
    project = snapshot.get("project_dir", "")

    context_text = (
        "[softpack] Pre-compaction snapshot preserved. "
        "Key project context before compaction:\n"
        f"{ctx}"
    )

    output = {
        "decision": "continue",
        "additionalContext": context_text,
    }

    print(json.dumps(output, ensure_ascii=False))

    # Clean up after successful injection
    SNAPSHOT_FILE.unlink(missing_ok=True)
    sys.exit(0)


def install_hooks():
    """
    Install softpack hooks into .claude/settings.json

    Adds:
    - PreCompact: softpack hook pre-compact (save snapshot before compaction)
    - SessionStart(matcher:"compact"): softpack hook post-compact (restore after)
    """
    settings_path = Path.cwd() / ".claude" / "settings.json"

    if not settings_path.parent.exists():
        print("Error: .claude/ directory not found in current project.", file=sys.stderr)
        print("Run this from your project root (where CLAUDE.md lives).", file=sys.stderr)
        sys.exit(1)

    # Read existing settings
    if settings_path.exists():
        with open(settings_path, "r", encoding="utf-8") as f:
            try:
                settings = json.load(f)
            except json.JSONDecodeError:
                print(f"Error: {settings_path} is not valid JSON.", file=sys.stderr)
                sys.exit(1)
    else:
        settings = {}

    # Ensure hooks dict exists
    if "hooks" not in settings:
        settings["hooks"] = {}

    hooks = settings["hooks"]

    # PreCompact hook
    precompact_hook = {
        "matcher": "",
        "hooks": [
            {
                "type": "command",
                "command": "softpack hook pre-compact"
            }
        ]
    }

    # Check if softpack PreCompact already installed
    existing_precompact = hooks.get("PreCompact", [])
    already_installed_pre = any(
        "softpack hook pre-compact" in json.dumps(h)
        for h in existing_precompact
    )

    if not already_installed_pre:
        if "PreCompact" not in hooks:
            hooks["PreCompact"] = []
        hooks["PreCompact"].append(precompact_hook)
        print("+ Added PreCompact hook -> softpack saves snapshot before compaction")
    else:
        print("  PreCompact hook already installed - skipping")

    # SessionStart(matcher:compact) hook
    postcompact_hook = {
        "matcher": "compact",
        "hooks": [
            {
                "type": "command",
                "command": "softpack hook post-compact"
            }
        ]
    }

    existing_session = hooks.get("SessionStart", [])
    already_installed_post = any(
        "softpack hook post-compact" in json.dumps(h)
        for h in existing_session
    )

    if not already_installed_post:
        if "SessionStart" not in hooks:
            hooks["SessionStart"] = []
        hooks["SessionStart"].append(postcompact_hook)
        print("+ Added SessionStart(compact) hook -> softpack restores snapshot after compaction")
    else:
        print("  SessionStart(compact) hook already installed - skipping")

    # Write back
    with open(settings_path, "w", encoding="utf-8") as f:
        json.dump(settings, f, indent=2, ensure_ascii=False)
        f.write("\n")

    print()
    print("softpack hooks installed!")
    print(f"   Config: {settings_path}")
    print()
    print("What happens now:")
    print("  1. Before LLM compaction -> softpack saves compressed snapshot")
    print("  2. After LLM compaction    -> softpack injects preserved context")
    print()
    print("To remove: delete the softpack entries from .claude/settings.json")


def main():
    if len(sys.argv) < 2:
        print("Usage: softpack hook <pre-compact|post-compact|install>", file=sys.stderr)
        sys.exit(1)

    subcommand = sys.argv[1]

    if subcommand == "pre-compact":
        pre_compact()
    elif subcommand == "post-compact":
        post_compact()
    elif subcommand == "install":
        install_hooks()
    else:
        print(f"Unknown hook command: {subcommand}", file=sys.stderr)
        print("Usage: softpack hook <pre-compact|post-compact|install>", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
