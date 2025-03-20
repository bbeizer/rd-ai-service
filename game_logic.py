# game_logic.py
import copy
from hashlib import new
from utils import get_pieces_by_color, position_to_coords, coords_to_position, generate_piece_moves, get_pieces_by_color, get_pieces_by_color_by_rank, extract_rank, get_ball_holder, pass_ball
from collections import deque
from copy import deepcopy

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
    if check_for_win(game_state, 'white'):
        return 'white'  # White is guaranteed to win

    if check_for_win(game_state, 'black'):
        return 'black'  # Black is guaranteed to win

    return None  # No winner yet

def check_and_return_win_for_ai(game_state, ai_color):
    """
    Check if the AI can win immediately by moving or passing.
    """
    human_color = 'white' if ai_color == 'black' else 'black'
    board = game_state["currentBoardStatus"]
    human_pieces = get_pieces_by_color(board, human_color)
    ai_pieces = get_pieces_by_color(board, ai_color)
    ai_is_maximizing = True if ai_color == 'white' else False
    back_rank = 8 if ai_is_maximizing else 1
    print(f"{ai_is_maximizing}")
    print(f"{back_rank}")
    #Check for move + pass combinations
    for piece in ai_pieces:
        # Generate possible moves
        possible_moves = get_child_states(game_state, ai_is_maximizing)  # Assuming True means AI moves
        for state in possible_moves:
            get_pieces_by_color(state['currentBoardStatus'], ai_color)
        for new_state in possible_moves:
            new_board = new_state["currentBoardStatus"]
            ball_holder = get_ball_holder(get_pieces_by_color(new_board, ai_color))
            backRankPieces = get_pieces_by_color_by_rank(new_board, back_rank, ai_color)
            for end_piece in backRankPieces:
                if is_passable_path(ball_holder, end_piece, human_pieces, ai_pieces):
                        print(f"🚨 Win found via move + pass for {ai_color}!")
                        return deepcopy(new_state)  # ✅ Return winning state
        return None

from collections import deque

def is_passable_path(ball_holder, target_piece, opponent_pieces, team_pieces):
    """
    Checks if a ball can be passed from ball_holder to target_piece via direct passes or teammate relays.
    - The pass must be a straight-line move (horizontal, vertical, diagonal).
    - Opponent pieces **block** the pass.
    - Teammates **do not** block the pass and can **relay** the ball.
    """

    print(f"\n🔍 Checking pass chain from {ball_holder['position']} to {target_piece['position']}")

    # Directions for possible passes (orthogonal + diagonal)
    directions = [
        (1, 0), (-1, 0),  # Horizontal (right, left)
        (0, 1), (0, -1),  # Vertical (up, down)
        (1, 1), (1, -1), (-1, 1), (-1, -1)  # Diagonal
    ]

    queue = deque([ball_holder])  # Start BFS with the ball holder
    visited = set()  # Track visited pieces to prevent loops

    while queue:
        current_piece = queue.popleft()
        current_file, current_rank = position_to_coords(current_piece['position'])
        visited.add(current_piece['position'])

        for file_step, rank_step in directions:
            temp_file, temp_rank = current_file + file_step, current_rank + rank_step
            path_positions = []  # Track path for debugging

            while 0 <= temp_file < 8 and 0 <= temp_rank < 8:
                current_pos = coords_to_position(temp_file, temp_rank)
                path_positions.append(current_pos)

                # **Opponent blocks the path**
                if any(p['position'] == current_pos for p in opponent_pieces):
                    print(f"❌ Blocked by opponent at {current_pos}, stopping direction.")
                    break  # Stop looking in this direction

                # **If we reached the target piece, return True ✅**
                if current_pos == target_piece['position']:
                    print(f"✅ Winning pass found! Path: {path_positions}")
                    pass_ball(ball_holder, target_piece)
                    return True  # Found a valid pass

                # **If a teammate is in the path, enqueue them for another pass attempt**
                teammate = next((p for p in team_pieces if p['position'] == current_pos), None)
                if teammate and teammate['position'] not in visited:
                    print(f"🔄 Pass possible to teammate at {current_pos}, adding to queue.")
                    queue.append(teammate)  # Continue searching from this teammate
                    visited.add(teammate['position'])
                    break  # Stop further movement in this direction

                # Move further along this direction
                temp_file += file_step
                temp_rank += rank_step

    print(f"❌ No passable path found from {ball_holder['position']} to {target_piece['position']}")
    return False  # No valid path found

def check_for_win(game_state, color):
    """
    Pure function that checks if a player has won, without making a move.
    """
    for position, piece in game_state['currentBoardStatus'].items():
        if piece and piece['color'] == color and piece['hasBall']:
            goal_row = 8 if color == 'white' else 1
            if extract_rank(position) == goal_row:
                return True  # This player has won
    return False

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
    current_color_being_evaluated = 'white' if is_maximizing else 'black'
    pieces = get_pieces_by_color(board_status, current_color_being_evaluated)
    child_states = []

    #print(f"Generating child states for {'maximizing' if is_maximizing else 'minimizing'} player: {current_color_being_evaluated}")

    for piece in pieces:
        #print(f"Processing piece at {piece['position']}")
        possible_moves = generate_piece_moves(piece['position'], board_status)
        for move in possible_moves:
            updated_state = update_board(game_state, piece, move)
            #print(f"Updated board after moving {piece['position']} -> {move}")
            child_states.append(updated_state)

    #print(f"Total child states generated: {len(child_states)}")
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
