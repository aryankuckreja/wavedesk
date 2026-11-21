"""The daily brief (FR11, US5). Reports what analysts posted; never recommends (BR11)."""
from __future__ import annotations

from datetime import datetime

from .models import PositionView

DISCLAIMER = (
    "WaveDesk reports levels exactly as analysts published them, credited to each analyst. "
    "It does not give investment advice."
)


def _lv(level) -> str:
    return f"{level.price:,.2f} ({level.level_type.value}, Analyst {level.analyst})"


def _price(view: PositionView) -> str:
    q = view.quote
    return f"{q.price:,.2f} live as of {q.as_of:%H:%M} ET" if q else "no live price"


def render(views: list[PositionView], now: datetime) -> str:
    held = [v for v in views if not v.position.watch_only]
    watch = [v for v in views if v.position.watch_only]
    out = [f"# WaveDesk brief, {now:%a %b %d %Y, %H:%M} ET", ""]

    out += ["## 1. Anything on what I already own?", ""]
    flagged = False
    for v in held:
        p = v.position
        notes = []
        if v.breached_invalidations:
            notes.append("price is below " + ", ".join(_lv(lv) for lv in v.breached_invalidations))
        be = p.break_even
        t = v.nearest_target_above
        if t and be is not None:
            side = "above" if t.price >= be else "below"
            notes.append(f"nearest target {_lv(t)} is {side} break-even {be:,.2f}")
        late = [lv for lv, status in v.expiry_check if status == "after expiry"]
        if late:
            notes.append("target timing after expiry: " + ", ".join(_lv(lv) for lv in late))
        if v.stale:
            notes.append(f"{len(v.stale)} stale level(s) labelled, not shown as current")
        if v.unreadable:
            notes.append(f"{len(v.unreadable)} unreadable level(s) sent to review")
        if notes:
            flagged = True
            label = p.ticker if p.kind.value == "share" else f"{p.ticker} {p.strike:g} {p.kind.value} {p.expiry:%b %Y}"
            out.append(f"- **{label}** at {_price(v)}")
            out += [f"  - {n}" for n in notes]
    if not flagged:
        out.append("- Nothing new on held positions.")
    out.append("")

    out += ["## 2. Anything on my watch list?", ""]
    near = []
    for v in watch:
        if v.quote and v.nearest_below and v.quote.price - v.nearest_below.price <= 0.02 * v.quote.price:
            near.append(f"- **{v.position.ticker}** at {_price(v)} is within 2% of {_lv(v.nearest_below)}")
    out += near or ["- No watch-list stock is near a published level."]
    out.append("")

    out += ["## 3. Where do analysts agree?", ""]
    agreements = [(v, a, b) for v in views for a, b in v.agreements]
    if agreements:
        for v, a, b in agreements:
            out.append(f"- **{v.position.ticker}**: Analyst {a.analyst} {a.price:,.2f} and Analyst {b.analyst} {b.price:,.2f} "
                       f"are within 1% (both {a.level_type.value}/{b.level_type.value}, fresh charts)")
    else:
        out.append("- No fresh levels within 1% of each other.")
    out += ["", f"_{DISCLAIMER}_", ""]
    return "\n".join(out)
