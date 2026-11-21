"""Core data types. Mirrors the Lab 3 data model (Portfolio, Level Data, Market groups)."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional


class Kind(str, Enum):
    SHARE = "share"
    CALL = "call"
    PUT = "put"


class LevelType(str, Enum):
    TARGET = "target"
    SUPPORT = "support"
    RESISTANCE = "resistance"
    INVALIDATION = "invalidation"


class Timeframe(str, Enum):
    INTRADAY = "intraday"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass(frozen=True)
class Position:
    ticker: str
    kind: Kind
    quantity: float
    cost: float                       # per share, or per contract premium per share
    strike: Optional[float] = None
    expiry: Optional[date] = None
    account: str = "default"
    watch_only: bool = False          # watch-list entries carry no quantity or cost

    @property
    def break_even(self) -> Optional[float]:
        """Underlying price at which the position stops losing money at expiry."""
        if self.watch_only:
            return None
        if self.kind is Kind.SHARE:
            return self.cost
        if self.strike is None:
            raise ValueError(f"{self.ticker}: option without a strike")
        return self.strike + self.cost if self.kind is Kind.CALL else self.strike - self.cost


@dataclass(frozen=True)
class Level:
    ticker: str               # always from the post's symbol tag (BR8)
    analyst: str
    level_type: LevelType
    price: Optional[float]    # None = unreadable, sent to review queue (BR9)
    chart_time: datetime      # post time in Eastern Time (BR13)
    timeframe: Timeframe
    post_url: str             # every level traceable to its post (BR2)
    price_scale: str = "regular"     # e.g. "regular", "split-adjusted", contract month (BR4)
    timing_ends: Optional[date] = None   # analyst's stated timing for a target (BR10)


@dataclass(frozen=True)
class Quote:
    """A live price. Never confused with a chart price (BR3)."""
    ticker: str
    price: float
    as_of: datetime
    price_scale: str = "regular"


@dataclass
class PositionView:
    """One dashboard row (FR7)."""
    position: Position
    quote: Optional[Quote]
    nearest_below: Optional[Level] = None
    nearest_above: Optional[Level] = None
    nearest_target_above: Optional[Level] = None
    invalidations: list[Level] = field(default_factory=list)
    stale: list[Level] = field(default_factory=list)
    unreadable: list[Level] = field(default_factory=list)
    agreements: list[tuple[Level, Level]] = field(default_factory=list)
    expiry_check: list[tuple[Level, str]] = field(default_factory=list)
    breached_invalidations: list[Level] = field(default_factory=list)
    last_covered: Optional[datetime] = None
