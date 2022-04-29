from typing import Any


# prevent xss attacks through viewing script tags in database
DISALLOWED_STRING_SYMBOLS = '<>'


def string(value: Any) -> bool:
    """
    Return
    - True if value is of type str
    - False otherwise
    """
    if not isinstance(value, str):
        return False

    for c in value:
        if c in DISALLOWED_STRING_SYMBOLS:
            return False

    return True


def number(value: Any) -> bool:
    """
    Return
    - True if value is of type int or float
    - False otherwise
    """
    if type(value) in (int, float):
        return True
    if type(value) == str:
        if value.isdigit():
            return True
    return False


def year(value: int) -> bool:
    """
    Return
    - True if value is between 1940 (exclusive) and 2040 (inclusive)
    - False otherwise
    """
    return (1940 < value <= 2040)


def leap_year(yyyy: int) -> bool:
    """
    Return
    - True if yyyy is a multiple of 4 (simple leap year)
    - False otherwise
    """
    return year(yyyy) and (yyyy % 4 == 0)


def date(value: str) -> bool:
    """
    Return
    - True if value is a valid str in YYYYMMDD format OR YYYY-MM-DD
    - False otherwise
    """
    # Type check
    if not string(value):
        return False

    # If YYYY-MM-DD format remove '-'
    if value.count('-') != 2:
        return False
    value = value.replace('-', '')

    # Length check
    if len(value) != 8:
        return False

    # Format check
    if not value.isdigit():
        return False

    y, m, d = int(value[:4]), int(value[4:6]), int(value[6:])

    # Format/Range check
    if not (1930 < y < 2030):
        return False
    if not (1 <= m <= 12):
        return False
    if (
        m in (1, 3, 5, 7, 8, 10, 12)
        and not (1 <= d <= 31)
    ):
        return False
    if (
        m in (4, 6, 9, 11)
        and not (1 <= d <= 30)
    ):
        return False
    if m == 2:
        if leap_year(y) and not (1 <= d <= 29):
            return False
        elif not leap_year(y) and not (1 <= d <= 28):
            return False
    return True
