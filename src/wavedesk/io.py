"""Load positions from a broker-style CSV (FR1, US7) and levels and quotes from JSON."""
from __future__ import annotations

import csv
import json
from datetime import date, datetime
from pathlib import Path

from .models import Kind, Level, LevelType, Position, Quote, Timeframe


class RowError(ValueError):
    pass


def load_positions(path: Path) -> tuple[list[Position], list[str]]:
    """Returns (positions, errors). Bad rows are reported for correction, not dropped silently."""
    positions, errors = [], []
    with open(path, newline="") as f:
        for n, row in enumerate(csv.DictReader(f), start=2):
            try:
                kind = Kind(row["kind"].strip().lower())
                if kind is not Kind.SHARE and (not row.get("strike") or not row.get("expiry")):
                    raise RowError("options need a strike and an expiry")
                positions.append(Position(
                    ticker=row["ticker"].strip().upper(),
                    kind=kind,
                    quantity=float(row["quantity"] or 0),
                    cost=float(row["cost"] or 0),
                    strike=float(row["strike"]) if row.get("strike") else None,
                    expiry=date.fromisoformat(row["expiry"]) if row.get("expiry") else None,
                    account=row.get("account") or "default",
                    watch_only=row.get("watch_only", "").strip().lower() in {"1", "true", "yes"},
                ))
            except (KeyError, ValueError) as e:
                errors.append(f"row {n}: {e}")
    return positions, errors


def load_levels(path: Path) -> list[Level]:
    raw = json.loads(Path(path).read_text())
    return [
        Level(
            ticker=r["ticker"].upper(),
            analyst=r["analyst"],
            level_type=LevelType(r["type"]),
            price=r.get("price"),
            chart_time=datetime.fromisoformat(r["chart_time"]),
            timeframe=Timeframe(r["timeframe"]),
            post_url=r["post_url"],
            price_scale=r.get("price_scale", "regular"),
            timing_ends=date.fromisoformat(r["timing_ends"]) if r.get("timing_ends") else None,
        )
        for r in raw
    ]


def load_quotes(path: Path) -> dict[str, Quote]:
    raw = json.loads(Path(path).read_text())
    return {
        r["ticker"].upper(): Quote(r["ticker"].upper(), r["price"], datetime.fromisoformat(r["as_of"]),
                                   r.get("price_scale", "regular"))
        for r in raw
    }
