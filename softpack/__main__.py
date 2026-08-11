"""
CLI entry point: python -m softpack or `softpack` command.
"""

import argparse
import sys

from softpack import compress, __version__


def main():
    parser = argparse.ArgumentParser(
        prog="softpack",
        description="Gentle pre-compression for AI agent context.",
    )

    sub = parser.add_subparsers(dest="command")

    # --- compress subcommand ---
    cmp = sub.add_parser("compress", help="Compress text from stdin or args")
    cmp.add_argument(
        "text", nargs="?", default=None,
        help="Text to compress. If not provided, reads from stdin."
    )
    cmp.add_argument(
        "-m", "--method", default="hybrid_lock",
        choices=["uniform", "hybrid_lock", "p0p1", "edge_preserve"],
        help="Compression method (default: hybrid_lock)."
    )
    cmp.add_argument(
        "-r", "--ratio", type=float, default=0.5,
        help="Target keep ratio in (0, 1] (default: 0.5)."
    )

    # --- hook subcommand ---
    hook = sub.add_parser("hook", help="Claude Code hook integration")
    hook.add_argument(
        "hook_cmd", nargs="?", default=None,
        choices=["pre-compact", "post-compact", "install"],
        help="Hook command: pre-compact | post-compact | install"
    )

    # --- mcp subcommand ---
    mcp = sub.add_parser("mcp", help="Run as MCP server (for Claude Code)")

    # --- version ---
    parser.add_argument("-v", "--version", action="version", version=f"softpack {__version__}")

    args = parser.parse_args()

    if args.command == "compress":
        text = args.text
        if text is None:
            text = sys.stdin.read()
        if not text.strip():
            print("Error: no text provided.", file=sys.stderr)
            sys.exit(1)

        try:
            result = compress(text, method=args.method, ratio=args.ratio)
        except ValueError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        print(result)

    elif args.command == "hook":
        from softpack.hooks import main as hook_main
        sys.argv = [sys.argv[0]]
        if args.hook_cmd:
            sys.argv.append(args.hook_cmd)
        hook_main()

    elif args.command == "mcp":
        from softpack.mcp_server import serve
        serve()

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
