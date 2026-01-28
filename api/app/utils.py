import secrets
import string


def generate_agent_id(name: str, hash_length: int = 5) -> str:
    """Generate a unique agent ID in format {name}-{hash}.

    Args:
        name: The agent name to use as prefix.
        hash_length: Length of the random hash suffix.

    Returns:
        A unique ID like "my-agent-a1b2c".
    """
    charset = string.ascii_lowercase + string.digits
    hash_part = "".join(secrets.choice(charset) for _ in range(hash_length))
    return f"{name}-{hash_part}"
