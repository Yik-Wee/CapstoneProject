import string as char
from typing import Any

valid_domain_char = char.ascii_letters + char.digits + '._-'
valid_user_char = valid_domain_char + '+'

def true(value=None) -> bool:
    # Always returns True
    return True

def false(value=None) -> bool:
    # Always returns False
    return False

def string(value: Any) -> bool:
    """
    Return
    - True if value is of type str
    - False otherwise
    """
    return (
        type(value) is str
    )

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

def singapore_number(value: str) -> bool:
    """
    Return
    - True if value is a valid Singapore contact number
      (Eight digits starting with 6, 8, or 9)
    - False otherwise
    """
    # Type check
    if not string(value):
        return False
    # Length check
    if len(value) != 8:
        return False
    # Format check
    if not value.isdigit():
        return False
    if value[0] not in '689':
        return False
    return True

def foreign_number(value: str) -> bool:
    """
    Return
    - True if value is a valid foreign contact number
      consists of optional starting '+', and digits only
    - False otherwise
    """
    if not string(value):
        return False
    if not value.isdigit():
        return False
    if value[0] not in '689':
        return False
    return True

def contact_number(value: str) -> bool:
    """
    Return
    - True if value is a valid singapore or foreign number
    - False otherwise
    """
    return (
        singapore_number(value) or foreign_number(value)
    )

def username(value: str) -> bool:
    """
    Return
    - True if value is a valid username
      - contains only letters, numbers, or '._-+'
    - False otherwise
    """
    # Length check
    if len(value) == 0:
        return False
    # Range check
    for ch in value:
        if ch not in valid_user_char:
            return False
    return True

def domain(value: str) -> bool:
    """
    Return
    - True if value is a valid domain
      - has only one or two '.'
      - contains only letters, numbers, or '.-_'
    - False otherwise
    """
    # Length check
    if len(value) == 0:
        return False
    # Range check
    if not (0 < value.count('.') <= 2):
        return False
    for ch in value:
        if ch not in valid_domain_char:
            return False
    return True

def email(value: str) -> bool:
    """
    Return
    - True if value is a valid email address
      - has only one @
      - username and domain are valid
      - username contains only letters, numbers, or '._-+'
      - domain has only one or two '.'
      - domain contains only letters, numbers, or '.-_'
    - False otherwise
    """
    # Type check
    if not string(value):
        return False
    # Format check
    if value.count('@') != 1:
        return False

    user, domain = value.split('@')
    if not username(user):
        return False
    if not domain(domain):
        return False
    return True

def nyjc_email(value: str) -> bool:
    """
    Assume value is a valid email.

    Return
    - True if value is a valid NYJC email address
      (domain: nyjc.edu.sg)
    - False otherwise
    """
    user, domain = value.split('@')
    if not domain == 'nyjc.edu.sg':
        return False
    return True

def moe_email(value: str) -> bool:
    """
    Assume value is a valid email.

    Return
    - True if value is a valid MOE email address
      (domain: moe.edu.sg)
    - False otherwise
    """
    user, domain = value.split('@')
    if not domain == 'moe.edu.sg':
        return False
    return True

def gov_email(value: str) -> bool:
    """
    Assume value is a valid email.

    Return
    - True if value is a valid Gov email address
      (domain: schools.gov.sg)
    - False otherwise
    """
    user, domain = value.split('@')
    if not domain == 'schools.gov.sg':
        return False
    return True

def approved_email(value: str) -> bool:
    """
    Assume value is a valid email.

    Return
    - True if value is an approved email address
      (NYJC, MOE, or Gov)
    - False otherwise
    """
    if not nyjc_email(value):
        return False
    if not moe_email(value):
        return False
    if not gov_email(value):
        return False
    return True

def contains(options: list, choice: str) -> bool:
    """
    Return
    - True if choice is in options
    - False otherwise
    """
    return (choice in options)
