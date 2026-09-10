"""
Role authentication for the two protected portals.

The credentials below are demonstration accounts for the public prototype. A
production deployment must replace this module with the department's identity
provider and must not carry passwords in source control.
"""

PORTAL_CREDENTIALS = {
    "government": {"admin": "mospi2026"},
    "contractor": {"contractor": "pass123"},
}


def authenticate(role: str, username: str, password: str) -> bool:
    """Returns True when the credentials are valid for that portal role."""
    accounts = PORTAL_CREDENTIALS.get(role, {})
    expected = accounts.get(username)
    return expected is not None and expected == password
