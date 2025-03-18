# game_logic.py
import copy
from utils import get_pieces_by_color, position_to_coords, coords_to_position, generate_piece_moves, get_pieces_by_color, extract_file, extract_rank, extract_row_col, get_ball_holder
from collections import deque
from copy import deepcopy
import pdb; 

def game_over(game_state):
    """
    Checks if the game is won OR if a player has a guaranteed winning path (even if the ball hasn't been passed yet).
    """
    board_status = game_state['currentBoardStatus']
    
    # Step 1: Check for literal wins (ball is in endzone)
    winner = check_literal_win(board_status)
    if winner:
        return winner  # Someone has already won
    
    # Step 2: Check if someone has a **guaranteed winning path**
    if check_if_win(game_state, 'white'):
        return 'white'  # White is guaranteed to win

    if check_if_win(game_state, 'black'):
        return 'black'  # Black is guaranteed to win

    return None  # No winner yet

def check_and_return_win(game_state, potential_winner):
    """
    Returns the updated game state with the win executed if a forced win exists.
    Otherwise, returns None.
    """
    board_status = game_state['currentBoardStatus']
    opponent = "black" if potential_winner == "white" else "white"
    
    # Get AI and opponent pieces
    ai_pieces = get_pieces_by_color(board_status, potential_winner)
    human_pieces = get_pieces_by_color(board_status, opponent)
    ai_ball_holder = get_ball_holder(ai_pieces)

    if not ai_ball_holder:
        return None  # No ball-holder, no forced win

    goal_row = 1 if potential_winner == 'black' else 8  

    # Find all teammates that are already in the endzone
    endzone_pieces = [p for p in ai_pieces if extract_rank(p['position']) == goal_row]

    if not endzone_pieces:
        return None  # No teammates in the endzone, no auto-win

    # **Step 1: Check if the ball-holder can pass directly to an endzone piece**
    for end_piece in endzone_pieces:
        if is_passable_path(ai_ball_holder, end_piece, human_pieces, ai_pieces):
            print(f"🔥 FORCED WIN DETECTED: {ai_ball_holder['position']} ➝ {end_piece['position']}")

            # **Create a deep copy of the game state and update it**
            updated_state = deepcopy(game_state)
            board = updated_state['currentBoardStatus']
            board[ai_ball_holder["position"]]["hasBall"] = False
            board[end_piece["position"]]["hasBall"] = True

            # **Declare the winner**
            updated_state['winner'] = potential_winner
            updated_state['status'] = 'won'
            print(f"🏆 {potential_winner.upper()} WINS!")
            return updated_state  # ✅ Directly return the updated game state

    # **Step 2: Check for an indirect win (pass through another piece)**
    for piece in ai_pieces:
        if piece == ai_ball_holder or piece in endzone_pieces:
            continue  # Skip the ball-holder and pieces already in the endzone

        if is_passable_path(ai_ball_holder, piece, human_pieces, ai_pieces):
            for end_piece in endzone_pieces:
                if is_passable_path(piece, end_piece, human_pieces, ai_pieces):
                    print(f"🔥 INDIRECT WIN DETECTED: {ai_ball_holder['position']} ➝ {piece['position']} ➝ {end_piece['position']}")

                    # **Create a deep copy and execute the indirect pass**
                    updated_state = deepcopy(game_state)
                    board = updated_state['currentBoardStatus']
                    board[ai_ball_holder["position"]]["hasBall"] = False
                    board[piece["position"]]["hasBall"] = False
                    board[end_piece["position"]]["hasBall"] = True

                    # **Declare the winner**
                    updated_state['winner'] = potential_winner
                    updated_state['playing'] = 'won'
                    print(f"🏆 {potential_winner.upper()} WINS!")
                    return updated_state  # ✅ Directly return the updated game state

    return None  # No immediate forced win found


def check_if_win(game_state, color):
    """
    Pure function that checks if a player has won, without making a move.
    """
    for position, piece in game_state['currentBoardStatus'].items():
        if piece and piece['color'] == color and piece['hasBall']:
            goal_row = 8 if color == 'white' else 1
            if extract_rank(position) == goal_row:
                return True  # This player has won
    return False



def is_passable_path(ball_holder, target_piece, opponent_pieces, team_pieces):
    """
    Checks if a ball can be passed from ball_holder to target_piece.
    - The pass must be a straight-line move (horizontal, vertical, diagonal).
    - No opponent pieces should block the path.
    - The target must be a teammate.
    """

    start_file, start_rank = position_to_coords(ball_holder['position'])
    end_file, end_rank = position_to_coords(target_piece['position'])

    # Ensure movement is straight-line (orthogonal or diagonal)
    file_step = 1 if end_file > start_file else -1 if end_file < start_file else 0
    rank_step = 1 if end_rank > start_rank else -1 if end_rank < start_rank else 0

    # Start stepping toward target
    current_file, current_rank = start_file + file_step, start_rank + rank_step

    while (current_file, current_rank) != (end_file, end_rank):
        # Ensure we stay in bounds
        if not (0 <= current_file < 8 and 0 <= current_rank < 8):
            return False  # Out of bounds

        # Convert coordinates back to board notation
        current_pos = coords_to_position(current_file, current_rank)

        # If an opponent piece is in the way, return False
        if any(p['position'] == current_pos for p in opponent_pieces):
            return False  # Blocked by opponent

        # If a teammate (not the target) is in the way, return False
        if any(p['position'] == current_pos for p in team_pieces) and current_pos != target_piece['position']:
            return False  # Blocked by teammate

        # Move forward
        current_file += file_step
        current_rank += rank_step

    return True  # Path is clear ✅




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

def get_child_states(game_state, is_maximizing):
    """
    Generate all possible child states for the current player.
    """
    board_status = game_state['currentBoardStatus']
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
    board = updated_state['currentBoardStatus']

    # Make a copy of the piece to avoid mutating the original
    updated_piece = deepcopy(piece)
    old_position = updated_piece['position']

    # Update the position of the copied piece
    updated_piece['position'] = new_position

    # Clear the old position on the board and place the updated piece
    board[old_position] = None
    board[new_position] = updated_piece

    # Switch turn to the other player
    updated_state['currentPlayerTurn'] = (
        "black" if updated_state['currentPlayerTurn'] == "white" else "white"
    )

    return updated_state
