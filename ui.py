"""
Premium Luxury UI for the AI Fruit Cutter game.

Includes:
- Premium glassmorphism HUD
- Score / High Score
- Lives
- Combo animation
- FPS
- Cinematic main menu
- Game Over screen
- Animated restart button
- Smooth progress ring
- Premium dark theme
- AI / Computer Vision branding
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


# ============================================================
# PREMIUM COLOR SYSTEM
# ============================================================

MIDNIGHT = (5, 8, 18)
GLASS = (12, 18, 34)
GLASS_LIGHT = (20, 29, 50)

CYAN = (72, 224, 255)
CYAN_SOFT = (115, 245, 255)

VIOLET = (150, 105, 255)

GOLD = (255, 215, 90)

MINT = (90, 255, 190)

TEXT = (242, 247, 255)
MUTED = (145, 160, 185)


class UI:

    # ========================================================
    # INITIALIZATION
    # ========================================================

    def __init__(self):

        pygame.font.init()

        # ----------------------------------------------------
        # Fonts
        # ----------------------------------------------------

        self.font_title = pygame.font.SysFont(
            "Segoe UI",
            72,
            bold=True
        )

        self.font_huge = pygame.font.SysFont(
            "Segoe UI",
            64,
            bold=True
        )

        self.font_large = pygame.font.SysFont(
            "Segoe UI",
            48,
            bold=True
        )

        self.font_medium = pygame.font.SysFont(
            "Segoe UI",
            30,
            bold=True
        )

        self.font_small = pygame.font.SysFont(
            "Segoe UI",
            22,
            bold=True
        )

        self.font_tiny = pygame.font.SysFont(
            "Segoe UI",
            17
        )

        # ----------------------------------------------------
        # Animation state
        # ----------------------------------------------------

        self.hover_anim = 0.0
        self.last_time = pygame.time.get_ticks()

        self.combo_scale = 0.0
        self.combo_alpha = 255

    # ========================================================
    # PREMIUM VISUAL HELPERS
    # ========================================================

    def _draw_shadow_text(
        self,
        surface,
        text,
        font,
        color,
        center,
        shadow=(0, 0, 0, 150),
        offset=3
    ):

        shadow_surf = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        shadow_text = font.render(
            text,
            True,
            shadow[:3]
        )

        shadow_text.set_alpha(
            shadow[3]
        )

        shadow_surf.blit(
            shadow_text,
            (
                center[0]
                - shadow_text.get_width() // 2
                + offset,

                center[1]
                - shadow_text.get_height() // 2
                + offset
            )
        )

        surface.blit(
            shadow_surf,
            (0, 0)
        )

        rendered = font.render(
            text,
            True,
            color
        )

        surface.blit(
            rendered,
            (
                center[0]
                - rendered.get_width() // 2,

                center[1]
                - rendered.get_height() // 2
            )
        )

    # ========================================================
    # GLASS PANEL
    # ========================================================

    def _draw_glass_panel(
        self,
        surface,
        rect,
        fill=(12, 18, 34, 220),
        border=(72, 224, 255, 90),
        radius=24
    ):

        panel = pygame.Surface(
            rect.size,
            pygame.SRCALPHA
        )

        pygame.draw.rect(
            panel,
            fill,
            panel.get_rect(),
            border_radius=radius
        )

        pygame.draw.rect(
            panel,
            border,
            panel.get_rect(),
            1,
            border_radius=radius
        )

        surface.blit(
            panel,
            rect.topleft
        )

        # Small glass highlight
        highlight = pygame.Surface(
            (
                max(1, rect.width - 32),
                2
            ),
            pygame.SRCALPHA
        )

        highlight.fill(
            (255, 255, 255, 28)
        )

        surface.blit(
            highlight,
            (
                rect.x + 16,
                rect.y + 8
            )
        )

    # ========================================================
    # CINEMATIC BACKGROUND
    # ========================================================

    def _draw_menu_background(self, surface):

        # Gradient background

        for y in range(HEIGHT):

            t = y / max(
                1,
                HEIGHT - 1
            )

            r = int(
                4 + 8 * t
            )

            g = int(
                7 + 10 * t
            )

            b = int(
                20 + 24 * t
            )

            pygame.draw.line(
                surface,
                (r, g, b),
                (0, y),
                (WIDTH, y)
            )

        # ----------------------------------------------------
        # Technical grid
        # ----------------------------------------------------

        for x in range(
            0,
            WIDTH,
            80
        ):

            pygame.draw.line(
                surface,
                (30, 48, 75),
                (x, 0),
                (x, HEIGHT),
                1
            )

        for y in range(
            0,
            HEIGHT,
            80
        ):

            pygame.draw.line(
                surface,
                (30, 48, 75),
                (0, y),
                (WIDTH, y),
                1
            )

        # ----------------------------------------------------
        # Center glow
        # ----------------------------------------------------

        glow = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        cx = WIDTH // 2
        cy = HEIGHT // 2 - 80

        for radius, alpha in (
            (300, 8),
            (230, 10),
            (170, 14)
        ):

            pygame.draw.circle(
                glow,
                (60, 170, 255, alpha),
                (cx, cy),
                radius
            )

        surface.blit(
            glow,
            (0, 0)
        )

    # ========================================================
    # CENTER TEXT
    # ========================================================

    def draw_text_center(
        self,
        surface,
        text,
        font,
        color,
        y
    ):

        rendered = font.render(
            text,
            True,
            color
        )

        x = (
            WIDTH // 2
            - rendered.get_width() // 2
        )

        surface.blit(
            rendered,
            (x, y)
        )

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
        fps
    ):

        # ----------------------------------------------------
        # Premium top glass panel
        # ----------------------------------------------------

        hud_rect = pygame.Rect(
            12,
            10,
            WIDTH - 24,
            76
        )

        self._draw_glass_panel(
            surface,
            hud_rect,
            fill=(8, 14, 28, 225),
            border=(72, 224, 255, 80),
            radius=18
        )

        # ----------------------------------------------------
        # Bottom separator
        # ----------------------------------------------------

        pygame.draw.line(
            surface,
            CYAN,
            (30, 85),
            (WIDTH - 30, 85),
            1
        )

        # ----------------------------------------------------
        # Score
        # ----------------------------------------------------

        self._draw_stat(
            surface,
            "SCORE",
            str(score),
            35,
            18,
            CYAN
        )

        # ----------------------------------------------------
        # High score
        # ----------------------------------------------------

        self._draw_stat(
            surface,
            "BEST",
            str(high_score),
            235,
            18,
            GOLD
        )

        # ----------------------------------------------------
        # FPS
        # ----------------------------------------------------

        fps_text = self.font_tiny.render(
            f"{int(fps)} FPS",
            True,
            MUTED
        )

        surface.blit(
            fps_text,
            (
                WIDTH
                - fps_text.get_width()
                - 30,
                18
            )
        )

        # ----------------------------------------------------
        # Lives
        # ----------------------------------------------------

        lives_label = self.font_tiny.render(
            "LIVES",
            True,
            MUTED
        )

        surface.blit(
            lives_label,
            (
                WIDTH - 190,
                18
            )
        )

        for i in range(3):

            x = WIDTH - 130 + i * 35
            y = 51

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
                    (60, 65, 80)
                )

        # ----------------------------------------------------
        # Combo
        # ----------------------------------------------------

        if combo > 1:

            pulse = (
                math.sin(
                    pygame.time.get_ticks()
                    / 100.0
                ) + 1
            ) * 0.5

            scale = (
                1.0
                + pulse * 0.08
            )

            combo_font = pygame.font.SysFont(
                "Segoe UI",
                int(42 * scale),
                bold=True
            )

            combo_text = combo_font.render(
                f"{combo}x COMBO!",
                True,
                GOLD
            )

            combo_x = (
                WIDTH // 2
                - combo_text.get_width() // 2
            )

            # Glow
            glow = pygame.Surface(
                (
                    combo_text.get_width() + 30,
                    combo_text.get_height() + 20
                ),
                pygame.SRCALPHA
            )

            pygame.draw.rect(
                glow,
                (255, 215, 90, 20),
                glow.get_rect(),
                border_radius=15
            )

            surface.blit(
                glow,
                (
                    combo_x - 15,
                    94
                )
            )

            surface.blit(
                combo_text,
                (
                    combo_x,
                    98
                )
            )

            pygame.draw.line(
                surface,
                GOLD,
                (
                    WIDTH // 2 - 90,
                    145
                ),
                (
                    WIDTH // 2 + 90,
                    145
                ),
                2
            )

    # ========================================================
    # HUD STAT
    # ========================================================

    def _draw_stat(
        self,
        surface,
        label,
        value,
        x,
        y,
        color
    ):

        label_text = self.font_tiny.render(
            label,
            True,
            MUTED
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
            (
                x,
                y + 20
            )
        )

    # ========================================================
    # HEART
    # ========================================================

    def draw_heart(
        self,
        surface,
        x,
        y,
        size,
        color
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
                (
                    x - size,
                    y - size // 4
                ),
                (
                    x + size,
                    y - size // 4
                ),
                (
                    x,
                    y + size
                )
            ]
        )

    # ========================================================
    # GAME OVER
    # ========================================================

    def draw_game_over(
        self,
        surface,
        score,
        high_score
    ):

        # ----------------------------------------------------
        # Dark cinematic overlay
        # ----------------------------------------------------

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (0, 0, 10, 215)
        )

        surface.blit(
            overlay,
            (0, 0)
        )

        # ----------------------------------------------------
        # Glass panel
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

        panel_rect = pygame.Rect(
            panel_x,
            panel_y,
            panel_width,
            panel_height
        )

        self._draw_glass_panel(
            surface,
            panel_rect,
            fill=(12, 18, 34, 242),
            border=(90, 180, 255, 110),
            radius=25
        )

        # ----------------------------------------------------
        # GAME OVER
        # ----------------------------------------------------

        title = self.font_title.render(
            "GAME OVER",
            True,
            (255, 105, 125)
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
        # Final Score
        # ----------------------------------------------------

        score_label = self.font_small.render(
            "FINAL SCORE",
            True,
            MUTED
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
            CYAN
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
        # Best Score
        # ----------------------------------------------------

        best_text = self.font_medium.render(
            f"BEST SCORE  •  {high_score}",
            True,
            GOLD
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
        # Restart instruction
        # ----------------------------------------------------

        instruction = self.font_small.render(
            "Use your hand to restart",
            True,
            MUTED
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
        progress
    ):

        current_time = pygame.time.get_ticks()

        dt = (
            current_time
            - self.last_time
        )

        self.last_time = current_time

        dt = max(
            0,
            min(dt, 50)
        )

        # ----------------------------------------------------
        # Hover animation
        # ----------------------------------------------------

        if is_hovering:

            self.hover_anim = min(
                1.0,
                self.hover_anim
                + dt / 180.0
            )

        else:

            self.hover_anim = max(
                0.0,
                self.hover_anim
                - dt / 220.0
            )

        ease = 1.0 - (
            1.0 - self.hover_anim
        ) ** 3

        # ----------------------------------------------------
        # Scale
        # ----------------------------------------------------

        scale = (
            1.0
            + 0.08 * ease
        )

        if progress >= 1.0:
            scale += 0.05

        width = int(
            rect.width * scale
        )

        height = int(
            rect.height * scale
        )

        x = (
            rect.centerx
            - width // 2
        )

        y = (
            rect.centery
            - height // 2
        )

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
                (
                    x - 30,
                    y - 30
                )
            )

        # ----------------------------------------------------
        # Button color
        # ----------------------------------------------------

        normal_color = (
            15,
            100,
            65
        )

        hover_color = (
            20,
            190,
            105
        )

        r = int(
            normal_color[0]
            + (
                hover_color[0]
                - normal_color[0]
            ) * ease
        )

        g = int(
            normal_color[1]
            + (
                hover_color[1]
                - normal_color[1]
            ) * ease
        )

        b = int(
            normal_color[2]
            + (
                hover_color[2]
                - normal_color[2]
            ) * ease
        )

        pygame.draw.rect(
            surface,
            (r, g, b),
            button_rect,
            border_radius=18
        )

        pygame.draw.rect(
            surface,
            MINT,
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
            (
                text_x,
                text_y
            )
        )

    # ========================================================
    # MAIN MENU
    # ========================================================

    def draw_main_menu(
        self,
        surface
    ):

        # ----------------------------------------------------
        # Cinematic background
        # ----------------------------------------------------

        self._draw_menu_background(
            surface
        )

        overlay = pygame.Surface(
            (WIDTH, HEIGHT),
            pygame.SRCALPHA
        )

        overlay.fill(
            (3, 6, 16, 90)
        )

        surface.blit(
            overlay,
            (0, 0)
        )

        # ----------------------------------------------------
        # Decorative animated rings
        # ----------------------------------------------------

        center_x = WIDTH // 2
        center_y = HEIGHT // 2

        pulse = (
            math.sin(
                pygame.time.get_ticks()
                / 700
            ) + 1
        ) * 0.5

        radius = int(
            170
            + pulse * 15
        )

        pygame.draw.circle(
            surface,
            (20, 80, 130),
            (
                center_x,
                center_y - 90
            ),
            radius,
            2
        )

        pygame.draw.circle(
            surface,
            (70, 150, 210),
            (
                center_x,
                center_y - 90
            ),
            radius - 25,
            1
        )

        # ----------------------------------------------------
        # Main title
        # ----------------------------------------------------

        self._draw_shadow_text(
            surface,
            "FRUIT CUTTER",
            self.font_title,
            TEXT,
            (
                WIDTH // 2,
                HEIGHT // 3 - 25
            ),
            shadow=(
                0,
                0,
                0,
                180
            ),
            offset=4
        )

        # ----------------------------------------------------
        # AI / Computer Vision badge
        # ----------------------------------------------------

        badge = self.font_small.render(
            "AI  •  COMPUTER VISION  •  HAND GESTURE CONTROL",
            True,
            CYAN_SOFT
        )

        surface.blit(
            badge,
            (
                WIDTH // 2
                - badge.get_width() // 2,
                HEIGHT // 3 + 52
            )
        )

        # ----------------------------------------------------
        # AI label
        # ----------------------------------------------------

        ai_text = self.font_large.render(
            "AI",
            True,
            VIOLET
        )

        surface.blit(
            ai_text,
            (
                WIDTH // 2
                - ai_text.get_width() // 2,
                HEIGHT // 3 + 82
            )
        )

        # ----------------------------------------------------
        # Instruction glass panel
        # ----------------------------------------------------

        box = pygame.Rect(
            WIDTH // 2 - 300,
            HEIGHT // 2 + 100,
            600,
            80
        )

        self._draw_glass_panel(
            surface,
            box,
            fill=(10, 18, 36, 235),
            border=(72, 224, 255, 110),
            radius=20
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
        # Footer
        # ----------------------------------------------------

        footer = self.font_tiny.render(
            "Slice fruits  •  Avoid bombs  •  Build combos",
            True,
            MUTED
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
        progress
    ):

        if progress <= 0:
            return

        progress = min(
            1.0,
            max(0.0, progress)
        )

        points = []

        segments = 12

        # ----------------------------------------------------
        # Top
        # ----------------------------------------------------

        points.append(
            (
                rect.left + radius,
                rect.top
            )
        )

        points.append(
            (
                rect.right - radius,
                rect.top
            )
        )

        # ----------------------------------------------------
        # Top-right
        # ----------------------------------------------------

        for i in range(
            segments + 1
        ):

            angle = math.radians(
                -90
                + 90 * i / segments
            )

            points.append(
                (
                    rect.right
                    - radius
                    + radius
                    * math.cos(angle),

                    rect.top
                    + radius
                    + radius
                    * math.sin(angle)
                )
            )

        # ----------------------------------------------------
        # Right
        # ----------------------------------------------------

        points.append(
            (
                rect.right,
                rect.bottom - radius
            )
        )

        # ----------------------------------------------------
        # Bottom-right
        # ----------------------------------------------------

        for i in range(
            segments + 1
        ):

            angle = math.radians(
                90 * i / segments
            )

            points.append(
                (
                    rect.right
                    - radius
                    + radius
                    * math.cos(angle),

                    rect.bottom
                    - radius
                    + radius
                    * math.sin(angle)
                )
            )

        # ----------------------------------------------------
        # Bottom
        # ----------------------------------------------------

        points.append(
            (
                rect.left + radius,
                rect.bottom
            )
        )

        # ----------------------------------------------------
        # Bottom-left
        # ----------------------------------------------------

        for i in range(
            segments + 1
        ):

            angle = math.radians(
                90
                + 90 * i / segments
            )

            points.append(
                (
                    rect.left
                    + radius
                    + radius
                    * math.cos(angle),

                    rect.bottom
                    - radius
                    + radius
                    * math.sin(angle)
                )
            )

        # ----------------------------------------------------
        # Left
        # ----------------------------------------------------

        points.append(
            (
                rect.left,
                rect.top + radius
            )
        )

        # ----------------------------------------------------
        # Top-left
        # ----------------------------------------------------

        for i in range(
            segments + 1
        ):

            angle = math.radians(
                180
                + 90 * i / segments
            )

            points.append(
                (
                    rect.left
                    + radius
                    + radius
                    * math.cos(angle),

                    rect.top
                    + radius
                    + radius
                    * math.sin(angle)
                )
            )

        # ----------------------------------------------------
        # Calculate lengths
        # ----------------------------------------------------

        lengths = []

        total_length = 0

        for i in range(
            len(points) - 1
        ):

            p1 = points[i]
            p2 = points[i + 1]

            length = math.hypot(
                p2[0] - p1[0],
                p2[1] - p1[1]
            )

            lengths.append(
                length
            )

            total_length += length

        target = (
            total_length
            * progress
        )

        # ----------------------------------------------------
        # Build partial path
        # ----------------------------------------------------

        path = [
            points[0]
        ]

        current = 0

        for i, length in enumerate(
            lengths
        ):

            if (
                current + length
                <= target
            ):

                path.append(
                    points[i + 1]
                )

                current += length

            else:

                remaining = (
                    target
                    - current
                )

                ratio = (
                    remaining / length
                    if length > 0
                    else 0
                )

                p1 = points[i]
                p2 = points[i + 1]

                x = (
                    p1[0]
                    + (
                        p2[0]
                        - p1[0]
                    ) * ratio
                )

                y = (
                    p1[1]
                    + (
                        p2[1]
                        - p1[1]
                    ) * ratio
                )

                path.append(
                    (x, y)
                )

                break

        # ----------------------------------------------------
        # Draw
        # ----------------------------------------------------

        if len(path) >= 2:

            pygame.draw.lines(
                surface,
                MINT,
                False,
                path,
                thickness
            )

            # Smooth endpoints

            for point in path:

                pygame.draw.circle(
                    surface,
                    MINT,
                    (
                        int(point[0]),
                        int(point[1])
                    ),
                    thickness // 2
                )