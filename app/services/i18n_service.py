import json
import os
import logging
from typing import Dict

logger = logging.getLogger(__name__)

class I18nService:
    def __init__(self, locales_dir: str = "app/locales", default_lang: str = "en"):
        self.locales_dir = locales_dir
        self.default_lang = default_lang
        self.translations: Dict[str, Dict[str, str]] = {}
        self._load_translations()

    def _load_translations(self) -> None:
        if not os.path.exists(self.locales_dir):
            os.makedirs(self.locales_dir, exist_ok=True)
            return

        for filename in os.listdir(self.locales_dir):
            if filename.endswith(".json"):
                lang_code = filename[:-5]
                filepath = os.path.join(self.locales_dir, filename)
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        self.translations[lang_code] = json.load(f)
                except Exception as e:
                    logger.error(f"Failed to load translation file {filepath}: {e}")

    def gettext(self, key: str, lang: str = None) -> str:
        _lang = lang or self.default_lang
        
        # If translation exists for the specific language
        if _lang in self.translations and key in self.translations[_lang]:
            return self.translations[_lang][key]
            
        # Fallback to english translation if ukrainian is passed (assuming base language is UK)
        if self.default_lang in self.translations and key in self.translations[self.default_lang]:
            return self.translations[self.default_lang].get(key, key)
            
        return key

i18n_service = I18nService()
