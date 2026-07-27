from __future__ import annotations

import importlib.util
import pathlib
import sys

from durin_tcg.config import CONFIG
from durin_tcg.models.cards import Card

CARD_ROOT = pathlib.Path(CONFIG.card_root)


def read_cards() -> dict[str, Card]:
    all_cards: dict[str, Card] = {}

    for subfolder in CARD_ROOT.iterdir():
        if not subfolder.is_dir():
            continue

        for file in subfolder.glob("*.py"):
            module_name = f"{subfolder.name}.{file.stem}"
            spec = importlib.util.spec_from_file_location(module_name, file)
            if spec is None or spec.loader is None:
                continue

            module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = module
            spec.loader.exec_module(module)

            # Find the class that inherits from Card
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (
                    isinstance(attr, type)
                    and issubclass(attr, Card)
                    and attr is not Card
                    and attr.__name__ not in {"GenshinCard", "HSRCard", "ZZZCard"}
                ):
                    card_instance = attr()  # pyright: ignore[reportCallIssue]
                    all_cards[card_instance.name] = card_instance

    return all_cards
