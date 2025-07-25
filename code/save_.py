import os
import json
from singleton import SingletonMeta
from support import get_path
from typing import Optional, Any

class Save(metaclass=SingletonMeta):
    def __init__(self):
        self.load()

    def load(self):
        with open(get_path("save", "player.json"), "r", encoding="utf-8") as f:
            self._data = json.load(f)

    def get(self, key: str, default: Optional[Any] = None):
        return self._data.get(key)
        