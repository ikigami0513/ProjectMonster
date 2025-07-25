import pygame
from typing import Dict
from settings import *
from team import Team
from timer_ import Timer
from encyclopedia import Encyclopedia
from monster import Monster


class Menu:
    def __init__(self, monsters: Dict[int, Monster], monster_frames: Dict[str, Dict[str, pygame.Surface]], fonts: Dict[str, pygame.font.Font]):
        self.display_surface = pygame.display.get_surface()
        self.monsters = monsters
        self.monster_frames = monster_frames
        self.fonts = fonts
        self.is_open = False
        self.opening_timer = Timer(100)

        self.tint_surf = pygame.Surface((self.display_surface.get_width(), self.display_surface.get_height()))
        self.tint_surf.set_alpha(200)

        # Dimensions
        self.item_spacing = 10
        self.main_rect = pygame.FRect(
            0, 0,
            self.display_surface.get_width() * 0.3, self.display_surface.get_height() * 0.8
        ).move_to(center = (self.display_surface.get_width() / 2, self.display_surface.get_height() / 2))

        # Menu options
        self.options = ["Team", "Inventory", "Encyclopedia", "Settings", "Save", "Quit"]

        # List settings
        self.visible_items = len(self.options)
        self.item_height = (self.main_rect.height - (self.visible_items + 1) * self.item_spacing) / self.visible_items
        self.index = 0

        # option
        self.current_menu = None
        self.team = Team(self.monsters, self.fonts, self.monster_frames)
        self.encyclopedia = Encyclopedia(self.monster_frames, self.fonts)

    def open(self):
        self.is_open = True
        self.opening_timer.activate()

    def close(self):
        self.is_open = False
        self.opening_timer.deactivate()

    def input(self):
        if self.opening_timer.active:
            return
        
        keys = pygame.key.get_just_pressed()
        if self.current_menu is None:
            if keys[pygame.K_UP]:
                self.index -= 1

            if keys[pygame.K_DOWN]:
                self.index += 1

            if keys[pygame.K_RETURN]:
                option = self.options[self.index]
                if option == "Team":
                    self.current_menu = self.team
                elif option == "Inventory":
                    print("Inventory")
                elif option == "Encyclopedia":
                    self.current_menu = self.encyclopedia
                elif option == "Settings":
                    print("Settings")
                elif option == "Save":
                    print("Save")
                elif option == "Quit":
                    print("Quit")

        if keys[pygame.K_ESCAPE]:
            if self.current_menu:
                self.current_menu = None
            else:
                self.close()

        # Loop index around
        self.index = self.index % len(self.options)

    def display(self):
        # Main background
        pygame.draw.rect(self.display_surface, COLORS['dark'], self.main_rect, border_radius=12)

        # Draw each menu option
        for i, option in enumerate(self.options):
            # Compute position
            top = self.main_rect.top + i * (self.item_height + self.item_spacing) + self.item_spacing
            left = self.main_rect.left + self.item_spacing
            item_rect = pygame.FRect(left, top, self.main_rect.width - self.item_spacing * 2, self.item_height)

            # Colors
            bg_color = COLORS['gray'] if self.index != i else COLORS['light']
            text_color = COLORS['white'] if self.index != i else COLORS['gold']

            # Draw background rectangle
            pygame.draw.rect(self.display_surface, bg_color, item_rect, border_radius=6)

            # Render text
            text_surf = self.fonts['regular'].render(option, True, text_color)
            text_rect = text_surf.get_frect(center=item_rect.center)
            self.display_surface.blit(text_surf, text_rect)

    def update(self, dt: float):
        self.opening_timer.update()
        self.input()
        if self.current_menu:
            self.current_menu.update(dt)
        else:
            self.display_surface.blit(self.tint_surf, (0, 0))
            self.display()
