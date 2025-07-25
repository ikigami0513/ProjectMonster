import pygame
from game_data import MonsterData
from save_ import Save
from settings import *
from typing import List, Dict


class Encyclopedia:
    def __init__(self, monster_frames: Dict[str, Dict[str, pygame.Surface]], fonts: Dict[str, pygame.Font]):
        self.display_surface = pygame.display.get_surface()
        self.fonts = fonts
        self.frame_index = 0

        # frames
        self.icon_frames = monster_frames['icons']
        self.monster_frames = monster_frames['monsters']
        self.ui_frames = monster_frames['ui']

        self.tint_surf = pygame.Surface((self.display_surface.get_width(), self.display_surface.get_height()))
        self.tint_surf.set_alpha(200)

        # dimensions
        self.main_rect = pygame.FRect(
            0, 0,
            self.display_surface.get_width() * 0.6, self.display_surface.get_height() * 0.8
        ).move_to(center = (self.display_surface.get_width() * 0.5, self.display_surface.get_height() * 0.5))

        # list
        self.visible_items = 6
        self.list_width = self.main_rect.width * 0.4
        self.item_height = self.main_rect.height / self.visible_items
        self.index = 0

        monsters_data = MonsterData.all()
        save = Save()
        available_monsters: List[Dict[str, str]] = save.get("encyclopedia")

        status_map: Dict[str, str] = {
            monster["monster"]: monster['status'] for monster in available_monsters
        }

        self.monsters_list: List[Dict[str, str]] = []
        for monster_data in monsters_data:
            name: str = monster_data["name"].lower()
            status: str = status_map.get(name, "unknown")

            self.monsters_list.append({
                "monster": name,
                "status": status,
                "data": monster_data
            })

        self.monsters_list.sort(key=lambda m: m["data"].get("number", 9999))

    def input(self) -> None:
        keys = pygame.key.get_just_pressed()
        if keys[pygame.K_UP]:
            self.index -= 1
        if keys[pygame.K_DOWN]:
            self.index += 1

        self.index = self.index % len(self.monsters_list)

    def display_list(self):
        bg_rect = pygame.FRect(self.main_rect.topleft, (self.list_width, self.main_rect.height))
        pygame.draw.rect(self.display_surface, COLORS['gray'], bg_rect, 0, 0, 12, 0, 12, 0)

        v_offset = 0 if self.index < self.visible_items else -(self.index - self.visible_items + 1) * self.item_height
        for index, monster in enumerate(self.monsters_list):
            # colors
            bg_color = COLORS['gray'] if self.index != index else COLORS['light']
            text_color = COLORS['white']

            top = self.main_rect.top + index * self.item_height + v_offset
            item_rect = pygame.FRect(self.main_rect.left, top, self.list_width, self.item_height)

            if monster["status"] == "unknown":
                text_surf = self.fonts['regular'].render(f"{monster['data']['number']} # " + "?" * len(monster["monster"]), False, text_color)
                text_rect = text_surf.get_frect(midleft = item_rect.midleft + pygame.Vector2(90, 0))
 
                icon_surf = self.ui_frames['cross']
                icon_rect = icon_surf.get_frect(center = item_rect.midleft + pygame.Vector2(45, 0))
            else:
                text_surf = self.fonts['regular'].render(f"{monster['data']['number']} # {monster['data']['name']}", False, text_color)
                text_rect = text_surf.get_frect(midleft = item_rect.midleft + pygame.Vector2(90, 0))

                icon_surf = self.icon_frames[monster["data"]["name"]]
                icon_rect = icon_surf.get_frect(center = item_rect.midleft + pygame.Vector2(45, 0))

            if item_rect.colliderect(self.main_rect):
                # check corners
                if item_rect.collidepoint(self.main_rect.topleft):
                    pygame.draw.rect(self.display_surface, bg_color, item_rect, 0, 0, 12)
                elif item_rect.collidepoint(self.main_rect.bottomleft + pygame.Vector2(1, -1)):
                    pygame.draw.rect(self.display_surface, bg_color, item_rect, 0, 0, 0, 0, 12, 0)
                else:
                    pygame.draw.rect(self.display_surface, bg_color, item_rect)

                self.display_surface.blit(text_surf, text_rect)
                self.display_surface.blit(icon_surf, icon_rect)

        # lines
        for i in range(1, min(self.visible_items, len(self.monsters_list))):
            y = self.main_rect.top + self.item_height * 1
            left = self.main_rect.left
            right = self.main_rect.left + self.list_width
            pygame.draw.line(self.display_surface, COLORS['light-gray'], (left, y), (right, y))

        # shadow
        shadow_surf = pygame.Surface((4, self.main_rect.height))
        shadow_surf.set_alpha(100)
        self.display_surface.blit(shadow_surf, (self.main_rect.left + self.list_width - 4, self.main_rect.top))

    def display_main(self, dt: float):
        # data
        monster = self.monsters_list[self.index]

        # main bg
        rect = pygame.FRect(self.main_rect.left + self.list_width, self.main_rect.top, self.main_rect.width - self.list_width, self.main_rect.height)
        pygame.draw.rect(self.display_surface, COLORS['dark'], rect, 0, 12, 0, 12, 0)

        if monster["status"] == "unknown":
            return

        # monster display
        top_rect = pygame.FRect(rect.topleft, (rect.width, rect.height * 0.4))
        pygame.draw.rect(self.display_surface, COLORS[monster["data"]["stats"]["element"]], top_rect, 0, 0, 0, 12)

        # monster animation
        self.frame_index += ANIMATION_SPEED * dt
        monster_animation = self.monster_frames[monster["data"]["name"]]["idle"]
        monster_surf: pygame.Surface = monster_animation[int(self.frame_index) % len(monster_animation)]
        monster_rect: pygame.FRect = monster_surf.get_frect(center = top_rect.center)
        self.display_surface.blit(monster_surf, monster_rect)

        # name
        name_surf = self.fonts['bold'].render(monster["data"]["name"], False, COLORS['white'])
        name_rect = name_surf.get_frect(topleft = top_rect.topleft + pygame.Vector2(10, 10))
        self.display_surface.blit(name_surf, name_rect)

        # element
        element_surf = self.fonts['regular'].render(monster["data"]["stats"]["element"], False, COLORS['white'])
        element_rect = element_surf.get_frect(bottomright = top_rect.bottomright + pygame.Vector2(-10, -10))
        self.display_surface.blit(element_surf, element_rect)

    def update(self, dt: float):
        self.input()
        self.display_surface.blit(self.tint_surf, (0, 0))
        self.display_list()
        self.display_main(dt)
