import pygame
import sys

from checkers.constants import WIDTH, HEIGHT, SQUARE_SIZE, RED, WHITE, BLUE
from checkers.game import Game
from checkers.minimax import minimax

FPS = 60
AI_DEPTH = 3 # Depth of the minimax search tree, adjust for difficulty lvl

# Pygame initialization
pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Checkers')

def get_row_col_from_mouse(pos):
    """Converts mouse click position (x, y) to board (row, col)."""
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return row, col

def main():
    """Main game loop."""
    run = True
    clock = pygame.time.Clock()
    game = Game(WIN)
    ai_color = WHITE
    human_color = RED

    while run:
        clock.tick(FPS)

        # AI's turn
        if game.turn == ai_color:
            is_maximizing = (ai_color == WHITE)
            value, new_board = minimax(game.get_board(), AI_DEPTH, is_maximizing, game, float('-inf'), float('+inf'))

            if new_board is None:
                print(f"{'White' if ai_color == WHITE else 'Red'} (AI) has no valid moves!")
                winner_check = game.winner() # Re-check winner if AI had no move
                if winner_check is not None:
                     print(f"Immediate Winner after AI no-move check: {'WHITE' if winner_check == WHITE else 'RED'}")
                     run = False
                else:
                     print("Stalemate likely or other player wins as AI cannot move.")
                     run = False # End game on stalemate

            else:
                game.ai_move(new_board)


        # Check for winner
        if run:
            winner = game.winner()
            if winner is not None:
                print(f"WINNER DETECTED: {'WHITE' if winner == WHITE else 'RED'}")
                display_winner_message(WIN, winner)
                run = False # End game loop

        # Event Handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if event.type == pygame.MOUSEBUTTONDOWN:
                if game.turn == human_color: 
                    pos = pygame.mouse.get_pos()
                    row, col = get_row_col_from_mouse(pos)
                    game.select(row, col)

        # Update Display
        if run: 
             game.update()

    print("Game Over.")
    pygame.quit()
    sys.exit()

def display_winner_message(window, winner_color):
    """Displays a simple winner message on the screen."""
    font = pygame.font.SysFont('comicsans', 80)
    text = f"{'WHITE' if winner_color == WHITE else 'RED'} WINS!"
    render_text = font.render(text, 1, BLUE)
    text_rect = render_text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    bg_rect = pygame.Rect(text_rect.left - 20, text_rect.top - 20, text_rect.width + 40, text_rect.height + 40)
    bg_surf = pygame.Surface(bg_rect.size, pygame.SRCALPHA) 
    bg_surf.fill((200, 200, 200, 180)) 
    window.blit(bg_surf, bg_rect.topleft)
    window.blit(render_text, text_rect)
    pygame.display.update() 
    pygame.time.wait(3000) 

if __name__ == '__main__':
    main()