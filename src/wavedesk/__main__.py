"""Command line: python -m wavedesk data/positions.csv data/levels.json data/quotes.json --now 2026-10-23T07:00"""
from __future__ import annotations

import argparse
import sys
from datetime import datetime
from pathlib import Path

from .brief import render
from .io import load_levels, load_positions, load_quotes
from .reconcile import reconcile


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(prog="wavedesk", description="Build the daily brief from sample data.")
    ap.add_argument("positions", type=Path)
    ap.add_argument("levels", type=Path)
    ap.add_argument("quotes", type=Path)
    ap.add_argument("--now", default=None, help="ISO time in Eastern Time (default: now)")
    args = ap.parse_args(argv)

    now = datetime.fromisoformat(args.now) if args.now else datetime.now()
    positions, errors = load_positions(args.positions)
    for e in errors:
        print(f"[import] {e}", file=sys.stderr)
    views = reconcile(positions, load_levels(args.levels), load_quotes(args.quotes), now)
    print(render(views, now))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
