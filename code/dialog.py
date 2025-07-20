import pygame
from settings import *
from entities import Character, Player
from types_utils import GroupsArgument
from timer_ import Timer
from typing import Callable


class DialogTree:
    def __init__(self, character: Character, player: Player, all_sprites: pygame.sprite.Group, font: pygame.font.Font, end_dialog: Callable[[Character], None]) -> None:
        self.player = player
        self.character = character
        self.font = font
        self.all_sprites = all_sprites
        self.end_dialog = end_dialog
    
        self.dialog = self.character.get_dialog()
        self.dialog_num = len(self.dialog)
        self.dialog_index = 0

        self.current_dialog = DialogSprite(self.dialog[self.dialog_index], self.character, self.all_sprites, self.font)
        self.dialog_timer = Timer(500, autostart = True)

    def input(self) -> None:
        keys = pygame.key.get_just_pressed()
        if keys[pygame.K_SPACE] and not self.dialog_timer.active:
            self.current_dialog.kill()
            self.dialog_index += 1
            if self.dialog_index < self.dialog_num:
                self.current_dialog = DialogSprite(self.dialog[self.dialog_index], self.character, self.all_sprites, self.font)
                self.dialog_timer.activate()
            else:
                self.end_dialog(self.character)

    def update(self) -> None:
        self.dialog_timer.update()
        self.input()

    
class DialogSprite(pygame.sprite.Sprite):
    def __init__(self, message: str, character: Character, groups: GroupsArgument, font: pygame.Font) -> None:
        super().__init__(groups)
        self.z = WORLD_LAYERS['top']

        # text
        text_surf = font.render(message, False, COLORS['black'])
        self.padding = 5
        width = max(30, text_surf.get_width() + self.padding * 2)
        height = text_surf.get_height() + self.padding * 2

        # background
        surf = pygame.Surface((width, height), pygame.SRCALPHA)
        surf.fill((0, 0, 0, 0))
        pygame.draw.rect(surf, COLORS['pure white'], surf.get_frect(topleft = (0, 0)), 0, 4)
        surf.blit(text_surf, text_surf.get_frect(center = (width / 2, height / 2)))

        self.image = surf
        self.rect = self.image.get_frect(midbottom = character.rect.midtop + pygame.Vector2(0, 10))
