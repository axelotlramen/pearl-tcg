from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from pearl_tcg.enums import AbilityType, Path


@dataclass(frozen=True)
class Mark:
    """Generic attachable metadata - the same small type is used both for persistent state on a
    Boss (e.g. a debuff waiting to be exploited) and for future attachments on an ActionCard
    itself (e.g. a shop-purchased Wildcard). pearl_tcg doesn't interpret what any Mark means -
    only pearl_tcg_assets' combo resolvers assign or read one."""

    type: AbilityType | None = None
    path: Path | None = None
    tag: str = ""
