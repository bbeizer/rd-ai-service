# utils.py
import json
import hashlib
from copy import deepcopy

def apply_pass(game_state, from_piece, to_piece):
    """
    Returns a new game state where the ball is passed from from_piece to to_piece.
    Assumes the pass is valid.
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
    """
    board = game_state["currentBoardStatus"]

    # Sort the board keys to get consistent order
    sorted_items = sorted(board.items())  # [('a1', None), ('c1', {'color':..., ...}), ...]

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
    pieces = [
        piece for pos, piece in board.items()
        if piece and piece['color'] == color
    ]
    #print(f"Pieces for {color}: {[p['position'] for p in pieces]}")  # Log positions of pieces
    return pieces

def get_pieces_by_color_by_rank(board, rank, color):
    """
    Get all pieces on a given rank (row) of the board.
    
    Args:
        board (dict): Dictionary representing the board state.
        rank (int): The rank (row number) to filter pieces by.

    Returns:
        list: A list of pieces that are on the given rank.
    """
    pieces = [
        piece for pos, piece in board.items()
        if piece and extract_rank(pos) == rank and piece['color'] == color
    ]
    #print(f"Pieces on rank {rank}: {[p['position'] for p in pieces]}")  # Log positions of pieces
    return pieces

def get_ball_holder(pieces):
    for piece in pieces:
        if piece.get('hasBall', False):  # Use .get() to avoid errors if 'hasBall' key is missing
            return piece
    return None  # If no piece has the ball, return None

def extract_file(position):
    # Extracts the file (column) from a chess position. Converts 'a' to 1, 'b' to 2, ..., 'h' to 8.
    return ord(position[0]) - ord('a') + 1


def extract_rank(position):
    # Strip the first letter and convert the rest to an integer
    return int(position[1:])

def extract_row_col(position):
    file = position[0]  # First character (letter)
    rank = int(position[1])  # Second character (number)

    row = 8 - rank  # Convert rank (1-8) to row (7-0)
    col = ord(file) - ord('a')  # Convert file (a-h) to column (0-7)

    return row, col

def position_to_coords(pos):
    # Convert board position (e.g., "a1") to frontend-friendly row and column
    return (ord(pos[0]) - ord('a'), 8 - int(pos[1]))  # col = letter, row = inverted number


def coords_to_position(x, y):
    # Convert row and column back to board position (e.g., (0, 7) -> "a1")
    return f"{chr(x + ord('a'))}{8 - y}"
    
def is_valid_position(col, row, board):
    """
    Check if a position (col, row) is valid on the board and not occupied.
    """
    pos = coords_to_position(col, row)  # Convert to position string
    return 0 <= col < 8 and 0 <= row < 8 and (pos not in board or board[pos] is None)

def generate_piece_moves(pos, board):
    """
    Generate all valid knight moves from a given position.
    Ball holders cannot move.
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
