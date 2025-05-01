import pygame
from .constants import BLACK, ROWS, RED, SQUARE_SIZE, COLS, WHITE, LIGHT_WOOD, DARK_WOOD
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
        win.fill(DARK_WOOD)
        for row in range(ROWS):
            for col in range(row % 2, COLS, 2): # Alternate starting column
                pygame.draw.rect(win, LIGHT_WOOD, (row * SQUARE_SIZE, col * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

    def move(self, piece, row, col):
        """Moves a piece on the board, handles kinging, and updates piece count."""
        # Swap the piece on the board grid: place piece in new spot, empty old spot
        self.board[piece.row][piece.col], self.board[row][col] = self.board[row][col], self.board[piece.row][piece.col]
        piece.move(row, col)

        # Check for kinging
        if row == ROWS - 1 or row == 0: # If piece reaches opposite end
            if not piece.king:
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
        return None # Out of bounds

    def draw(self, win):
        """Draws entire board with squares and pieces onto window."""
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
                else:
                    self.white_left -= 1

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

    def _traverse_left(self, start, stop, step, color, left, skipped=[]):
        """Helper to recursively check diagonal moves/jumps to the left."""
        moves = {}
        last = [] # Last skipped piece

        for r in range(start, stop, step):
            if left < 0: # Off the board left
                break

            current_square = self.board[r][left]

            if current_square == 0: # Empty square 
                if skipped and not last: # Can't move to empty square after skipping
                    break
                elif skipped: # Valid jump landing spot
                    moves[(r, left)] = last + skipped
                else: # Regular move
                    moves[(r, left)] = last

                if last: # If we just jumped over a piece
                    if step == -1: # Moving up
                        row = max(r - 3, -1)
                    else: # Moving down
                        row = min(r + 3, ROWS)
                    # Check for further jumps from this landing spot
                    moves.update(self._traverse_left(r + step, row, step, color, left - 1, skipped=moves[(r, left)]))
                    moves.update(self._traverse_right(r + step, row, step, color, left + 1, skipped=moves[(r, left)]))
                break # Stop searching this direction after finding empty square or landing spot

            elif current_square.color == color: # Own piece blocking
                break
            else: # Found opponent piece
                last = [current_square] # Potential piece to jump over

            left -= 1 # Move diagonally left

        return moves

    def _traverse_right(self, start, stop, step, color, right, skipped=[]):
        """Helper to recursively check diagonal moves/jumps to the right."""
        moves = {}
        last = []

        for r in range(start, stop, step):
            if right >= COLS: # Off the board right
                break

            current = self.board[r][right]
            if current == 0: # Empty square
                if skipped and not last:
                    break
                elif skipped:
                    moves[(r, right)] = last + skipped
                else:
                    moves[(r, right)] = last

                if last:
                    if step == -1:
                        row = max(r - 3, -1)
                    else:
                        row = min(r + 3, ROWS)
                    moves.update(self._traverse_left(r + step, row, step, color, right - 1, skipped=moves[(r, right)]))
                    moves.update(self._traverse_right(r + step, row, step, color, right + 1, skipped=moves[(r, right)]))
                break

            elif current.color == color: # Own piece
                break
            else: # Opponent piece
                last = [current]

            right += 1 # Move diagonally right

        return moves

    # AI Heuristic Evaluation Function
    def evaluate(self):
        """
        Calculates and returns a heuristic score for board favorability for WHITE.
        Positive score favors WHITE, negative score favors RED.
        """
        # Simple heuristic: piece count difference + king value (more value for king piece)
        score = self.white_left - self.red_left + (self.white_kings * 0.5 - self.red_kings * 0.5)

        # --- Potential Enhancements (Optional) ---
        # 1. Positional Advantage: Give bonuses for pieces in center, advancing, etc.
        #    Ex: Bonus for pieces closer to becoming kings.
        # for row in range(ROWS):
        #     for col in range(COLS):
        #         piece = self.board[row][col]
        #         if piece != 0:
        #             if piece.color == WHITE:
        #                 # Bonus for white pieces advancing down the board
        #                 score += (row * 0.1) if not piece.king else 0
        #             else:
        #                 # Bonus for red pieces advancing up the board
        #                 score -= ((ROWS - 1 - row) * 0.1) if not piece.king else 0

        # 2. Piece Safety: Penalize pieces that are immediately threatened.
        # 3. Control of Center: Bonus for controlling center squares.
        # 4. Mobility: Count possible moves for each piece and add to score.
        
        return score

    def get_all_pieces(self, color):
        """Returns a list of all piece objects of a given color."""
        pieces = []
        for row in self.board:
            for piece in row:
                if piece != 0 and piece.color == color:
                    pieces.append(piece)
        return pieces