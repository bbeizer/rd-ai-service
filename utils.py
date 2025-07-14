"""
Utility functions for the game AI service.

This module contains helper functions for game state manipulation,
position conversion, move generation, and other utility operations.
"""

import json
import hashlib
from copy import deepcopy

def apply_pass(game_state, from_piece, to_piece):
    """
    Returns a new game state where the ball is passed from from_piece to to_piece.
    Assumes the pass is valid.
    
    Args:
        game_state (dict): Current game state
        from_piece (dict): Piece passing the ball
        to_piece (dict): Piece receiving the ball
    
    Returns:
        dict: New game state with ball transferred
    """
    new_state = deepcopy(game_state)
    board = new_state["currentBoardStatus"]

    from_pos = from_piece["position"]
    to_pos = to_piece["position"]

    # Transfer ball
    board[from_pos]["hasBall"] = False
    board[to_pos]["hasBall"] = True

    return new_state

def hash_game_state(game_state):
    """
    Creates a consistent hash based on currentBoardStatus.
    
    Args:
        game_state (dict): Game state to hash
    
    Returns:
        str: SHA256 hash of the game state
    """
    board = game_state["currentBoardStatus"]

    # Sort the board keys to get consistent order
    sorted_items = sorted(board.items())

    serializable_board = []
    for position, piece in sorted_items:
        if piece is None:
            serializable_board.append((position, None))
        else:
            serializable_board.append((
                position,
                {
                    "color": piece["color"],
                    "hasBall": piece["hasBall"]
                }
            ))

    # Serialize and hash
    board_str = json.dumps(serializable_board, sort_keys=True)
    return hashlib.sha256(board_str.encode('utf-8')).hexdigest()

def get_pieces_by_color(board, color):
    """
    Get all pieces of a specific color from the board.
    
    Args:
        board (dict): Board state
        color (str): Color to filter by ('white' or 'black')
    
    Returns:
        list: List of pieces of the specified color
    """
    return [
        piece for pos, piece in board.items()
        if piece and piece['color'] == color
    ]

def get_pieces_by_color_by_rank(board, rank, color):
    """
    Get all pieces on a given rank (row) of the board.
    
    Args:
        board (dict): Dictionary representing the board state
        rank (int): The rank (row number) to filter pieces by
        color (str): Color to filter by ('white' or 'black')

    Returns:
        list: A list of pieces that are on the given rank and color
    """
    return [
        piece for pos, piece in board.items()
        if piece and extract_rank(pos) == rank and piece['color'] == color
    ]

def get_ball_holder(pieces):
    """
    Find the piece that currently holds the ball.
    
    Args:
        pieces (list): List of pieces to search through
    
    Returns:
        dict or None: The piece holding the ball, or None if no piece has the ball
    """
    for piece in pieces:
        if piece.get('hasBall', False):
            return piece
    return None

def extract_file(position):
    """
    Extract the file (column) from a chess position.
    Converts 'a' to 1, 'b' to 2, ..., 'h' to 8.
    
    Args:
        position (str): Chess position (e.g., 'a1', 'h8')
    
    Returns:
        int: File number (1-8)
    """
    return ord(position[0]) - ord('a') + 1

def extract_rank(position):
    """
    Extract the rank (row) from a chess position.
    
    Args:
        position (str): Chess position (e.g., 'a1', 'h8')
    
    Returns:
        int: Rank number (1-8)
    """
    return int(position[1:])

def extract_row_col(position):
    """
    Convert chess position to row/column coordinates.
    
    Args:
        position (str): Chess position (e.g., 'a1', 'h8')
    
    Returns:
        tuple: (row, col) where row is 0-7 and col is 0-7
    """
    file = position[0]  # First character (letter)
    rank = int(position[1])  # Second character (number)

    row = 8 - rank  # Convert rank (1-8) to row (7-0)
    col = ord(file) - ord('a')  # Convert file (a-h) to column (0-7)

    return row, col

def position_to_coords(pos):
    """
    Convert board position to frontend-friendly row and column.
    
    Args:
        pos (str): Chess position (e.g., "a1")
    
    Returns:
        tuple: (col, row) coordinates
    """
    return (ord(pos[0]) - ord('a'), 8 - int(pos[1]))

def coords_to_position(x, y):
    """
    Convert row and column back to board position.
    
    Args:
        x (int): Column coordinate (0-7)
        y (int): Row coordinate (0-7)
    
    Returns:
        str: Chess position (e.g., "a1")
    """
    return f"{chr(x + ord('a'))}{8 - y}"

def is_valid_position(col, row, board):
    """
    Check if a position (col, row) is valid on the board and not occupied.
    
    Args:
        col (int): Column coordinate
        row (int): Row coordinate
        board (dict): Board state
    
    Returns:
        bool: True if position is valid and unoccupied
    """
    pos = coords_to_position(col, row)
    return 0 <= col < 8 and 0 <= row < 8 and (pos not in board or board[pos] is None)

def generate_piece_moves(pos, board):
    """
    Generate all valid knight moves from a given position.
    Ball holders cannot move.
    
    Args:
        pos (str): Current position
        board (dict): Board state
    
    Returns:
        list: List of valid move positions
    """
    piece = board.get(pos)
    if piece and piece.get('hasBall'):
        return []

    knight_offsets = [
        (2, 1), (2, -1), (-2, 1), (-2, -1),
        (1, 2), (1, -2), (-1, 2), (-1, -2)
    ]

    legal_moves = []
    x, y = position_to_coords(pos)

    for dx, dy in knight_offsets:
        new_x, new_y = x + dx, y + dy
        if is_valid_position(new_x, new_y, board):
            legal_moves.append(coords_to_position(new_x, new_y))

    return legal_moves

def generate_ball_passes(pos, board, color):
    """
    Generate all valid ball passes from a given position to adjacent pieces of the same color.
    
    Args:
        pos (str): Current position
        board (dict): Board state
        color (str): Color of the passing player
    
    Returns:
        list: List of valid pass target positions
    """
    adjacent_offsets = [
        (1, 0), (-1, 0), (0, 1), (0, -1),
        (1, 1), (1, -1), (-1, 1), (-1, -1)  
    ]
    valid_passes = []
    x, y = position_to_coords(pos)

    for dx, dy in adjacent_offsets:
        new_x, new_y = x + dx, y + dy
        if 0 <= new_x < 8 and 0 <= new_y < 8:
            target_pos = coords_to_position(new_x, new_y)
            target_piece = board.get(target_pos)
            if target_piece and target_piece['color'] == color:
                valid_passes.append(target_pos)

    return valid_passes
