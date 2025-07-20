import pygame
from settings import *
from typing import Tuple, List, Dict, Callable
from types_utils import GroupsArgument
from monster import Monster
from random import uniform
from support import draw_bar
from timer_ import Timer

# region overworld sprites

class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos: Tuple[float, float], surf: pygame.Surface, groups: GroupsArgument, z = WORLD_LAYERS['main']):
        super().__init__(groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft = pos)
        self.z = z
        self.y_sort = self.rect.centery
        self.hitbox = self.rect.copy()


class BorderSprite(Sprite):
    def __init__(self, pos: Tuple[float, float], surf: pygame.Surface, groups: GroupsArgument):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.copy()


class TransitionSprite(Sprite):
    def __init__(self, pos: Tuple[float, float], size: Tuple[float, float], target: Tuple[str, str], groups: GroupsArgument):
        surf = pygame.Surface(size)
        super().__init__(pos, surf, groups)
        self.target = target


class CollidableSprite(Sprite):
    def __init__(self, pos: Tuple[float, float], surf: pygame.Surface, groups: GroupsArgument):
        super().__init__(pos, surf, groups)
        self.hitbox = self.rect.inflate(0, -self.rect.height * 0.6)


class MonsterPatchSprite(Sprite):
    def __init__(self, pos: Tuple[float, float], surf: pygame.Surface, groups: GroupsArgument, biome: str, monsters: str, level: int):
        self.biome = biome
        super().__init__(pos, surf, groups, WORLD_LAYERS['main' if biome != 'sand' else 'bg'])
        self.y_sort -= 40
        self.monsters = monsters.split(',')
        self.level = level


class AnimatedSprite(Sprite):
    def __init__(self, pos: Tuple[float, float], frames: List[pygame.Surface], groups: GroupsArgument, z = WORLD_LAYERS['main']):
        self.frame_index = 0
        self.frames = frames
        super().__init__(pos, self.frames[self.frame_index], groups, z)

    def animate(self, dt: float):
        self.frame_index += ANIMATION_SPEED * dt
        self.image = self.frames[int(self.frame_index % len(self.frames))]

    def update(self, dt: float):
        self.animate(dt)

# endregion

# region battle sprites

class MonsterSprite(pygame.sprite.Sprite):
    def __init__(self, pos: Tuple[float, float], frames: Dict[str, List[pygame.Surface]], groups: GroupsArgument, monster: Monster, index: int, pos_index: int, entity: str, apply_attack: Callable[['MonsterSprite', str, int], None], create_monster: Callable[[Monster, int, int, str], None]):
        # data
        self.index = index
        self.pos_index = pos_index
        self.entity = entity
        self.monster = monster
        self.frame_index = 0
        self.adjusted_frame_index = 0
        self.frames = frames
        self.state = 'idle'
        self.animation_speed = ANIMATION_SPEED + uniform(-1, 1)
        self.z = BATTLE_LAYERS['monster']
        self.highlight = False
        self.target_sprite = None
        self.current_attack = None
        self.apply_attack = apply_attack
        self.create_monster = create_monster
        self.next_monster_data = None

        # sprite setup
        super().__init__(groups)
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_frect(center = pos)

        self.timers: Dict[str, Timer] = {
            'remove highlight': Timer(500, func = lambda: self.set_highlight(False)),
            'kill': Timer(600, func = self.destroy)
        }

    def animate(self, dt: float):
        self.frame_index += ANIMATION_SPEED * dt
        if self.state == 'attack' and self.frame_index >= len(self.frames['attack']):
            # apply attack
            self.apply_attack(self.target_sprite, self.current_attack, self.monster.get_base_damage(self.current_attack))
            self.state = 'idle'

        self.adjusted_frame_index = int(self.frame_index % len(self.frames[self.state]))
        self.image = self.frames[self.state][self.adjusted_frame_index]

        if self.highlight:
            white_surf = pygame.mask.from_surface(self.image).to_surface()
            white_surf.set_colorkey('black')
            self.image = white_surf

    def set_highlight(self, value: bool):
        self.highlight = value
        if value:
            self.timers['remove highlight'].activate()

    def activate_attack(self, target_sprite: 'MonsterSprite', attack: str):
        self.state = 'attack'
        self.frame_index = 0
        self.target_sprite = target_sprite
        self.current_attack = attack
        self.monster.reduce_energy(attack)

    def delayed_kill(self, new_monster):
        if not self.timers['kill'].active:
            self.next_monster_data = new_monster
            self.timers['kill'].activate()

    def destroy(self):
        if self.next_monster_data:
            self.create_monster(*self.next_monster_data)
        self.kill()

    def update(self, dt: float):
        for timer in self.timers.values():
            timer.update()
        self.animate(dt)
        self.monster.update(dt)


