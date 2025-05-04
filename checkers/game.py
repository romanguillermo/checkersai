import pygame
from .constants import RED, WHITE, BLUE, SQUARE_SIZE, BOARD_OFFSET_X, BOARD_OFFSET_Y
from .board import Board
from .minimax import get_all_moves as get_all_possible_next_boards

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
        self.winner_result = None

    def update(self):
        """Updates display with the current game state."""
        self.board.draw(self.win)
        self.draw_valid_moves(self.valid_moves)

    def check_winner(self):
        """Checks for a winner based on remaining pieces OR stalemate."""
        # Check piece count
        winner_by_pieces = self.board.winner()
        if winner_by_pieces:
            self.winner_result = winner_by_pieces
            return self.winner_result

        # Check for stalemate: current player has no valid moves
        possible_moves = get_all_possible_next_boards(self.board, self.turn, self)
        if not possible_moves: # If list of next board states is empty
            self.winner_result = 'STALEMATE'
            # player who cannot move loses:
            # self.winner_result = WHITE if self.turn == RED else RED
            return self.winner_result

        self.winner_result = None # No winner yet
        return None

    def get_winner(self):
        """Returns the stored winner result."""
        return self.winner_result

    def reset(self):
        """Resets the game to the initial state."""
        self._init()

    def select(self, row, col):
        """Handles player selection of a piece or a move destination."""
        # Case 1: A piece is already selected
        if self.selected:
            result = self._move(row, col) # Attempt move to (row, col)
            if not result: # If click was not a valid move
                self.selected = None # Deselect
                self.valid_moves = {}
                # Try selecting the newly clicked square immediately
                self.select(row, col) # Allows changing selected piece easily
            return result # Return True if move was successful, False otherwise

        # Case 2: No piece selected, try to select one
        piece = self.board.get_piece(row, col)
        # Check if valid piece of current player
        if piece != 0 and piece.color == self.turn:
            self.selected = piece
            self.valid_moves = self.board.get_valid_moves(piece)
            return True # Piece selected

        return False

    def _move(self, row, col):
        """Attempts to move the selected piece to (row, col)."""
         # Target square must be empty and be a key in valid_moves dict
        if self.selected and self.board.get_piece(row, col) == 0 and (row, col) in self.valid_moves:
            self.board.move(self.selected, row, col)
            skipped = self.valid_moves[(row, col)] # Get list of skipped pieces
            if skipped:
                self.board.remove(skipped) # Remove captured pieces
            self.change_turn() # Successful move, change turn
            return True
        # Invalid move target
        return False

    def draw_valid_moves(self, moves):
        """Highlights the valid moves on the board."""
        for move in moves:
            row, col = move
            # Calculate center of the target square
            center_x = BOARD_OFFSET_X + col * SQUARE_SIZE + SQUARE_SIZE // 2
            center_y = BOARD_OFFSET_Y + row * SQUARE_SIZE + SQUARE_SIZE // 2
            # Draw small indicator circle
            pygame.draw.circle(self.win, BLUE, (center_x, center_y), 15)

    def change_turn(self):
        """Switches player turn and clears valid moves."""
        self.valid_moves = {}
        self.selected = None
        if self.turn == RED:
            self.turn = WHITE
        else:
            self.turn = RED


    def get_board(self):
        """Returns current board object."""
        return self.board

    def ai_move(self, board):
        """Applies the move chosen by the AI."""
        self.board = board # Update board to new state returned by AI
        self.change_turn() # AI finished, change turn back