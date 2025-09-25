import re


def validate_phone(phone: str) -> bool:
    """Validate phone number format: +7 and 10 digits"""
    return bool(re.match(r'^\+7\d{10}$', phone))


def validate_password(password: str) -> tuple[bool, str]:
    """Validate password requirements"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"

    if not re.match(r'^[a-zA-Z]', password):
        return False, "Password must contain only latin characters"

    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"

    if not re.search(r'[$%&!:]', password):
        return False, "Password must contain at least one special character ($%&!:)"

    return True, "Valid password"