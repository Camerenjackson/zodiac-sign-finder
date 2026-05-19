"""Zodiac sign and element lookup from birth month and day."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Final

ELEMENT_MESSAGES: Final[dict[str, str]] = {
    "Air": (
        "Air signs are rational, social, and love communication and relationships."
    ),
    "Earth": (
        "Earth signs are grounded and bring us down to earth. "
        "They are mostly conservative and realistic."
    ),
    "Fire": (
        "Fire signs tend to be passionate, dynamic, and temperamental. "
        "They get angry quickly, but they also forgive easily."
    ),
    "Water": (
        "Water signs are exceptionally emotional and ultra-sensitive."
    ),
}

SIGN_ELEMENTS: Final[dict[str, str]] = {
    "Aries": "Fire",
    "Taurus": "Earth",
    "Gemini": "Air",
    "Cancer": "Water",
    "Leo": "Fire",
    "Virgo": "Earth",
    "Libra": "Air",
    "Scorpio": "Water",
    "Sagittarius": "Fire",
    "Capricorn": "Earth",
    "Aquarius": "Air",
    "Pisces": "Water",
}

# Canonical month names
MONTHS: Final[list[str]] = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]

# Accept common spellings and abbreviations (including your original "Febuary")
MONTH_ALIASES: Final[dict[str, int]] = {}
for i, name in enumerate(MONTHS, start=1):
    MONTH_ALIASES[name.lower()] = i
    MONTH_ALIASES[name[:3].lower()] = i

MONTH_ALIASES.update(
    {
        "febuary": 2,
        "feb": 2,
        "sept": 9,
        "sep": 9,
        "oct": 10,
        "nov": 11,
        "dec": 12,
        "jan": 1,
        "mar": 3,
        "apr": 4,
        "jun": 6,
        "jul": 7,
        "aug": 8,
    }
)

# (month, day) on or after this date starts the sign (Western tropical zodiac)
_SIGN_STARTS: Final[list[tuple[int, int, str]]] = [
    (1, 20, "Aquarius"),
    (2, 19, "Pisces"),
    (3, 21, "Aries"),
    (4, 20, "Taurus"),
    (5, 21, "Gemini"),
    (6, 21, "Cancer"),
    (7, 23, "Leo"),
    (8, 23, "Virgo"),
    (9, 23, "Libra"),
    (10, 23, "Scorpio"),
    (11, 22, "Sagittarius"),
    (12, 22, "Capricorn"),
]

DAYS_IN_MONTH: Final[dict[int, int]] = {
    1: 31,
    2: 29,
    3: 31,
    4: 30,
    5: 31,
    6: 30,
    7: 31,
    8: 31,
    9: 30,
    10: 31,
    11: 30,
    12: 31,
}

SIGN_SYMBOLS: Final[dict[str, str]] = {
    "Aries": "♈",
    "Taurus": "♉",
    "Gemini": "♊",
    "Cancer": "♋",
    "Leo": "♌",
    "Virgo": "♍",
    "Libra": "♎",
    "Scorpio": "♏",
    "Sagittarius": "♐",
    "Capricorn": "♑",
    "Aquarius": "♒",
    "Pisces": "♓",
}

SIGN_DATE_RANGES: Final[dict[str, str]] = {
    "Aries": "March 21 – April 19",
    "Taurus": "April 20 – May 20",
    "Gemini": "May 21 – June 20",
    "Cancer": "June 21 – July 22",
    "Leo": "July 23 – August 22",
    "Virgo": "August 23 – September 22",
    "Libra": "September 23 – October 22",
    "Scorpio": "October 23 – November 21",
    "Sagittarius": "November 22 – December 21",
    "Capricorn": "December 22 – January 19",
    "Aquarius": "January 20 – February 18",
    "Pisces": "February 19 – March 20",
}

ELEMENT_COLORS: Final[dict[str, str]] = {
    "Fire": "#f97316",
    "Earth": "#84cc16",
    "Air": "#38bdf8",
    "Water": "#6366f1",
}

SIGNS_BY_ELEMENT: Final[dict[str, list[str]]] = {
    "Fire": ["Aries", "Leo", "Sagittarius"],
    "Earth": ["Taurus", "Virgo", "Capricorn"],
    "Air": ["Gemini", "Libra", "Aquarius"],
    "Water": ["Cancer", "Scorpio", "Pisces"],
}


@dataclass(frozen=True, slots=True)
class ZodiacResult:
    month_name: str
    day: int
    sign: str
    element: str
    element_message: str

    @property
    def symbol(self) -> str:
        return SIGN_SYMBOLS[self.sign]

    @property
    def date_range(self) -> str:
        return SIGN_DATE_RANGES[self.sign]

    @property
    def element_color(self) -> str:
        return ELEMENT_COLORS[self.element]

    @property
    def summary(self) -> str:
        return (
            f"Birthday: {self.month_name} {self.day}\n"
            f"Zodiac sign: {self.sign} ({self.symbol})\n"
            f"Element: {self.element}\n"
            f"Sign period: {self.date_range}"
        )

    @property
    def clipboard_text(self) -> str:
        return (
            f"{self.sign} {self.symbol}\n"
            f"Born: {self.month_name} {self.day}\n"
            f"Element: {self.element}\n"
            f"Period: {self.date_range}\n\n"
            f"{self.element_message}"
        )


class ZodiacError(ValueError):
    """Invalid month or day for lookup."""


_MAX_MONTH_INPUT_LEN = 32


def parse_month(month_input: str) -> int:
    if not isinstance(month_input, str):
        raise ZodiacError("Month must be text.")
    key = month_input.strip().lower()
    if len(key) > _MAX_MONTH_INPUT_LEN:
        raise ZodiacError("Month name is too long.")
    if not key:
        raise ZodiacError("Please choose a birth month.")
    if key in MONTH_ALIASES:
        return MONTH_ALIASES[key]
    raise ZodiacError("Not a valid month. Choose from the month list.")


def validate_day(month: int, day: int) -> None:
    if day < 1:
        raise ZodiacError("Day must be at least 1.")
    max_day = DAYS_IN_MONTH[month]
    if day > max_day:
        raise ZodiacError(f"Day must be between 1 and {max_day} for {MONTHS[month - 1]}.")


def get_zodiac_sign(month: int, day: int) -> str:
    """Return zodiac sign name for a valid calendar month (1–12) and day."""
    validate_day(month, day)
    sign = "Capricorn"
    for start_month, start_day, name in _SIGN_STARTS:
        if (month, day) >= (start_month, start_day):
            sign = name
    return sign


def max_day_for_month(month_input: str) -> int:
    month = parse_month(month_input)
    return DAYS_IN_MONTH[month]


def lookup(month_input: str, day: int) -> ZodiacResult:
    if not isinstance(day, int) or isinstance(day, bool):
        raise ZodiacError("Day must be a whole number.")
    month = parse_month(month_input)
    validate_day(month, day)
    sign = get_zodiac_sign(month, day)
    element = SIGN_ELEMENTS[sign]
    return ZodiacResult(
        month_name=MONTHS[month - 1],
        day=day,
        sign=sign,
        element=element,
        element_message=ELEMENT_MESSAGES[element],
    )
