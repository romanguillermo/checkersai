import pygame

# Game window/board dimensions
WIDTH, HEIGHT = 800, 800
ROWS, COLS = 8, 8
SQUARE_SIZE = WIDTH // COLS

# Color constants (rgb)
RED = (255, 0, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255) # possible move
GREY = (128, 128, 128)
DARK_WOOD = (139, 69, 19)
LIGHT_WOOD = (210, 180, 140)

# Crown piece image
CROWN = pygame.transform.smoothscale(pygame.image.load('./checkers/assets/crown.png'), (36, 36)) 