class MonsterOutlineSprite(pygame.sprite.Sprite):
    def __init__(self, monster_sprite: MonsterSprite, groups: GroupsArgument, frames: Dict[str, List[pygame.Surface]]):
        super().__init__(groups)
        self.z = BATTLE_LAYERS['outline']
        self.monster_sprite = monster_sprite
        self.frames = frames

        self.image: pygame.Surface = self.frames[self.monster_sprite.state][self.monster_sprite.frame_index]
        self.rect = self.image.get_frect(center = self.monster_sprite.rect.center)

    def update(self, _):
        self.image = self.frames[self.monster_sprite.state][self.monster_sprite.adjusted_frame_index]

        if not self.monster_sprite.groups():
            self.kill()


class MonsterNameSprite(pygame.sprite.Sprite):
    def __init__(self, pos: Tuple[float, float], monster_sprite: MonsterSprite, groups: GroupsArgument, font: pygame.font.Font):
        super().__init__(groups)
        self.monster_sprite = monster_sprite
        self.z = BATTLE_LAYERS['name']

        text_surf = font.render(self.monster_sprite.monster.name, False, COLORS['black'])
        padding = 20

        self.image = pygame.Surface((text_surf.get_width() + 2 * padding, text_surf.get_height() + 2 * padding))
        self.image.fill(COLORS['white'])
        self.image.blit(text_surf, (padding, padding))
        self.rect = self.image.get_frect(midtop = pos)

    def update(self, _):
        if not self.monster_sprite.groups():
            self.kill()


class MonsterLevelSprite(pygame.sprite.Sprite):
    def __init__(self, entity: str, pos: Tuple[float, float], monster_sprite: MonsterSprite, groups: GroupsArgument, font: pygame.font.Font):
        super().__init__(groups)
        self.monster_sprite = monster_sprite
        self.font = font
        self.z = BATTLE_LAYERS['name']

        self.image = pygame.Surface((60, 26))
        self.rect = self.image.get_frect(topleft = pos) if entity == 'player' else self.image.get_frect(topright = pos)
        self.xp_rect = pygame.FRect(0, self.rect.height - 2, self.rect.width, 2)

    def update(self, _):
        self.image.fill(COLORS['white'])

        text_surf = self.font.render(f"Lvl {self.monster_sprite.monster.level}", False, COLORS['black'])
        text_rect = text_surf.get_frect(center = (self.rect.width / 2, self.rect.height / 2))
        self.image.blit(text_surf, text_rect)

        draw_bar(self.image, self.xp_rect, self.monster_sprite.monster.xp, self.monster_sprite.monster.level_up, COLORS['black'], COLORS['white'])

        if not self.monster_sprite.groups():
            self.kill()


class MonsterStatsSprite(pygame.sprite.Sprite):
    def __init__(self, pos: Tuple[float, float], monster_sprite: MonsterSprite, size: Tuple[float, float], groups: GroupsArgument, font: pygame.font.Font):
        super().__init__(groups)
        self.monster_sprite = monster_sprite
        self.image = pygame.Surface(size)
        self.rect = self.image.get_frect(midbottom = pos)
        self.font = font
        self.z = BATTLE_LAYERS['overlay']

    def update(self, _):
        self.image.fill(COLORS['white'])

        for index, (value, max_value) in enumerate(self.monster_sprite.monster.get_info()):
            color = (COLORS['red'], COLORS['blue'], COLORS['gray'])[index]

            if index < 2: # health and energy
                text_surf = self.font.render(f'{int(value)}/{max_value}', False, COLORS['black'])
                text_rect = text_surf.get_frect(topleft = (self.rect.width * 0.05, index * self.rect.height / 2))
                bar_rect = pygame.FRect(text_rect.bottomleft + pygame.Vector2(0, -2), (self.rect.width * 0.9, 4))

                self.image.blit(text_surf, text_rect)
                draw_bar(self.image, bar_rect, value, max_value, color, COLORS['black'], 2)
            else:
                init_rect = pygame.FRect((0, self.rect.height - 2), (self.rect.width, 2))
                draw_bar(self.image, init_rect, value, max_value, color, COLORS['white'], 0)

        if not self.monster_sprite.groups():
            self.kill()


class AttackSprite(AnimatedSprite):
    def __init__(self, pos: Tuple[float, float], frames: List[pygame.Surface], groups: GroupsArgument):
        super().__init__(pos, frames, groups, BATTLE_LAYERS['overlay'])
        self.rect.center = pos

    def animate(self, dt: float):
        self.frame_index += ANIMATION_SPEED * dt
        if self.frame_index < len(self.frames):
            self.image = self.frames[int(self.frame_index)]
        else:
            self.kill()

    def update(self, dt: float):
        self.animate(dt)


class TimedSprite(Sprite):
    def __init__(self, pos: Tuple[float, float], surf: pygame.Surface, groups: GroupsArgument, duration: float):
        super().__init__(pos, surf, groups, z = BATTLE_LAYERS['overlay'])
        self.rect.center = pos
        self.death_timer = Timer(duration, autostart=True, func=self.kill)

    def update(self, _):
        self.death_timer.update()

# endregion