# utils.py

def get_pieces_by_color(board_status, color):
    pieces = [
        piece for pos, piece in board_status.items()
        if piece and piece['color'] == color
    ]
    print(f"Pieces for {color}: {[p['position'] for p in pieces]}")  # Log positions of pieces
    return pieces

def get_ball_holder(pieces):
    for piece in pieces:
        if piece.get('hasBall', False):  # Use .get() to avoid errors if 'hasBall' key is missing
            return piece
    return None  # If no piece has the ball, return None

def get_ai_color(color):
    return color

def extract_file(position):
    # Extracts the file (column) from a chess position. Converts 'a' to 1, 'b' to 2, ..., 'h' to 8.
    return ord(position[0]) - ord('a') + 1


def extract_rank(position):
    # Strip the first letter and convert the rest to an integer
    return int(position[1:])


def position_to_coords(pos):
    # Convert board position (e.g., "a1") to frontend-friendly row and column
    return (ord(pos[0]) - ord('a'), 8 - int(pos[1]))  # col = letter, row = inverted number


def coords_to_position(x, y):
    # Convert row and column back to board position (e.g., (0, 7) -> "a1")
    return f"{chr(x + ord('a'))}{8 - y}"
    
def is_valid_position(col, row, board_status):
    """
    Check if a position (col, row) is valid on the board and not occupied.
    """
    pos = coords_to_position(col, row)  # Convert to position string
    return 0 <= col < 8 and 0 <= row < 8 and (pos not in board_status or board_status[pos] is None)

def generate_piece_moves(pos, board_status):
    """
    Generate all valid knight moves from a given position.
    """
    knight_offsets = [
        (2, 1), (2, -1), (-2, 1), (-2, -1),
        (1, 2), (1, -2), (-1, 2), (-1, -2)
    ]
    legal_moves = []
    x, y = position_to_coords(pos)

    for dx, dy in knight_offsets:
        new_x, new_y = x + dx, y + dy
        if is_valid_position(new_x, new_y, board_status):
            legal_moves.append(coords_to_position(new_x, new_y))
    print(f"Moves generated for {pos}: {legal_moves}")
    return legal_moves


def generate_ball_passes(pos, board_status, color):
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
            target_piece = board_status.get(target_pos)
            if target_piece and target_piece['color'] == color:
                valid_passes.append(target_pos)

    return valid_passes
