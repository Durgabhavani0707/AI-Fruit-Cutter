"""
main.py

Main entry point for the Fruit Cutter AI game.
Initializes Pygame, HandTracker, and the Game Loop.
"""
import pygame
import sys
from settings import WIDTH, HEIGHT, FPS
from hand_tracker import HandTracker
from game import Game
from ui import UI

def main():
    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Fruit Cutter AI")
    clock = pygame.time.Clock()

    # Initialize Modules
    tracker = HandTracker(WIDTH, HEIGHT)
    game = Game()
    ui = UI()
    
    menu_pos_history = []

    def play_beep():
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            import numpy as np
            sample_rate = 44100
            duration = 0.1
            freq = 660.0
            t = np.linspace(0, duration, int(sample_rate * duration), False)
            wave = np.sin(freq * t * 2 * np.pi)
            audio = (wave * 32767).astype(np.int16)
            stereo_audio = np.column_stack((audio, audio))
            sound = pygame.sndarray.make_sound(stereo_audio)
            sound.play()
        except:
            pass

    running = True
    is_hovering = False
    hover_progress = 0.0
    flash_start_time = 0
    btn_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 50, 300, 80)
    RESTART_HOVER_TIME = 1600.0 # ms
    last_loop_time = pygame.time.get_ticks()
    
    # State tracking
    hand_detected_duration = 0.0
    countdown_timer = 0.0

    while running:
        current_time = pygame.time.get_ticks()
        dt_main = current_time - last_loop_time
        last_loop_time = current_time
        
        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            
            # Allow mouse clicks for debugging / backup input
            if event.type == pygame.MOUSEBUTTONDOWN and game.state == "MENU":
                game.start_game()
            if event.type == pygame.MOUSEBUTTONDOWN and game.state == "GAME_OVER":
                game.state = "MENU"

        # Get Camera Frame and Finger Position
        frame_surface, current_finger_pos, prev_finger_pos = tracker.get_frame_and_finger()

        # Render Background (Webcam Feed)
        if frame_surface:
            # Draw webcam feed as background
            screen.blit(frame_surface, (0, 0))
        else:
            # Fallback black background if camera fails
            screen.fill((0, 0, 0))

        # Game State Machine
        if game.state == "MENU":
            ui.draw_main_menu(screen)
            # Gesture to start: Horizontal wave only
            if current_finger_pos:
                menu_pos_history.append(current_finger_pos)
                if len(menu_pos_history) > 30: # 0.5 seconds at 60 FPS
                    menu_pos_history.pop(0)
                
                # Check for robust horizontal wave immediately (as few as 5 frames)
                if len(menu_pos_history) >= 5:
                    xs = [p[0] for p in menu_pos_history]
                    ys = [p[1] for p in menu_pos_history]
                    
                    x_span = max(xs) - min(xs)
                    y_span = max(ys) - min(ys)
                    
                    # Must travel > 120px horizontally, but < 80px vertically (ignore vertical sweeps)
                    if x_span > 120 and y_span < 80:
                        menu_pos_history.clear()
                        game.start_game()
            else:
                menu_pos_history.clear()
            
            # Allow click to bypass
            if pygame.mouse.get_pressed()[0]:
                game.start_game()

        elif game.state == "PLAYING":
            # Update game logic
            game.update(current_time, current_finger_pos, prev_finger_pos)
            
            # Screen shake effect
            shake_x, shake_y = 0, 0
            if getattr(game, 'screen_shake_timer', 0) > 0:
                game.screen_shake_timer -= dt_main
                import random
                intensity = max(1, int(game.screen_shake_timer / 30.0))
                shake_x = random.randint(-intensity, intensity)
                shake_y = random.randint(-intensity, intensity)
                
            if shake_x != 0 or shake_y != 0:
                game_surf = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
                game.draw(game_surf)
                tracker.draw_trail(game_surf)
                screen.blit(game_surf, (shake_x, shake_y))
            else:
                game.draw(screen)
                tracker.draw_trail(screen)
            
            # Draw UI HUD
            ui.draw_hud(screen, game.score, game.high_score, game.lives, game.combo, clock.get_fps())

        elif game.state == "GAME_OVER":
            ui.draw_game_over(screen, game.score, game.high_score)
            
            # Hover Restart logic
            if flash_start_time > 0:
                is_hovering = True
                hover_progress = 1.0
                if current_time - flash_start_time >= 150:
                    game.state = "MENU"
                    is_hovering = False
                    hover_progress = 0.0
                    flash_start_time = 0
            else:
                if current_finger_pos:
                    if btn_rect.collidepoint(current_finger_pos):
                        if not is_hovering:
                            is_hovering = True
                        
                        hover_progress += dt_main / RESTART_HOVER_TIME
                        
                        if hover_progress >= 1.0:
                            play_beep()
                            flash_start_time = current_time
                            hover_progress = 1.0
                    else:
                        is_hovering = False
                else:
                    is_hovering = False
                    
                # Reset progress completely if finger leaves
                if not is_hovering:
                    hover_progress = 0.0
                
            if game.state == "GAME_OVER":
                ui.draw_restart_button(screen, btn_rect, is_hovering, hover_progress)
                
            tracker.draw_trail(screen)

        pygame.display.flip()
        clock.tick(FPS)

    tracker.release()
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
