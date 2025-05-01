from copy import deepcopy # Deepcopy for board state simulations 
import pygame
from .constants import RED, WHITE

def minimax(current_board_state, depth, is_max_player, game, alpha, beta):
    """
    Minimax algorithm w Alpha-Beta pruning.

    current_board_state: Current Board object state to evaluate.
    depth: Move depth to search.
    is_max_player: (bool) True if maximizing (AI turn), False if minimizing (Opponent turn).
    game: Main Game object.
    alpha: Alpha value for pruning.
    beta: Beta value for pruning.

    Returns: [move_evaluation_score, best_move_board_state]
    """
    # --- Base Cases ---
    # 1. Reached maximum search depth
    # 2. A player has won (no opponent pieces left)
    if depth == 0 or current_board_state.winner() is not None:
        # Return static evaluation of the board and the board itself (no further move from here)
        return current_board_state.evaluate(), current_board_state

    # --- Recursive Step ---
    if is_max_player: # AI's turn (wants to maximize score)
        max_eval = float('-inf') # Initialize with lowest possible score
        best_move_board = None   # Track board state leading to max_eval

        # Iterate through all possible moves (resulting board states) for the maximizer
        for potential_next_board in get_all_moves(current_board_state, WHITE, game):
            # Recursively call minimax for opponent's turn (minimizer)
            # Depth is decreased by 1, is_max_player is False
            evaluation, _ = minimax(potential_next_board, depth - 1, False, game, alpha, beta)

            # Update max_eval if this move leads to a better score
            if evaluation > max_eval:
                max_eval = evaluation
                best_move_board = potential_next_board # Store this board state

            # Alpha-Beta Pruning Check (Maximizer)
            alpha = max(alpha, evaluation) # Update alpha (best option for maximizer found so far)
            if beta <= alpha:
                # If beta <= alpha, the minimizing player (parent node) would have already pruned this branch
                break # Prune this branch, stop exploring further moves from this state

        return max_eval, best_move_board

    else: # Minimizing player's turn (wants to minimize the score for ai)
        min_eval = float('+inf') # Initialize with highest possible score
        best_move_board = None   # Track board state leading to min_eval

        # Iterate through all possible moves (resulting board states) for the minimizer
        for potential_next_board in get_all_moves(current_board_state, RED, game):
            # Recursively call minimax for maximizer's turn
            # Depth is decreased by 1, is_max_player is True
            evaluation, _ = minimax(potential_next_board, depth - 1, True, game, alpha, beta)

            # Update min_eval if this move leads to a lower score (better for minimizer)
            if evaluation < min_eval:
                min_eval = evaluation
                best_move_board = potential_next_board

            # Alpha-Beta Pruning Check (Minimizer)
            beta = min(beta, evaluation) # Update beta (best option for minimizer found so far)
            if beta <= alpha:
                # If beta <= alpha, maximizing player (parent node) will prune this branch.
                break 

        return min_eval, best_move_board


def simulate_move(piece, move_coords, board_copy, skipped_pieces):
    """
    Simulates making a move on copy of board.
    Modifies board copy to reflect the move and any captures.
    """
    # Perform move on the copied board
    board_copy.move(piece, move_coords[0], move_coords[1])
    # If pieces were captured during this move, remove them from the copied board
    if skipped_pieces:
        board_copy.remove(skipped_pieces)
    return board_copy

def get_all_moves(board, color, game):
    """Generates all possible board states reachable in one turn by given color."""
    possible_next_boards = [] # List to store resulting board states
 
    # Iterate through all pieces of the given color on the board
    for piece in board.get_all_pieces(color):
        # Get all valid moves (including jumps) for the current piece
        valid_moves = board.get_valid_moves(piece) # Returns {(row, col): [skipped]}

        # For each valid move destination
        for move_coords, skipped_pieces_info in valid_moves.items():
            # Create a deep copy of the board for simulation and avoid modifying original
            temp_board = deepcopy(board)
            temp_piece = temp_board.get_piece(piece.row, piece.col)
            temp_skipped_pieces = [temp_board.get_piece(p.row, p.col) for p in skipped_pieces_info]

            # Simulate the move on temporary board copy
            new_board_state = simulate_move(temp_piece, move_coords, temp_board, temp_skipped_pieces)

            # Add resulting board state to our list of possibilities
            possible_next_boards.append(new_board_state)

    return possible_next_boards