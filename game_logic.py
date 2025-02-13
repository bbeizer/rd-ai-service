# game_logic.py
import copy
from utils import get_pieces_by_color, position_to_coords, coords_to_position, is_valid_position, generate_piece_moves, get_pieces_by_color, extract_file, extract_rank, get_ball_holder
from copy import deepcopy


def game_over(game_state):
    """
    Checks if the game is won OR if a player has a guaranteed winning path (even if the ball hasn't been passed yet).
    """
    board_status = game_state['gameData']['currentBoardStatus']
    
    # Step 1: Check for literal wins (ball is in endzone)
    winner = check_literal_win(board_status)
    if winner:
        return winner  # Someone has already won
    
    # Step 2: Check if someone has a **guaranteed winning path**
    if has_forced_win(game_state, 'white'):
        return 'white'  # White is guaranteed to win

    if has_forced_win(game_state, 'black'):
        return 'black'  # Black is guaranteed to win

    return None  # No winner yet

def has_forced_win(game_state, player_color):
    """
    Returns True if the player has a guaranteed passing sequence to score.
    """
    board_status = game_state['gameData']['currentBoardStatus']
    pieces = get_pieces_by_color(board_status, player_color)
    ball_holder = get_ball_holder(pieces)

    if not ball_holder:
        return False  # No ball-holder, no forced win

    goal_row = 1 if player_color == 'black' else 8  # Black AI scores on row 1, White scores on row 8

    # Find all teammates that are already in the endzone
    endzone_pieces = [p for p in pieces if extract_rank(p['position']) == goal_row]

    if not endzone_pieces:
        return False  # No teammates in the endzone, no auto-win

    # Check if the ball-holder can pass to an endzone piece without an opponent blocking
    opponent_pieces = get_pieces_by_color(board_status, get_ai_color())  # Get the opponent's pieces
    for end_piece in endzone_pieces:
        if is_passable_path(ball_holder, end_piece, opponent_pieces, pieces):
            print(f"🔥 {player_color.upper()} has a forced win! {ball_holder['position']} can pass to {end_piece['position']}")
            return True  # Player can guarantee a win

    return False  # No forced win found



def check_literal_win(board_status):
    """
    Checks if a player has won the game by reaching the end zone with the ball.
    Returns 'white' if White wins, 'black' if Black wins, or None if no literal win.
    """
    white_pieces = get_pieces_by_color(board_status, 'white')
    black_pieces = get_pieces_by_color(board_status, 'black')

    # Check White pieces for a win
    for piece in white_pieces:
        if piece['hasBall']:  # Only check pieces with the ball
            rank = extract_rank(piece['position'])
            if rank == 8:  # White wins if they reach rank 8 with the ball
                return 'white'

    # Check Black pieces for a win
    for piece in black_pieces:
        if piece['hasBall']:  # Only check pieces with the ball
            rank = extract_rank(piece['position'])
            if rank == 1:  # Black wins if they reach rank 1 with the ball
                return 'black'

    return None  # No literal win detected


def is_passable_path(ball_holder, target_piece, opponent_pieces, all_pieces):
    """
    Determines if the ball-holder can pass to the target piece without an opponent blocking.
    """
    ball_position = ball_holder['position']
    target_position = target_piece['position']

    # Convert board positions to (file, rank)
    ball_file, ball_rank = extract_file(ball_position), extract_rank(ball_position)
    target_file, target_rank = extract_file(target_position), extract_rank(target_position)

    # Generate the list of squares the ball must pass through
    path_squares = get_path_squares(ball_file, ball_rank, target_file, target_rank)

    # Check if any opponent pieces are blocking the path
    for piece in opponent_pieces:
        if piece['position'] in path_squares:
            return False  # Pass is blocked

    return True  # No opponent blocking, pass is possible

def get_path_squares(start_file, start_rank, end_file, end_rank):
    """
    Returns a list of board squares representing the path from (start_file, start_rank)
    to (end_file, end_rank) in a straight line.
    """
    path = []
    
    file_step = 1 if end_file > start_file else -1 if end_file < start_file else 0
    rank_step = 1 if end_rank > start_rank else -1 if end_rank < start_rank else 0

    current_file, current_rank = start_file + file_step, start_rank + rank_step

    while (current_file, current_rank) != (end_file, end_rank):
        path.append(f"{chr(current_file + ord('a'))}{current_rank}")  # Convert (file, rank) to board notation
        current_file += file_step
        current_rank += rank_step

    return path


def get_child_states(game_state, is_maximizing):
    """
    Generate all possible child states for the current player.
    """
    board_status = game_state['gameData']['currentBoardStatus']
    current_player = 'white' if is_maximizing else 'black'
    pieces = get_pieces_by_color(board_status, current_player)
    child_states = []

    print(f"Generating child states for {'maximizing' if is_maximizing else 'minimizing'} player: {current_player}")

    for piece in pieces:
        print(f"Processing piece at {piece['position']}")
        possible_moves = generate_piece_moves(piece['position'], board_status)
        for move in possible_moves:
            updated_state = update_board(game_state, piece, move)
            print(f"Updated board after moving {piece['position']} -> {move}")
            child_states.append(updated_state)

    print(f"Total child states generated: {len(child_states)}")
    return child_states


def update_board(game_state, piece, new_position):
    """
    Updates the game board by moving the specified piece to the new position.
    Ensures the original game state remains untouched.
    """
    # Deepcopy the game state to ensure immutability
    updated_state = deepcopy(game_state)
    board = updated_state['gameData']['currentBoardStatus']

    # Make a copy of the piece to avoid mutating the original
    updated_piece = deepcopy(piece)
    old_position = updated_piece['position']

    # Update the position of the copied piece
    updated_piece['position'] = new_position

    # Clear the old position on the board and place the updated piece
    board[old_position] = None
    board[new_position] = updated_piece

    # Switch turn to the other player
    updated_state['gameData']['currentPlayerTurn'] = (
        "black" if updated_state['gameData']['currentPlayerTurn'] == "white" else "white"
    )

    return updated_state
