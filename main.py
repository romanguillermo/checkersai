import pygame
import sys
import time

from checkers.constants import *
from checkers.game import Game
from checkers.minimax import minimax

FPS = 60
# AI_DEPTH = 3 # Depth of the minimax search tree, adjust for difficulty lvl, handled in menu

# Game States
STATE_START_MENU = 'START_MENU'
STATE_PLAYING = 'PLAYING'
STATE_GAME_OVER = 'GAME_OVER'

# Pygame initialization
pygame.init()
pygame.font.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers')

FONT_TITLE = pygame.font.SysFont(None, 70)
FONT_BUTTON = pygame.font.SysFont(None, 45)
FONT_HUD = pygame.font.SysFont(None, 30)
FONT_MESSAGE = pygame.font.SysFont(None, 50)

def draw_text(surface, text, font, color, center_pos):
    """Draws text centered at a given position."""
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect(center=center_pos)
    surface.blit(text_surface, text_rect)

def draw_button(surface, rect, text, button_color, hover_color, text_color, font, is_selected=False):
    """Draws a button and returns True if mouse is hovering over it."""
    mouse_pos = pygame.mouse.get_pos()
    is_hovering = rect.collidepoint(mouse_pos)

    if is_selected:
        color = SELECTED_BUTTON_COLOR
    elif is_hovering:
        color = hover_color
    else:
        color = button_color

    pygame.draw.rect(surface, color, rect, border_radius=8)
    draw_text(surface, text, font, text_color, rect.center)
    return is_hovering

def get_row_col_from_mouse(pos):
    """Converts mouse click position (x, y) to board (row, col)."""
    x,y = pos
    if BOARD_OFFSET_X <= x < BOARD_OFFSET_X + COLS * SQUARE_SIZE and \
       BOARD_OFFSET_Y <= y < BOARD_OFFSET_Y + ROWS * SQUARE_SIZE:
        row = (y - BOARD_OFFSET_Y) // SQUARE_SIZE
        col = (x - BOARD_OFFSET_X) // SQUARE_SIZE
        return row, col
    else:
        return None # Click out of bounds
    

