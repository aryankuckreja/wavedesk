"""Business rules from the Lab 3 analysis. Each function names the rule it enforces."""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import Optional

from .models import Level, LevelType, Quote, Timeframe

AGREEMENT_TOLERANCE = 0.01          # BR6: within 1%
INTRADAY_MAX_AGE = timedelta(days=1)    # BR7: 1 trading day for intraday charts
DAILY_MAX_AGE = timedelta(days=3)       # BR7: 3 days for daily and weekly charts


def is_stale(level: Level, now: datetime) -> bool:
    """BR7: stale levels are labelled, never deleted."""
    limit = INTRADAY_MAX_AGE if level.timeframe is Timeframe.INTRADAY else DAILY_MAX_AGE
    return now - level.chart_time > limit


def comparable(level: Level, quote: Quote) -> bool:
    """BR4: only compare prices on the same scale and contract."""
    return level.price is not None and level.price_scale == quote.price_scale


def agree(a: Level, b: Level, now: datetime) -> bool:
    """BR6: two analysts agree only within 1% and when both charts are fresh."""
    if a.analyst == b.analyst or a.price is None or b.price is None:
        return False
    if a.price_scale != b.price_scale or is_stale(a, now) or is_stale(b, now):
        return False
    return abs(a.price - b.price) / max(a.price, b.price) <= AGREEMENT_TOLERANCE


def expiry_status(level: Level, expiry: Optional[date]) -> str:
    """BR10: 'before expiry' only when the analyst's stated timing ends before expiry."""
    if level.level_type is not LevelType.TARGET or expiry is None:
        return "not applicable"
    if level.timing_ends is None:
        return "timing not stated"
    return "before expiry" if level.timing_ends <= expiry else "after expiry"


def ticker_from_tags(symbol_tags: list[str]) -> Optional[str]:
    """BR8: a ticker comes only from the post's symbol tag, never from words in the text."""
    tags = [t.strip().upper() for t in symbol_tags if t and t.strip()]
    return tags[0] if len(tags) == 1 else None
