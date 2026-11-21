import unittest
from datetime import date, datetime

from wavedesk.models import Kind, Level, LevelType, Position, Quote, Timeframe
from wavedesk import rules
from wavedesk.reconcile import reconcile

NOW = datetime(2026, 10, 23, 7, 0)


def lv(price, analyst="A", t=LevelType.TARGET, when=datetime(2026, 10, 22, 16, 0),
       tf=Timeframe.DAILY, scale="regular", timing=None, ticker="HIMS"):
    return Level(ticker, analyst, t, price, when, tf, "https://example.com/p", scale, timing)


class BusinessRules(unittest.TestCase):
    def test_br7_intraday_goes_stale_after_one_day(self):
        self.assertTrue(rules.is_stale(lv(10, tf=Timeframe.INTRADAY, when=datetime(2026, 10, 22, 6, 0)), NOW))
        self.assertFalse(rules.is_stale(lv(10, tf=Timeframe.INTRADAY, when=datetime(2026, 10, 22, 8, 0)), NOW))

    def test_br7_daily_allows_three_days(self):
        self.assertFalse(rules.is_stale(lv(10, when=datetime(2026, 10, 20, 8, 0)), NOW))
        self.assertTrue(rules.is_stale(lv(10, when=datetime(2026, 10, 19, 8, 0)), NOW))

    def test_br4_different_scales_are_not_compared(self):
        q = Quote("HIMS", 25.0, NOW, "regular")
        self.assertFalse(rules.comparable(lv(30, scale="split-adjusted"), q))
        self.assertTrue(rules.comparable(lv(30), q))

    def test_br6_agreement_needs_two_analysts_within_one_percent(self):
        self.assertTrue(rules.agree(lv(100.0, "A"), lv(100.9, "B"), NOW))
        self.assertFalse(rules.agree(lv(100.0, "A"), lv(101.5, "B"), NOW))
        self.assertFalse(rules.agree(lv(100.0, "A"), lv(100.5, "A"), NOW))

    def test_br6_stale_chart_cannot_agree(self):
        old = lv(100.2, "B", when=datetime(2026, 10, 10, 9, 0))
        self.assertFalse(rules.agree(lv(100.0, "A"), old, NOW))

    def test_br10_expiry_status(self):
        exp = date(2028, 1, 21)
        self.assertEqual(rules.expiry_status(lv(40, timing=date(2027, 6, 30)), exp), "before expiry")
        self.assertEqual(rules.expiry_status(lv(40, timing=date(2028, 6, 30)), exp), "after expiry")
        self.assertEqual(rules.expiry_status(lv(40), exp), "timing not stated")

    def test_br8_ticker_only_from_a_single_symbol_tag(self):
        self.assertEqual(rules.ticker_from_tags(["ma"]), "MA")
        self.assertIsNone(rules.ticker_from_tags([]))
        self.assertIsNone(rules.ticker_from_tags(["AMZN", "SHOP"]))


class Reconcile(unittest.TestCase):
    def test_break_even_for_call(self):
        p = Position("HIMS", Kind.CALL, 2, 6.85, strike=20, expiry=date(2028, 1, 21))
        self.assertAlmostEqual(p.break_even, 26.85)

    def test_nearest_levels_and_unreadable(self):
        p = Position("HIMS", Kind.SHARE, 10, 22.0)
        levels = [lv(24.1, t=LevelType.SUPPORT), lv(34.5), lv(41.0, "B"), lv(None, "C")]
        [view] = reconcile([p], levels, {"HIMS": Quote("HIMS", 26.35, NOW)}, NOW)
        self.assertEqual(view.nearest_below.price, 24.1)
        self.assertEqual(view.nearest_above.price, 34.5)
        self.assertEqual(len(view.unreadable), 1)

    def test_breached_invalidation_detected(self):
        p = Position("NVDA", Kind.SHARE, 15, 138.0)
        levels = [lv(148.0, "B", LevelType.INVALIDATION, ticker="NVDA")]
        [view] = reconcile([p], levels, {"NVDA": Quote("NVDA", 147.2, NOW)}, NOW)
        self.assertEqual(len(view.breached_invalidations), 1)


if __name__ == "__main__":
    unittest.main()
