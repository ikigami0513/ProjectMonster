import os
import json
from typing import Union


class Data:
    _cache = {}
    path: str = ""

    @classmethod
    def get(cls, id: Union[str, int]):
        cached_data = cls._cache.get(id)
        if cached_data is None:
            with open(os.path.join(cls.path, f"{id}.json"), "r", encoding="utf-8") as f:
                cached_data = json.load(f)
                cls._cache[id] = cached_data
        return cached_data
    
    @classmethod
    def all(cls):
        all_data = []
        for filename in os.listdir(cls.path):
            if filename.lower().endswith(".json"):
                id = filename.split(".")[0]
                data = cls.get(id)
                all_data.append(data)

        return all_data
    

class TrainerData(Data):
    path = "data/trainers/"


class MonsterData(Data):
    path = "data/monsters/"


class AttackData(Data):
    path = "data/attacks/"
