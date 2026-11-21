"""Match published levels to positions and build one dashboard row per position (FR7, FR8, FR12)."""
from __future__ import annotations

from datetime import datetime
from itertools import combinations
from typing import Iterable

from .models import Level, LevelType, Position, PositionView, Quote
from . import rules


def reconcile(
    positions: Iterable[Position],
    levels: Iterable[Level],
    quotes: dict[str, Quote],
    now: datetime,
) -> list[PositionView]:
    by_ticker: dict[str, list[Level]] = {}
    for lv in levels:
        by_ticker.setdefault(lv.ticker.upper(), []).append(lv)

    views = []
    for pos in positions:
        quote = quotes.get(pos.ticker.upper())
        view = PositionView(position=pos, quote=quote)
        ticker_levels = by_ticker.get(pos.ticker.upper(), [])
        if ticker_levels:
            view.last_covered = max(lv.chart_time for lv in ticker_levels)

        fresh = []
        for lv in ticker_levels:
            if lv.price is None:
                view.unreadable.append(lv)          # BR9: never guess
            elif rules.is_stale(lv, now):
                view.stale.append(lv)               # BR7: label, do not delete
            else:
                fresh.append(lv)

        view.invalidations = [lv for lv in fresh if lv.level_type is LevelType.INVALIDATION]

        if quote is not None:
            usable = [lv for lv in fresh if rules.comparable(lv, quote)]
            below = [lv for lv in usable if lv.price <= quote.price]
            above = [lv for lv in usable if lv.price > quote.price]
            view.nearest_below = max(below, key=lambda lv: lv.price, default=None)
            view.nearest_above = min(above, key=lambda lv: lv.price, default=None)
            view.nearest_target_above = min(
                (lv for lv in above if lv.level_type is LevelType.TARGET), key=lambda lv: lv.price, default=None
            )
            # A long position's invalidation is breached when price trades through it from above.
            view.breached_invalidations = [
                lv for lv in view.invalidations if rules.comparable(lv, quote) and quote.price < lv.price
            ]

        view.agreements = [(a, b) for a, b in combinations(fresh, 2) if rules.agree(a, b, now)]

        if pos.expiry is not None:
            view.expiry_check = [
                (lv, rules.expiry_status(lv, pos.expiry))
                for lv in fresh
                if lv.level_type is LevelType.TARGET
            ]
        views.append(view)
    return views
