"""Unit tests for zodiac lookup logic."""

from __future__ import annotations

import unittest

from zodiac_gui.zodiac_logic import (
    ZodiacError,
    get_zodiac_sign,
    lookup,
    max_day_for_month,
    parse_month,
)


class ParseMonthTests(unittest.TestCase):
    def test_canonical_month(self) -> None:
        self.assertEqual(parse_month("March"), 3)

    def test_alias_febuary(self) -> None:
        self.assertEqual(parse_month("Febuary"), 2)

    def test_abbreviation(self) -> None:
        self.assertEqual(parse_month("jul"), 7)

    def test_empty_raises(self) -> None:
        with self.assertRaises(ZodiacError):
            parse_month("   ")

    def test_invalid_raises_without_echoing_input(self) -> None:
        with self.assertRaises(ZodiacError) as ctx:
            parse_month("NotAMonth")
        self.assertNotIn("NotAMonth", str(ctx.exception))

    def test_oversized_input_raises(self) -> None:
        with self.assertRaises(ZodiacError):
            parse_month("x" * 50)


class LookupTests(unittest.TestCase):
    def test_capricorn_early_january(self) -> None:
        result = lookup("January", 10)
        self.assertEqual(result.sign, "Capricorn")
        self.assertEqual(result.element, "Earth")

    def test_pisces_mid_march(self) -> None:
        result = lookup("March", 15)
        self.assertEqual(result.sign, "Pisces")
        self.assertEqual(result.element, "Water")

    def test_leo_late_july(self) -> None:
        result = lookup("July", 30)
        self.assertEqual(result.sign, "Leo")
        self.assertEqual(result.element, "Fire")

    def test_february_30_invalid(self) -> None:
        with self.assertRaises(ZodiacError):
            lookup("February", 30)

    def test_non_int_day_rejected(self) -> None:
        with self.assertRaises(ZodiacError):
            lookup("May", True)  # type: ignore[arg-type]

    def test_clipboard_text_contains_sign(self) -> None:
        result = lookup("April", 25)
        self.assertIn(result.sign, result.clipboard_text)
        self.assertIn(result.element, result.clipboard_text)


class MaxDayTests(unittest.TestCase):
    def test_february_max(self) -> None:
        self.assertEqual(max_day_for_month("February"), 29)

    def test_april_max(self) -> None:
        self.assertEqual(max_day_for_month("April"), 30)


class SignBoundaryTests(unittest.TestCase):
    def test_aquarius_starts_jan_20(self) -> None:
        self.assertEqual(get_zodiac_sign(1, 20), "Aquarius")

    def test_capricorn_ends_jan_19(self) -> None:
        self.assertEqual(get_zodiac_sign(1, 19), "Capricorn")


if __name__ == "__main__":
    unittest.main()
