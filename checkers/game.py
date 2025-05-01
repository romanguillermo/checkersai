import pygame
from .constants import RED, WHITE, BLUE, SQUARE_SIZE
from .board import Board

class Game:
    """ Manages game state, player turns, and AI integration. """
    def __init__(self, win):
        self._init()
        self.win = win

    def _init(self):
        """Initializes/resets game state."""
        self.selected = None
        self.board = Board()
        self.turn = RED # Red starts
        self.valid_moves = {} # Store valid moves for selected piece

    def update(self):
        """Updates display with the current game state."""
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)
        pygame.display.update()

    def winner(self):
        """Checks for a winner based on remaining pieces."""
        return self.board.winner()

    def reset(self):
        """Resets the game to the initial state."""
        self._init()

    def select(self, row, col):
        """Handles player selection of a piece or a move destination."""
        if self.selected: # If piece is already selected
            result = self._move(row, col) # Move to clicked square
            if not result: # If clicked square is not valid
                self.selected = None # Deselect
                self.select(row, col) # Re-try select on the new square
            # If move was successful, result=true, turn changes, selection cleared
            return result # Move attempted

        # If no piece selected, try to select one
        piece = self.board.get_piece(row, col)
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True # Piece successfully selected

        return False # Non selectable piece

    def _move(self, row, col):
        """Attempts to move the selected piece to (row, col)."""
        piece = self.board.get_piece(row, col)
        # Check if target square is empty and in valid moves
        if self.selected and piece == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)] # Get list of skipped pieces
            if skipped:
                self.board.remove(skipped) # Remove captured pieces
            self.change_turn()
            return True # Move successful
        else:
            return False # Move invalid

    def draw_valid_moves(self, moves):
        """Highlights the valid moves on the board."""
        for move in moves:
            row, col = move
            # Calculate center of the target square
            center_x = col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = row * SQUARE_SIZE + SQUARE_SIZE // 2
            # Draw small indicator circle
            pygame.draw.circle(self.win, BLUE, (center_x, center_y), 15)

    def change_turn(self):
        """Switches player turn and clears valid moves."""
        self.valid_moves = {}
        if self.turn == RED:
            self.turn = WHITE
        else:
            self.turn = RED
        self.selected = None # Deselect piece after turn change


    def get_board(self):
        """Returns current board object."""
        return self.board

    def ai_move(self, board):
        """Applies the move chosen by the AI."""
        self.board = board # Update board to new state returned by AI
        self.change_turn()