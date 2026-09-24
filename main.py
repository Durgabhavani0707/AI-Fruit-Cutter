"""
main.py

Main entry point for the AI Fruit Cutter game.

Initializes:
- Pygame
- HandTracker
- Game
- UI

Controls:
- Hand wave -> Start game
- Mouse click -> Start game
- Finger hover -> Restart after game over
"""

import sys
import random
import pygame

from settings import WIDTH, HEIGHT, FPS
from hand_tracker import HandTracker
from game import Game
from ui import UI


def main():

    # ---------------------------------------------------------
    # INITIALIZE PYGAME
    # ---------------------------------------------------------

    pygame.init()

    # Try to initialize audio
    try:
        pygame.mixer.init()
        audio_available = True
    except pygame.error:
        audio_available = False

    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("AI Fruit Cutter")

    clock = pygame.time.Clock()

    # ---------------------------------------------------------
    # INITIALIZE GAME MODULES
    # ---------------------------------------------------------

    tracker = HandTracker(WIDTH, HEIGHT)
    game = Game()
    ui = UI()

    running = True

    # ---------------------------------------------------------
    # MENU WAVE DETECTION
    # ---------------------------------------------------------

    menu_pos_history = []

    # Number of frames used to detect a wave
    WAVE_HISTORY_LENGTH = 18

    # Minimum horizontal movement
    WAVE_X_DISTANCE = 120

    # Maximum vertical movement
    WAVE_Y_DISTANCE = 80

    # Prevent repeated triggering
    menu_cooldown = 0

    # ---------------------------------------------------------
    # GAME OVER RESTART
    # ---------------------------------------------------------

    is_hovering = False
    hover_progress = 0.0

    flash_start_time = 0

    btn_rect = pygame.Rect(
        WIDTH // 2 - 150,
        HEIGHT // 2 + 50,
        300,
        80
    )

    RESTART_HOVER_TIME = 1600.0  # milliseconds

    # ---------------------------------------------------------
    # TIME MANAGEMENT
    # ---------------------------------------------------------

    last_loop_time = pygame.time.get_ticks()

    # ---------------------------------------------------------
    # BEEP SOUND
    # ---------------------------------------------------------

    def play_beep():

        if not audio_available:
            return

        try:
            import numpy as np

            sample_rate = 44100
            duration = 0.10
            frequency = 660.0

            t = np.linspace(
                0,
                duration,
                int(sample_rate * duration),
                False
            )

            wave = np.sin(
                frequency * t * 2 * np.pi
            )

            audio = (wave * 32767).astype(np.int16)

            stereo_audio = np.column_stack(
                (audio, audio)
            )

            sound = pygame.sndarray.make_sound(
                stereo_audio
            )

            sound.play()

        except Exception:
            # Audio is optional, so don't crash the game
            pass

    # ---------------------------------------------------------
    # MAIN GAME LOOP
    # ---------------------------------------------------------

    try:

        while running:

            # -------------------------------------------------
            # DELTA TIME
            # -------------------------------------------------

            current_time = pygame.time.get_ticks()

            dt_main = current_time - last_loop_time
            last_loop_time = current_time

            # Prevent very large time jumps
            dt_main = min(dt_main, 100)

            # Countdown cooldown
            if menu_cooldown > 0:
                menu_cooldown -= dt_main

            # -------------------------------------------------
            # EVENT HANDLING
            # -------------------------------------------------

            for event in pygame.event.get():

                if event.type == pygame.QUIT:
                    running = False

                # ---------------------------------------------
                # Mouse controls
                # ---------------------------------------------

                elif event.type == pygame.MOUSEBUTTONDOWN:

                    # Start game from menu
                    if game.state == "MENU":
                        game.start_game()
                        menu_pos_history.clear()

                    # Return to menu from game over
                    elif game.state == "GAME_OVER":
                        game.state = "MENU"

                        is_hovering = False
                        hover_progress = 0.0
                        flash_start_time = 0

            # -------------------------------------------------
            # GET CAMERA + FINGER POSITION
            # -------------------------------------------------

            frame_surface, current_finger_pos, prev_finger_pos = (
                tracker.get_frame_and_finger()
            )

            # -------------------------------------------------
            # DRAW CAMERA BACKGROUND
            # -------------------------------------------------

            if frame_surface is not None:

                screen.blit(
                    frame_surface,
                    (0, 0)
                )

            else:

                screen.fill((0, 0, 0))

            # =================================================
            # MENU
            # =================================================

            if game.state == "MENU":

                ui.draw_main_menu(screen)

                # ---------------------------------------------
                # HAND WAVE TO START
                # ---------------------------------------------

                if current_finger_pos:

                    menu_pos_history.append(
                        current_finger_pos
                    )

                    # Keep only recent positions
                    if len(menu_pos_history) > WAVE_HISTORY_LENGTH:

                        menu_pos_history.pop(0)

                    # Need enough points before detecting wave
                    if (
                        len(menu_pos_history) >= 5
                        and menu_cooldown <= 0
                    ):

                        xs = [
                            position[0]
                            for position in menu_pos_history
                        ]

                        ys = [
                            position[1]
                            for position in menu_pos_history
                        ]

                        x_span = max(xs) - min(xs)
                        y_span = max(ys) - min(ys)

                        # -------------------------------------
                        # HORIZONTAL WAVE
                        # -------------------------------------

                        if (
                            x_span > WAVE_X_DISTANCE
                            and y_span < WAVE_Y_DISTANCE
                        ):

                            game.start_game()

                            menu_pos_history.clear()

                            # Small cooldown prevents
                            # accidental multiple triggers
                            menu_cooldown = 700

                else:

                    # No hand -> reset wave history
                    menu_pos_history.clear()

                # ---------------------------------------------
                # MOUSE FALLBACK
                # ---------------------------------------------

                if pygame.mouse.get_pressed()[0]:

                    game.start_game()
                    menu_pos_history.clear()

            # =================================================
            # PLAYING
            # =================================================

            elif game.state == "PLAYING":

                # ---------------------------------------------
                # UPDATE GAME
                # ---------------------------------------------

                game.update(
                    current_time,
                    current_finger_pos,
                    prev_finger_pos
                )

                # ---------------------------------------------
                # SCREEN SHAKE
                # ---------------------------------------------

                shake_x = 0
                shake_y = 0

                screen_shake_timer = getattr(
                    game,
                    "screen_shake_timer",
                    0
                )

                if screen_shake_timer > 0:

                    game.screen_shake_timer -= dt_main

                    intensity = max(
                        1,
                        int(
                            game.screen_shake_timer / 30.0
                        )
                    )

                    shake_x = random.randint(
                        -intensity,
                        intensity
                    )

                    shake_y = random.randint(
                        -intensity,
                        intensity
                    )

                # ---------------------------------------------
                # DRAW GAME
                # ---------------------------------------------

                if shake_x != 0 or shake_y != 0:

                    game_surface = pygame.Surface(
                        (WIDTH, HEIGHT),
                        pygame.SRCALPHA
                    )

                    game.draw(game_surface)

                    tracker.draw_trail(
                        game_surface
                    )

                    screen.blit(
                        game_surface,
                        (shake_x, shake_y)
                    )

                else:

                    game.draw(screen)

                    tracker.draw_trail(screen)

                # ---------------------------------------------
                # HUD
                # ---------------------------------------------

                ui.draw_hud(
                    screen,
                    game.score,
                    game.high_score,
                    game.lives,
                    game.combo,
                    clock.get_fps()
                )

            # =================================================
            # GAME OVER
            # =================================================

            elif game.state == "GAME_OVER":

                # ---------------------------------------------
                # GAME OVER SCREEN
                # ---------------------------------------------

                ui.draw_game_over(
                    screen,
                    game.score,
                    game.high_score
                )

                # ---------------------------------------------
                # RESTART HOVER
                # ---------------------------------------------

                if flash_start_time > 0:

                    # Button activation flash
                    is_hovering = True
                    hover_progress = 1.0

                    if (
                        current_time - flash_start_time
                        >= 150
                    ):

                        game.state = "MENU"

                        is_hovering = False
                        hover_progress = 0.0
                        flash_start_time = 0

                else:

                    # -----------------------------------------
                    # Finger hovering over restart button
                    # -----------------------------------------

                    if current_finger_pos:

                        if btn_rect.collidepoint(
                            current_finger_pos
                        ):

                            is_hovering = True

                            # Increase progress
                            hover_progress += (
                                dt_main /
                                RESTART_HOVER_TIME
                            )

                            # ---------------------------------
                            # Restart activated
                            # ---------------------------------

                            if hover_progress >= 1.0:

                                hover_progress = 1.0

                                play_beep()

                                flash_start_time = (
                                    current_time
                                )

                        else:

                            # Finger moved away
                            is_hovering = False
                            hover_progress = 0.0

                    else:

                        # No hand detected
                        is_hovering = False
                        hover_progress = 0.0

                # ---------------------------------------------
                # DRAW RESTART BUTTON
                # ---------------------------------------------

                ui.draw_restart_button(
                    screen,
                    btn_rect,
                    is_hovering,
                    hover_progress
                )

                # ---------------------------------------------
                # DRAW HAND TRAIL
                # ---------------------------------------------

                tracker.draw_trail(screen)

            # -------------------------------------------------
            # UPDATE DISPLAY
            # -------------------------------------------------

            pygame.display.flip()

            # -------------------------------------------------
            # CONTROL FPS
            # -------------------------------------------------

            clock.tick(FPS)

    # ---------------------------------------------------------
    # SAFE SHUTDOWN
    # ---------------------------------------------------------

    except KeyboardInterrupt:

        print("\nGame stopped by user.")

    except Exception as error:

        print("\nGame error:")
        print(error)

    finally:

        print("Closing AI Fruit Cutter...")

        try:
            tracker.release()
        except Exception:
            pass

        pygame.quit()

        sys.exit()


# =============================================================
# PROGRAM ENTRY POINT
# =============================================================

if __name__ == "__main__":
    main()