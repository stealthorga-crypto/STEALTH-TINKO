import os


def flag(name: str, default: str = "off") -> bool:
    """Return True when an env flag is logically enabled.

    Accepts on/off, true/false, 1/0, yes/no (case-insensitive).
    Unknown -> default.
    """
    val = os.getenv(name, default)
    return str(val).strip().lower() in {"on", "true", "1", "yes"}
