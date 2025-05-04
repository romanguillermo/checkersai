import pygame
from .constants import BLACK, ROWS, RED, SQUARE_SIZE, COLS, WHITE, LIGHT_WOOD, DARK_WOOD, BOARD_OFFSET_X, BOARD_OFFSET_Y
from .piece import Piece

class Board:
    """ Manages game board state and logic, includes heuristic evaluation function for AI. """
    def __init__(self):
        self.board = [] # 2d list board, contains a piece object or 0 for empty
        self.red_left = self.white_left = 12 # Starting pieces
        self.red_kings = self.white_kings = 0
        self.create_board()

    def create_board(self):
        """Initializes board with pieces in starting positions."""
        self.board = []
        self.red_left = self.white_left = 12
        self.red_kings = self.white_kings = 0
        for row in range(ROWS):
            self.board.append([])
            for col in range(COLS):
                if col % 2 == ((row + 1) % 2): # Place pieces on dark squares
                    if row < 3:
                        self.board[row].append(Piece(row, col, WHITE))
                    elif row > 4:
                        self.board[row].append(Piece(row, col, RED))
                    else:
                        self.board[row].append(0) # Empty square
                else:
                    self.board[row].append(0)

    def draw_squares(self, win):
        """Draws checker board squares."""
        # If offests create gaps, draw the background for the board area
        # pygame.draw.rect(win, DARK_WOOD, (BOARD_OFFSET_X, BOARD_OFFSET_Y, COLS * SQUARE_SIZE, ROWS * SQUARE_SIZE))
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2): # Alternate starting column
                rect_x = BOARD_OFFSET_X + col * SQUARE_SIZE
                rect_y = BOARD_OFFSET_Y + row * SQUARE_SIZE
                pygame.draw.rect(win, LIGHT_WOOD, (rect_x, rect_y, SQUARE_SIZE, SQUARE_SIZE))

    def move(self, piece, row, col):
        """Moves a piece on the board, handles kinging, and updates piece count."""
        # Swap the piece on the board grid: place piece in new spot, empty old spot
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        
        was_king = piece.king

        piece.move(row, col)

        # Check for kinging
        if not was_king and ( (row == 0 and piece.color == RED) or (row == ROWS - 1 and piece.color == WHITE) ):
            piece.make_king()
            # Update king count
            if piece.color == WHITE:
                self.white_kings += 1
            else:
                self.red_kings += 1

    def get_piece(self, row, col):
        """Returns piece object at the given coordinates."""
        if 0 <= row < ROWS and 0 <= col < COLS:
            return self.board[row][col]
        return 0

    def draw(self, win):
        """Draws entire board with squares and pieces onto window."""
        pygame.draw.rect(win, DARK_WOOD, (BOARD_OFFSET_X, BOARD_OFFSET_Y, COLS * SQUARE_SIZE, ROWS * SQUARE_SIZE))
        self.draw_squares(win)
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    piece.draw(win)

    def remove(self, pieces):
        """Removes captured pieces from board."""
        for piece in pieces:
            if piece != 0: # Ensure it's a piece object
                self.board[piece.row][piece.col] = 0
                if piece.color == RED:
                    self.red_left -= 1
                    if piece.king: self.red_kings -= 1 # Decrement king count
                elif piece.color == WHITE:
                     self.white_left -= 1
                     if piece.king: self.white_kings -= 1 # Decrement king count

    def winner(self):
        """Determines if there is a winner"""
        if self.red_left <= 0:
            return WHITE # White wins
        elif self.white_left <= 0:
            return RED # Red wins
        return None

    def get_valid_moves(self, piece):
        """Calculates all valid moves (including jumps) for a given piece."""
        moves = {} # Valid moves: { (target_row, target_col): [skipped_piece1, ...] }
        left = piece.col - 1
        right = piece.col + 1
        row = piece.row

        if piece.color == RED or piece.king:
            # Check moves moving up the board
            moves.update(self._traverse_left(row - 1, max(row - 3, -1), -1, piece.color, left))
            moves.update(self._traverse_right(row - 1, max(row - 3, -1), -1, piece.color, right))
        if piece.color == WHITE or piece.king:
            # Check moves moving down the board
            moves.update(self._traverse_left(row + 1, min(row + 3, ROWS), 1, piece.color, left))
            moves.update(self._traverse_right(row + 1, min(row + 3, ROWS), 1, piece.color, right))

        return moves

    def _traverse_left(self, start_row, stop_row, step, color, left_col, skipped_pieces=[]):
        """Helper to recursively check diagonal moves/jumps to the left."""
        moves = {}
        last_skipped = [] # Tracks piece skipped immediately before an empty square

        for r in range(start_row, stop_row, step):
            if left_col < 0: # Off the board left
                break

            current_square = self.get_piece(r, left_col) # Use get_piece for bounds check

            if current_square == 0: # Found an empty square
                if last_skipped:
                    # --- Landing after a jump ---
                    current_total_skipped = skipped_pieces + last_skipped
                    moves[(r, left_col)] = current_total_skipped

                    # --- Check for Multi-Jumps ---
                    # If we landed from a jump, check if further jumps are possible from here.
                    next_stop_row = max(r - 3, -1) if step == -1 else min(r + 3, ROWS)
                    # Crucially, pass the *current_total_skipped* list to the recursive calls.
                    moves.update(self._traverse_left(r + step, next_stop_row, step, color, left_col - 1, skipped_pieces=current_total_skipped))
                    moves.update(self._traverse_right(r + step, next_stop_row, step, color, left_col + 1, skipped_pieces=current_total_skipped))

                elif not skipped_pieces:
                    moves[(r, left_col)] = [] 
                break
            elif current_square.color == color: # Found own piece
                break # Blocked, stop searching this path
            else: # Found opponent's piece
                last_skipped = [current_square]

            # Continue diagonally left for the next iteration
            left_col -= 1

        return moves

    def _traverse_right(self, start_row, stop_row, step, color, right_col, skipped_pieces=[]):
        """Helper to recursively check diagonal moves/jumps to the right."""
        moves = {}
        last_skipped = [] # Track piece(s) skipped immediately before current square

        for r in range(start_row, stop_row, step):
            if right_col >= COLS: # Off the board right
                break

            current_square = self.get_piece(r, right_col) # Use get_piece for bounds check

            if current_square == 0: # Found an empty square
                if last_skipped:
                    # --- Landing after a jump ---
                    current_total_skipped = skipped_pieces + last_skipped
                    moves[(r, right_col)] = current_total_skipped
                    # --- Check for Multi-Jumps ---
                    next_stop_row = max(r - 3, -1) if step == -1 else min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, next_stop_row, step, color, right_col - 1, skipped_pieces=current_total_skipped))
                    moves.update(self._traverse_right(r + step, next_stop_row, step, color, right_col + 1, skipped_pieces=current_total_skipped))
                elif not skipped_pieces:
                    # --- Simple Move ---
                    moves[(r, right_col)] = []
                # Stop searching further along this path after finding a landing spot
                break
            elif current_square.color == color: # Found own piece
                break # Blocked
            else: # Found opponent's piece
                last_skipped = [current_square] # Potential jump target

            right_col += 1

        return moves


    # AI Heuristic Evaluation Function
    def evaluate(self):
        """
        Calculates and returns a heuristic score for board favorability for WHITE.
        Positive score favors WHITE, negative score favors RED.
        """
        # Simple heuristic: piece count difference + king value (more value for king piece)
        score = self.white_left - self.red_left + (self.white_kings * 0.5 - self.red_kings * 0.5)

        # Simple positional advantage: bonus for pieces advancing
        for row in range(ROWS):
            for col in range(COLS):
                piece = self.board[row][col]
                if piece != 0:
                    if piece.color == WHITE and not piece.king:
                        # Bonus for white pieces advancing down the board
                        score += (row * 0.1)
                    elif piece.color == RED and not piece.king:
                        # Bonus for red pieces advancing up the board
                        score -= ((ROWS - 1 - row) * 0.1)
        
        return score

    def get_all_pieces(self, color):
        """Returns a list of all piece objects of a given color."""
        pieces = []
        for row in self.board:
            for piece in row:
                if isinstance(piece, Piece) and piece.color == color:
                    pieces.append(piece)
        return pieces