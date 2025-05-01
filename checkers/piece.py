import pygame
from .constants import RED, WHITE, SQUARE_SIZE, GREY, CROWN

class Piece:
    """ Represents a checker piece."""

    PADDING = 15
    OUTLINE = 2

    def __init__(self, row, col, color):
        """Initializes a piece with row, column, and color."""
        self.row = row
        self.col = col
        self.color = color
        self.king = False
        self.x = 0
        self.y = 0
        self.calc_pos()

    def calc_pos(self):
        """Calculates screen x, y coordinates based on row, col."""
        self.x = SQUARE_SIZE * self.col + SQUARE_SIZE // 2
        self.y = SQUARE_SIZE * self.row + SQUARE_SIZE // 2

    def make_king(self):
        self.king = True

    def draw(self, win):
        """Draws the piece on game window."""
        radius = SQUARE_SIZE // 2 - self.PADDING
        # Draw grey outline
        pygame.draw.circle(win, GREY, (self.x, self.y), radius + self.OUTLINE)
        # Draw piece color
        pygame.draw.circle(win, self.color, (self.x, self.y), radius)
        # Draw crown if piece is king
        if self.king:
            win.blit(CROWN, (self.x - CROWN.get_width() // 2, self.y - CROWN.get_height() // 2))

    def move(self, row, col):
        """Updates the piece's row and column and recalculates position."""
        self.row = row
        self.col = col
        self.calc_pos()

    def __repr__(self):
        """String representation for debugging."""
        return str(self.color)