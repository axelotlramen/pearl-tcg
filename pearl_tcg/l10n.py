from __future__ import annotations

import pathlib
from typing import Any

import yaml
from discord import Locale

from durin_tcg.utils.logger import LOGGER

L10N_PATH = pathlib.Path("./l10n")
DEFAULT_LANG = "en_US"
DEFAULT_LOCALE = Locale.american_english


class LocaleStr:
    def __init__(
        self, key: str, translate: bool = True, default: str | None = None, **kwargs: Any
    ) -> None:
        self.key = key
        self.translate_ = translate
        self.default = default
        self.kwargs = kwargs

    def translate(self, locale: Locale) -> str:
        return translator.translate(self, locale)


class Translator:
    def __init__(self) -> None:
        super().__init__()

        self.logger = LOGGER
        self._l10n: dict[str, dict[str, str]] = {}

        self.load_l10n_files()

    def load_l10n_files(self) -> None:
        for file_path in L10N_PATH.glob("*.yaml"):
            lang = file_path.stem
            with file_path.open("r", encoding="utf-8") as f:
                self._l10n[lang] = yaml.safe_load(f)

    def translate(
        self, string: LocaleStr | str, locale: Locale = DEFAULT_LOCALE, **kwargs: Any
    ) -> str:
        if isinstance(string, str):
            return string

        source_string = self._l10n[DEFAULT_LANG].get(string.key)

        if string.translate_ and source_string is None:
            self.logger.warning("String %r is missing in source lang file", string.key)

        lang = locale.value.replace("-", "_")
        translation = self._l10n.get(lang, {}).get(string.key)

        translation = translation or string.default or source_string or string.key

        combined_kwargs = {**string.kwargs, **kwargs}
        return translation.format(**combined_kwargs)


# Singleton translator instance
translator = Translator()
