from __future__ import annotations

import importlib.util
import pathlib
import sys
from typing import TYPE_CHECKING

from pearl_tcg.config import CONFIG
from pearl_tcg.models.battle.combo_rules import ComboResolver

if TYPE_CHECKING:
    from types import ModuleType

    from pearl_tcg.models.cards import Card

COMBO_ROOT = pathlib.Path(CONFIG.combo_root)


def load_combo_module(stem: str) -> ModuleType:
    """Dynamically load (and cache) `<COMBO_ROOT>/<stem>.py` as `combos.<stem>` - the same
    file-path-based loading `read_combos()` uses for resolvers, but callable by name from
    anywhere (e.g. a card file in `cards/`) regardless of whether `read_combos()` has run yet.
    Checking `sys.modules` first keeps this idempotent no matter who asks for it first."""
    module_name = f"combos.{stem}"
    cached = sys.modules.get(module_name)
    if cached is not None:
        return cached

    file = COMBO_ROOT / f"{stem}.py"
    spec = importlib.util.spec_from_file_location(module_name, file)
    if spec is None or spec.loader is None:
        msg = f"Could not load combo module {stem!r} from {file}"
        raise ImportError(msg)

    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)
    return module


def read_combos() -> list[ComboResolver]:
    resolvers: list[ComboResolver] = []

    for file in COMBO_ROOT.glob("*.py"):
        module = load_combo_module(file.stem)

        # Find the class actually defined in this module (not merely imported into it)
        # that inherits from ComboResolver - excludes ComboResolver itself, which is only
        # ever imported here, never defined here.
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            if (
                isinstance(attr, type)
                and issubclass(attr, ComboResolver)
                and attr.__module__ == module.__name__
            ):
                resolvers.append(attr())

    # Sort rather than relying on glob() order, which isn't guaranteed - resolver `priority`
    # is meant to be a real, reproducible execution order, not whatever the filesystem returns.
    resolvers.sort(key=lambda resolver: (resolver.priority, resolver.name))
    return resolvers


def validate_combo_tags(cards: dict[str, Card], resolvers: list[ComboResolver]) -> list[str]:
    """Return every distinct combo_tag used by a card's abilities that no loaded resolver
    recognizes - catches a typo'd tag that would otherwise silently do nothing."""
    recognized: set[str] = set()
    for resolver in resolvers:
        recognized |= resolver.recognized_tags

    used: set[str] = set()
    for card in cards.values():
        for ability in (card.basic, card.skill, card.talent, card.ultimate):
            if ability.combo_tag:
                used.add(ability.combo_tag)

    return sorted(used - recognized)
