from __future__ import annotations


class InvalidAbilityUseError(Exception):
    """Raised when an ability is used in an invalid context (e.g. all enemies are dead)."""
