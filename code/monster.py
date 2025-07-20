from game_data import MONSTER_DATA, ATTACK_DATA
from random import randint
from typing import *


class Monster:
    def __init__(self, name: str, level: int) -> None:
        self.name = name
        self.level = level
        self.paused = False

        # stats
        self.element: str = MONSTER_DATA[name]['stats']['element']
        self.base_stats: Dict[str, int] = MONSTER_DATA[name]['stats']
        self.health: int = self.base_stats['max_health'] * self.level
        self.energy: int = self.base_stats['max_energy'] * self.level
        self.initiative = randint(0, 100)
        self.abilities: Dict[int, str] = MONSTER_DATA[name]['abilities']
        self.defending = False

        # experience
        self.xp = 0
        self.level_up = self.level * 150
        self.evolution = MONSTER_DATA[self.name]['evolve']

    def __repr__(self) -> str:
        return f'Monster: {self.name}, Lvl: {self.level}'

    def get_stat(self, stat: str) -> int:
        return self.base_stats[stat] * self.level
    
    def get_stats(self) -> Dict[str, int]:
        return {
            'health': self.get_stat('max_health'),
            'energy': self.get_stat('max_energy'),
            'attack': self.get_stat('attack'),
            'defense': self.get_stat('defense'),
            'speed': self.get_stat('speed'),
            'recovery': self.get_stat('recovery')
        }
    
    def get_abilities(self, all: bool = True) -> List[str]:
        if all:
            return [ability for lvl, ability in self.abilities.items() if self.level >= lvl]
        else:
            return [ability for lvl, ability in self.abilities.items() if self.level >= lvl and ATTACK_DATA[ability]['cost'] < self.energy]

    def get_info(self):
        return (
            (self.health, self.get_stat('max_health')),
            (self.energy, self.get_stat('max_energy')),
            (self.initiative, 100)
        )
    
    def reduce_energy(self, attack: str):
        self.energy -= ATTACK_DATA[attack]['cost']
    
    def get_base_damage(self, attack: str) -> int:
        return self.get_stat('attack') * ATTACK_DATA[attack]['amount']

    def update_xp(self, amount: int) -> None:
        if self.level_up - self.xp > amount:
            self.xp += amount
        else:
            self.level += 1
            self.xp = amount - (self.level_up - self.xp)
            self.level_up = self.level * 150

    def stat_limiter(self):
        self.health = max(0, min(self.health, self.get_stat('max_health')))
        self.energy = max(0, min(self.energy, self.get_stat('max_energy')))

    def update(self, dt: float):
        self.stat_limiter()
        if not self.paused:
            self.initiative += self.get_stat('speed') * dt
