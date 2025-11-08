"""
Request ID generation utilities.
"""
import time
import random
import os


def ulid() -> str:
    """
    Generate a simple ULID-like identifier.
    Format: timestamp (10 chars) + random (16 chars)
    """
    timestamp = int(time.time() * 1000)  # milliseconds
    random_part = "".join(
        random.choices("0123456789ABCDEFGHJKMNPQRSTVWXYZ", k=16)
    )
    timestamp_part = base32_encode(timestamp, 10)
    return f"{timestamp_part}{random_part}"


def base32_encode(num: int, length: int) -> str:
    """Simple base32 encoding for timestamp."""
    alphabet = "0123456789ABCDEFGHJKMNPQRSTVWXYZ"
    result = []
    while num > 0 and len(result) < length:
        num, remainder = divmod(num, 32)
        result.append(alphabet[remainder])
    while len(result) < length:
        result.append("0")
    return "".join(reversed(result))


def request_id(header_value: str | None = None) -> str:
    """
    Get or generate a request ID.
    If header_value is provided, use it; otherwise generate a new ULID.
    """
    if header_value:
        return header_value.strip()
    return ulid()
