"""
ui.py

Modern UI for the AI Fruit Cutter game.

Includes:
- Premium HUD
- Score / High Score
- Lives
- Combo animation
- FPS
- Main menu
- Game Over screen
- Animated restart button
- Smooth progress ring
"""

import math
import pygame

from settings import (
    WIDTH,
    HEIGHT,
    WHITE,
    BLACK,
    RED,
)


class UI:

    def __init__(self):
        pygame.font.init()

        # ----------------------------------------------------
        # Fonts
        # ----------------------------------------------------

        self.font_title = pygame.font.SysFont(
            "Arial", 72, bold=True
        )

        self.font_huge = pygame.font.SysFont(
            "Arial", 64, bold=True
        )

        self.font_large = pygame.font.SysFont(
            "Arial", 48, bold=True
        )

        self.font_medium = pygame.font.SysFont(
            "Arial", 30, bold=True
        )

        self.font_small = pygame.font.SysFont(
            "Arial", 22, bold=True
        )

        self.font_tiny = pygame.font.SysFont(
            "Arial", 17
        )

        # Animation state
        self.hover_anim = 0.0
        self.last_time = pygame.time.get_ticks()

        self.combo_scale = 0.0
        self.combo_alpha = 255

    # ========================================================
    # Utility
    # ========================================================

    def draw_text_center(
        self,
        surface,
        text,
        font,
        color,
        y,
    ):
        rendered = font.render(text, True, color)

        x = WIDTH // 2 - rendered.get_width() // 2

        surface.blit(rendered, (x, y))

        return rendered

    # ========================================================
    # HUD
    # ========================================================

    def draw_hud(
        self,
        surface,
        score,
        high_score,
        lives,
        combo,
        fps,
    ):
        """
        Draw modern in-game HUD.
        """

        # ----------------------------------------------------
        # Top glass-style panel
        # ----------------------------------------------------

        hud = pygame.Surface(
            (WIDTH, 76),
            pygame.SRCALPHA
        )

        hud.fill((5, 10, 25, 215))

        surface.blit(hud, (0, 0))

        # Bottom separator
        pygame.draw.line(
            surface,
            (80, 160, 255),
            (0, 75),
            (WIDTH, 75),
            2
        )

        # ----------------------------------------------------
        # Score
        # ----------------------------------------------------

        self._draw_stat(
            surface,
            "SCORE",
            str(score),
            30,
            12,
            (80, 220, 255)
        )

        # ----------------------------------------------------
        # High Score
        # ----------------------------------------------------

        self._draw_stat(
            surface,
            "BEST",
            str(high_score),
            230,
            12,
            (255, 215, 80)
        )

        # ----------------------------------------------------
        # FPS
        # ----------------------------------------------------

        fps_text = self.font_tiny.render(
            f"{int(fps)} FPS",
            True,
            (160, 180, 200)
        )

        surface.blit(
            fps_text,
            (WIDTH - fps_text.get_width() - 25, 12)
        )

        # ----------------------------------------------------
        # Lives
        # ----------------------------------------------------

        lives_label = self.font_tiny.render(
            "LIVES",
            True,
            (160, 180, 200)
        )

        surface.blit(
            lives_label,
            (WIDTH - 190, 12)
        )

        for i in range(3):

            x = WIDTH - 130 + i * 35
            y = 45

            if i < lives:
                self.draw_heart(
                    surface,
                    x,
                    y,
                    16,
                    (255, 70, 90)
                )
            else:
                self.draw_heart(
                    surface,
                    x,
                    y,
                    16,
                    (70, 75, 90)
                )

        # ----------------------------------------------------
        # Combo
        # ----------------------------------------------------

        if combo > 1:

            pulse = (
                math.sin(
                    pygame.time.get_ticks() / 100.0
                ) + 1
            ) * 0.5

            scale = 1.0 + pulse * 0.08

            combo_font = pygame.font.SysFont(
                "Arial",
                int(42 * scale),
                bold=True
            )

            combo_text = combo_font.render(
                f"{combo}x COMBO!",
                True,
                (255, 220, 60)
            )

            combo_x = (
                WIDTH // 2
                - combo_text.get_width() // 2
            )

            surface.blit(
                combo_text,
                (combo_x, 92)
            )

            # Small glow line
            pygame.draw.line(
                surface,
                (255, 210, 60),
                (WIDTH // 2 - 90, 145),
                (WIDTH // 2 + 90, 145),
                2
            )

    # ========================================================
    # HUD Stat
    # ========================================================

    def _draw_stat(
        self,
        surface,
        label,
        value,
        x,
        y,
        color,
    ):

        label_text = self.font_tiny.render(
            label,
            True,
            (150, 165, 185)
        )

        value_text = self.font_medium.render(
            value,
            True,
            color
        )

        surface.blit(
            label_text,
            (x, y)
        )

        surface.blit(
            value_text,
            (x, y + 20)
        )

    # ========================================================
    # Heart
    # ========================================================

    def draw_heart(
        self,
        surface,
        x,
        y,
        size,
        color,
    ):

        pygame.draw.circle(
            surface,
            color,
            (
                x - size // 2,
                y - size // 3
            ),
            size // 2
        )

        pygame.draw.circle(
            surface,
            color,
            (
                x + size // 2,
                y - size // 3
            ),
            size // 2
        )

        pygame.draw.polygon(
            surface,
            color,
            [
                (x - size, y - size // 4),
                (x + size, y - size // 4),
                (x, y + size),
            ]
        )

    # ========================================================
    # GAME OVER
    # ========================================================

    def draw_game_over(
        self,
        surface,
        score,
        high_score,
    ):

        # Dark overlay
        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 10, 205)
        )

        surface.blit(
            overlay,
            (0, 0)
        )

        # ----------------------------------------------------
        # Panel
        # ----------------------------------------------------

        panel_width = 600
        panel_height = 390

        panel_x = (
            WIDTH // 2
            - panel_width // 2
        )

        panel_y = (
            HEIGHT // 2
            - panel_height // 2
        )

        panel = pygame.Surface(
            (
                panel_width,
                panel_height
            ),
            pygame.SRCALPHA
        )

        panel.fill(
            (15, 20, 40, 235)
        )

        surface.blit(
            panel,
            (panel_x, panel_y)
        )

        # Panel border
        pygame.draw.rect(
            surface,
            (80, 150, 255),
            (
                panel_x,
                panel_y,
                panel_width,
                panel_height
            ),
            2,
            border_radius=25
        )

        # ----------------------------------------------------
        # GAME OVER
        # ----------------------------------------------------

        title = self.font_title.render(
            "GAME OVER",
            True,
            (255, 80, 90)
        )

        surface.blit(
            title,
            (
                WIDTH // 2
                - title.get_width() // 2,
                panel_y + 40
            )
        )

        # ----------------------------------------------------
        # Score
        # ----------------------------------------------------

        score_label = self.font_small.render(
            "FINAL SCORE",
            True,
            (150, 165, 190)
        )

        surface.blit(
            score_label,
            (
                WIDTH // 2
                - score_label.get_width() // 2,
                panel_y + 135
            )
        )

        score_text = self.font_huge.render(
            str(score),
            True,
            (80, 220, 255)
        )

        surface.blit(
            score_text,
            (
                WIDTH // 2
                - score_text.get_width() // 2,
                panel_y + 160
            )
        )

        # ----------------------------------------------------
        # Best
        # ----------------------------------------------------

        best_text = self.font_medium.render(
            f"BEST SCORE  •  {high_score}",
            True,
            (255, 215, 80)
        )

        surface.blit(
            best_text,
            (
                WIDTH // 2
                - best_text.get_width() // 2,
                panel_y + 235
            )
        )

        # ----------------------------------------------------
        # Instruction
        # ----------------------------------------------------

        instruction = self.font_small.render(
            "Use your hand to restart",
            True,
            (180, 190, 210)
        )

        surface.blit(
            instruction,
            (
                WIDTH // 2
                - instruction.get_width() // 2,
                panel_y + 285
            )
        )

    # ========================================================
    # RESTART BUTTON
    # ========================================================

    def draw_restart_button(
        self,
        surface,
        rect,
        is_hovering,
        progress,
    ):

        current_time = pygame.time.get_ticks()

        dt = current_time - self.last_time

        self.last_time = current_time

        dt = max(0, min(dt, 50))

        # ----------------------------------------------------
        # Smooth hover animation
        # ----------------------------------------------------

        if is_hovering:

            self.hover_anim = min(
                1.0,
                self.hover_anim + dt / 180.0
            )

        else:

            self.hover_anim = max(
                0.0,
                self.hover_anim - dt / 220.0
            )

        ease = 1.0 - (
            1.0 - self.hover_anim
        ) ** 3

        # ----------------------------------------------------
        # Scale
        # ----------------------------------------------------

        scale = 1.0 + 0.08 * ease

        if progress >= 1.0:
            scale += 0.05

        width = int(rect.width * scale)
        height = int(rect.height * scale)

        x = rect.centerx - width // 2
        y = rect.centery - height // 2

        button_rect = pygame.Rect(
            x,
            y,
            width,
            height
        )

        # ----------------------------------------------------
        # Glow
        # ----------------------------------------------------

        if is_hovering:

            glow = pygame.Surface(
                (
                    width + 60,
                    height + 60
                ),
                pygame.SRCALPHA
            )

            for i in range(5):

                alpha = int(
                    45
                    * ease
                    * (1 - i / 5)
                )

                glow_rect = pygame.Rect(
                    30 - i * 4,
                    30 - i * 4,
                    width + i * 8,
                    height + i * 8
                )

                pygame.draw.rect(
                    glow,
                    (50, 255, 150, alpha),
                    glow_rect,
                    border_radius=20
                )

            surface.blit(
                glow,
                (x - 30, y - 30)
            )

        # ----------------------------------------------------
        # Button color
        # ----------------------------------------------------

        normal_color = (15, 100, 65)
        hover_color = (20, 190, 105)

        r = int(
            normal_color[0]
            + (hover_color[0] - normal_color[0]) * ease
        )

        g = int(
            normal_color[1]
            + (hover_color[1] - normal_color[1]) * ease
        )

        b = int(
            normal_color[2]
            + (hover_color[2] - normal_color[2]) * ease
        )

        pygame.draw.rect(
            surface,
            (r, g, b),
            button_rect,
            border_radius=18
        )

        # Border
        pygame.draw.rect(
            surface,
            (100, 255, 180),
            button_rect,
            2,
            border_radius=18
        )

        # ----------------------------------------------------
        # Progress border
        # ----------------------------------------------------

        if 0 < progress < 1:

            self._draw_partial_rounded_rect(
                surface,
                button_rect,
                18,
                5,
                progress
            )

        # ----------------------------------------------------
        # Button text
        # ----------------------------------------------------

        text = self.font_medium.render(
            "RESTART",
            True,
            WHITE
        )

        text_x = (
            button_rect.centerx
            - text.get_width() // 2
        )

        text_y = (
            button_rect.centery
            - text.get_height() // 2
        )

        surface.blit(
            text,
            (text_x, text_y)
        )

    # ========================================================
    # MAIN MENU
    # ========================================================

    def draw_main_menu(self, surface):

        # ----------------------------------------------------
        # Background overlay
        # ----------------------------------------------------

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (3, 8, 20, 210)
        )

        surface.blit(
            overlay,
            (0, 0)
        )

        # ----------------------------------------------------
        # Decorative circles
        # ----------------------------------------------------

        center_x = WIDTH // 2
        center_y = HEIGHT // 2

        pulse = (
            math.sin(
                pygame.time.get_ticks() / 700
            ) + 1
        ) * 0.5

        radius = int(
            170 + pulse * 15
        )

        pygame.draw.circle(
            surface,
            (20, 80, 130),
            (center_x, center_y - 90),
            radius,
            2
        )

        pygame.draw.circle(
            surface,
            (40, 150, 180),
            (center_x, center_y - 90),
            radius - 25,
            1
        )

        # ----------------------------------------------------
        # Title
        # ----------------------------------------------------

        title = self.font_title.render(
            "FRUIT CUTTER",
            True,
            WHITE
        )

        title_x = (
            WIDTH // 2
            - title.get_width() // 2
        )

        surface.blit(
            title,
            (
                title_x,
                HEIGHT // 3 - 60
            )
        )

        # AI text
        ai_text = self.font_large.render(
            "AI",
            True,
            (80, 220, 255)
        )

        surface.blit(
            ai_text,
            (
                WIDTH // 2
                - ai_text.get_width() // 2,
                HEIGHT // 3 + 15
            )
        )

        # ----------------------------------------------------
        # Instruction panel
        # ----------------------------------------------------

        box = pygame.Rect(
            WIDTH // 2 - 300,
            HEIGHT // 2 + 100,
            600,
            80
        )

        pygame.draw.rect(
            surface,
            (10, 20, 40),
            box,
            border_radius=20
        )

        pygame.draw.rect(
            surface,
            (60, 150, 220),
            box,
            2,
            border_radius=20
        )

        prompt = self.font_medium.render(
            "✋  Raise your hand & wave to start",
            True,
            WHITE
        )

        surface.blit(
            prompt,
            (
                box.centerx
                - prompt.get_width() // 2,
                box.centery
                - prompt.get_height() // 2
            )
        )

        # ----------------------------------------------------
        # Bottom text
        # ----------------------------------------------------

        footer = self.font_tiny.render(
            "Slice fruits • Avoid bombs • Build combos",
            True,
            (130, 150, 175)
        )

        surface.blit(
            footer,
            (
                WIDTH // 2
                - footer.get_width() // 2,
                HEIGHT - 45
            )
        )

    # ========================================================
    # ANIMATED ROUNDED PROGRESS
    # ========================================================

    def _draw_partial_rounded_rect(
        self,
        surface,
        rect,
        radius,
        thickness,
        progress,
    ):

        if progress <= 0:
            return

        progress = min(
            1.0,
            max(0.0, progress)
        )

        points = []

        # ----------------------------------------------------
        # Generate rounded rectangle path
        # ----------------------------------------------------

        segments = 12

        # Top
        points.append(
            (rect.left + radius, rect.top)
        )

        points.append(
            (rect.right - radius, rect.top)
        )

        # Top-right
        for i in range(segments + 1):

            angle = math.radians(
                -90 + 90 * i / segments
            )

            points.append(
                (
                    rect.right - radius
                    + radius * math.cos(angle),

                    rect.top + radius
                    + radius * math.sin(angle)
                )
            )

        # Right
        points.append(
            (
                rect.right,
                rect.bottom - radius
            )
        )

        # Bottom-right
        for i in range(segments + 1):

            angle = math.radians(
                0 + 90 * i / segments
            )

            points.append(
                (
                    rect.right - radius
                    + radius * math.cos(angle),

                    rect.bottom - radius
                    + radius * math.sin(angle)
                )
            )

        # Bottom
        points.append(
            (
                rect.left + radius,
                rect.bottom
            )
        )

        # Bottom-left
        for i in range(segments + 1):

            angle = math.radians(
                90 + 90 * i / segments
            )

            points.append(
                (
                    rect.left + radius
                    + radius * math.cos(angle),

                    rect.bottom - radius
                    + radius * math.sin(angle)
                )
            )

        # Left
        points.append(
            (
                rect.left,
                rect.top + radius
            )
        )

        # Top-left
        for i in range(segments + 1):

            angle = math.radians(
                180 + 90 * i / segments
            )

            points.append(
                (
                    rect.left + radius
                    + radius * math.cos(angle),

                    rect.top + radius
                    + radius * math.sin(angle)
                )
            )

        # ----------------------------------------------------
        # Calculate total length
        # ----------------------------------------------------

        lengths = []

        total_length = 0

        for i in range(len(points) - 1):

            p1 = points[i]
            p2 = points[i + 1]

            length = math.hypot(
                p2[0] - p1[0],
                p2[1] - p1[1]
            )

            lengths.append(length)

            total_length += length

        target = total_length * progress

        # ----------------------------------------------------
        # Build partial path
        # ----------------------------------------------------

        path = [points[0]]

        current = 0

        for i, length in enumerate(lengths):

            if current + length <= target:

                path.append(points[i + 1])
                current += length

            else:

                remaining = target - current

                ratio = (
                    remaining / length
                    if length > 0
                    else 0
                )

                p1 = points[i]
                p2 = points[i + 1]

                x = p1[0] + (
                    p2[0] - p1[0]
                ) * ratio

                y = p1[1] + (
                    p2[1] - p1[1]
                ) * ratio

                path.append((x, y))

                break

        # ----------------------------------------------------
        # Draw
        # ----------------------------------------------------

        if len(path) >= 2:

            pygame.draw.lines(
                surface,
                (120, 255, 190),
                False,
                path,
                thickness
            )

            # Smooth endpoints
            for point in path:

                pygame.draw.circle(
                    surface,
                    (120, 255, 190),
                    (
                        int(point[0]),
                        int(point[1])
                    ),
                    thickness // 2
                )