def main():
    """Runs the main game application, managing states and loops."""
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)

    game_state = STATE_START_MENU
    selected_difficulty = None
    ai_depth = 2 # default
    game_start_time = 0
    elapsed_time_str = "00:00"
    winner_info = None 

    reset_button_w, reset_button_h = 80, 30 
    reset_button_rect = pygame.Rect(WIDTH - reset_button_w - 10,(HUD_HEIGHT - reset_button_h) // 2, reset_button_w, reset_button_h)

    ai_is_thinking = False
    ai_think_start_time = 0
    needs_ai_move = False

    # --- Main Application Loop ---
    while run:
        clock.tick(FPS)
        WIN.fill(MENU_BG_COLOR)
        mouse_pos = pygame.mouse.get_pos()

        if game_state == STATE_START_MENU:
            # --- Start Menu ---
            if 'reset_from_game_over' in locals() and reset_from_game_over:
                ai_is_thinking = False
                reset_from_game_over = False
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # Difficulty button clicks
                    if easy_button_rect.collidepoint(event.pos):
                        selected_difficulty = 'Easy'
                        ai_depth = 1 # Easy
                    elif medium_button_rect.collidepoint(event.pos):
                        selected_difficulty = 'Medium'
                        ai_depth = 2 # Medium
                    elif hard_button_rect.collidepoint(event.pos):
                        selected_difficulty = 'Hard'
                        ai_depth = 3 # Hard
                    # Check start button click
                    elif start_button_rect.collidepoint(event.pos) and selected_difficulty:
                        game_state = STATE_PLAYING
                        game_start_time = time.time() # Record game start time
                        ai_is_thinking = False
                        print(f"Starting game with AI Difficulty: {selected_difficulty} (Depth: {ai_depth})")


            # --- Start Menu Drawing ---
            draw_text(WIN, "Checkers vs AI", FONT_TITLE, WHITE, (WIDTH // 2, HEIGHT // 4))
            draw_text(WIN, "Select Difficulty:", FONT_BUTTON, WHITE, (WIDTH // 2, HEIGHT // 2 - 80))

            # Define button rects
            button_w, button_h = 180, 60
            spacing = 30
            total_w = 3 * button_w + 2 * spacing
            start_x = (WIDTH - total_w) // 2
            button_y = HEIGHT // 2 - 20

            easy_button_rect = pygame.Rect(start_x, button_y, button_w, button_h)
            medium_button_rect = pygame.Rect(start_x + button_w + spacing, button_y, button_w, button_h)
            hard_button_rect = pygame.Rect(start_x + 2 * (button_w + spacing), button_y, button_w, button_h)

            draw_button(WIN, easy_button_rect, "Easy", BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR, FONT_BUTTON, selected_difficulty == 'Easy')
            draw_button(WIN, medium_button_rect, "Medium", BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR, FONT_BUTTON, selected_difficulty == 'Medium')
            draw_button(WIN, hard_button_rect, "Hard", BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR, FONT_BUTTON, selected_difficulty == 'Hard')

            start_button_rect = pygame.Rect(WIDTH // 2 - button_w // 2, button_y + button_h + 40, button_w, button_h)
            start_active = selected_difficulty is not None # Enable start button only after selection
            start_btn_color = BUTTON_COLOR if start_active else GREY # Dim if inactive
            start_hover_color = BUTTON_HOVER_COLOR if start_active else GREY

            if draw_button(WIN, start_button_rect, "Start", start_btn_color, start_hover_color, BUTTON_TEXT_COLOR, FONT_BUTTON):
                pass 

        elif game_state == STATE_PLAYING:
            # --- Gameplay Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if reset_button_rect.collidepoint(mouse_pos):
                        print("Reset button clicked.")
                        game.reset()
                        game_start_time = time.time() 
                        winner_info = None
                        ai_is_thinking = False
                        needs_ai_move = False
                    elif game.turn == RED and not ai_is_thinking and not needs_ai_move:
                        board_coords = get_row_col_from_mouse(mouse_pos)
                        if board_coords:
                            move_success = game.select(board_coords[0], board_coords[1])
                            if move_success and game.turn == WHITE:
                                ai_is_thinking = True
                                ai_think_start_time = pygame.time.get_ticks()
                                needs_ai_move = False

            # --- AI Turn Logic ---
            if game.turn == WHITE and needs_ai_move: # AI's turn
                is_maximizing = True # AI is white, maximizing
                value, new_board = minimax(game.get_board(), ai_depth, is_maximizing, game, float('-inf'), float('+inf'))

                if new_board is None:
                    print("AI has no valid moves!")
                else:
                    game.ai_move(new_board)
                
                needs_ai_move = False # AI has made its move

            if ai_is_thinking:
                # Check if enough time has passed
                if pygame.time.get_ticks() - ai_think_start_time >= AI_MOVE_DELAY:
                    ai_is_thinking = False
                    needs_ai_move = True # delay over, ai moves

            game.update()

            # --- Draw HUD ---
            pygame.draw.rect(WIN, HUD_BG_COLOR, (0, 0, WIDTH, HUD_HEIGHT))
            # Timer
            current_time = time.time()
            elapsed_seconds = int(current_time - game_start_time)
            minutes = elapsed_seconds // 60
            seconds = elapsed_seconds % 60
            elapsed_time_str = f"{minutes:02}:{seconds:02}"
            draw_text(WIN, f"Time: {elapsed_time_str}", FONT_HUD, TEXT_COLOR, (WIDTH // 2, HUD_HEIGHT // 2))
            
            # Piece Counts
            white_text = f"White: {game.board.white_left} ({game.board.white_kings} Kings)"
            red_text = f"Red: {game.board.red_left} ({game.board.red_kings} Kings)"

            hud_text_y = HUD_HEIGHT // 2
            draw_text(WIN, white_text, FONT_HUD, WHITE, (WIDTH * 0.25, hud_text_y))
            draw_text(WIN, red_text, FONT_HUD, RED, (WIDTH * 0.75, hud_text_y))  

            font_reset = pygame.font.SysFont(None, 24)
            draw_button(WIN, reset_button_rect, "Reset", BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR, font_reset)

            if ai_is_thinking:
                draw_text(WIN, "AI Thinking...", FONT_HUD, YELLOW, (WIDTH // 2, HUD_HEIGHT // 2 + 20)) # Below timer

            # --- Check for Winner/Stalemate ---
            if winner_info is None: 
                winner_info = game.check_winner()
                if winner_info:
                    game_state = STATE_GAME_OVER
                    print(f"Game Over! Result: {winner_info}")

        elif game_state == STATE_GAME_OVER:
            # --- Game Over Event Handling ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    run = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if play_again_button_rect.collidepoint(event.pos):
                        # Reset game
                        game.reset()
                        selected_difficulty = None
                        winner_info = None
                        ai_is_thinking = False
                        needs_ai_move = False
                        reset_from_game_over = True
                        game_state = STATE_START_MENU # Go back to menu
                    elif quit_button_rect.collidepoint(event.pos):
                        run = False # Exit main loop

            # --- Game Over Drawing ---
            if winner_info == 'STALEMATE':
                message = "Stalemate!"
            elif winner_info == WHITE:
                 message = "AI Wins!"
            else:
                 message = "Red Wins!"

            draw_text(WIN, message, FONT_TITLE, WHITE, (WIDTH // 2, HEIGHT // 3))

            button_w, button_h = 200, 60
            button_y = HEIGHT // 2 + 30
            spacing = 50
            play_again_button_rect = pygame.Rect(WIDTH // 2 - button_w - spacing // 2, button_y, button_w, button_h)
            quit_button_rect = pygame.Rect(WIDTH // 2 + spacing // 2, button_y, button_w, button_h)

            draw_button(WIN, play_again_button_rect, "Play Again", BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR, FONT_BUTTON)
            draw_button(WIN, quit_button_rect, "Quit", BUTTON_COLOR, BUTTON_HOVER_COLOR, BUTTON_TEXT_COLOR, FONT_BUTTON)


        # --- Update Display ---
        pygame.display.update()

    # --- Cleanup ---
    print("Exiting Pygame.")
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()