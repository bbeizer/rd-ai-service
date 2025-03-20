# ai_service.py
from copy import deepcopy
from game_logic import (
    check_and_return_win_for_ai,
    game_over,
    get_child_states,
    get_pieces_by_color,
    check_for_win,
    is_passable_path
)
from utils import extract_file, extract_rank, get_ball_holder

# (Optional) If you later want caching at the base level:
transposition_table = {}

def ai_service(game_state):
    """
    Compute the AI move using minimax and return the updated game state.
    Immediate forced win detection is done at the base case.
    """
    depth = 1  # Adjust as needed for lookahead
    print("🚀 STARTING MINIMAX")
    ai_color = game_state["aiColor"]
    is_maximizing = True if ai_color == "white" else False
    result = minimax(game_state, ai_color, depth, is_maximizing)
    best_state = result["state"]
    
    print(f"✅ Best move chosen with score: {result['score']}")
    print("💾 Deepcopying the best state to return...")
    return deepcopy(best_state)

def minimax(game_state, ai_color, depth, is_maximizing):
    print(f"{'Maximizing' if is_maximizing else 'Minimizing'} at depth {depth}")
    
    # Base case: if depth is 0 or game is over, evaluate the state.
    if depth == 0 or game_over(game_state):
        score = evaluate_game_state(game_state)
        return {"score": score, "state": game_state}  # ✅ Returning only score at depth 0
    
    best_state = None
    if is_maximizing:
        best_score = float('-inf')
        for child_state in get_child_states(game_state, is_maximizing):
            result = minimax(child_state, ai_color, depth - 1, False)
            if result["score"] > best_score:
                best_score = result["score"]
                best_state = child_state  # ✅ Store best move
    else:
        best_score = float('inf')
        for child_state in get_child_states(game_state, is_maximizing):
            result = minimax(child_state, ai_color, depth - 1, True)
            if result["score"] < best_score:
                best_score = result["score"]
                best_state = child_state  # ✅ Store best move
    
    return {"score": best_score, "state": best_state}  # ✅ Return game state at depth N


def generate_state_key(game_state):
    """
    Generate a unique key for a game state (e.g., using the sorted board positions).
    This can be used for a transposition table if you wish.
    """
    return str(sorted(
        (pos, piece["color"], piece["hasBall"])
        for pos, piece in game_state["currentBoardStatus"].items() if piece
    ))

def evaluate_game_state(game_state):
    """
    Evaluate the board state and return a numerical score.
    Positive scores favor white; negative scores favor black.
    """
    board = game_state['currentBoardStatus']
    white_pieces = get_pieces_by_color(board, 'white')
    black_pieces = get_pieces_by_color(board, 'black')

    white_holder = get_ball_holder(white_pieces)
    black_holder = get_ball_holder(black_pieces)
    
    # Base evaluation based on progress toward the endzone.
    score = reward_progress_toward_endzone(white_pieces, black_pieces)
    
    # Adjust if a win is near.
    if check_for_win(game_state, 'white'):
        score += 5000
    if check_for_win(game_state, 'black'):
        score -= 5000
    
    # Reward a clear passing path.
    if white_holder:
        score += 10 * reward_path_to_goal(white_pieces, black_pieces, white_holder, 'white')
    if black_holder:
        score -= 10 * reward_path_to_goal(black_pieces, white_pieces, black_holder, 'black')
    
    # Add defensive positioning bonus.
    score += 3 * reward_defensive_positioning(white_pieces, black_pieces)
    score -= 3 * reward_defensive_positioning(black_pieces, white_pieces)
    
    print(f"[Evaluation] Score: {score}")
    return score

def reward_progress_toward_endzone(white_pieces, black_pieces):
    score = 0
    white_positions = [extract_rank(piece['position']) for piece in white_pieces]
    black_positions = [extract_rank(piece['position']) for piece in black_pieces]
    
    most_adv_white = max(white_positions) if white_positions else 1
    most_adv_black = min(black_positions) if black_positions else 8
    
    white_progress = most_adv_white - 1
    black_progress = 8 - most_adv_black
    
    score += white_progress
    score -= black_progress
    return score

def reward_path_to_goal(pieces, opponent_pieces, ball_holder, player_color):
    goal_row = 8 if player_color == 'white' else 1
    path_score = 0
    endzone_pieces = [p for p in pieces if extract_rank(p['position']) == goal_row]
    if not endzone_pieces:
        return 0
    for end_piece in endzone_pieces:
        if is_passable_path(ball_holder, end_piece, opponent_pieces, pieces):
            path_score += 10
    return path_score

def reward_defensive_positioning(my_pieces, opponent_pieces):
    defense_score = 0
    for opp in opponent_pieces:
        opp_row = extract_rank(opp['position'])
        opp_col = extract_file(opp['position'])
        for mine in my_pieces:
            my_row = extract_rank(mine['position'])
            my_col = extract_file(mine['position'])
            if my_col == opp_col and ((my_row > opp_row and mine['color'] == 'white') or (my_row < opp_row and mine['color'] == 'black')):
                defense_score += 3
            if abs(my_col - opp_col) == 1 and ((my_row > opp_row and mine['color'] == 'white') or (my_row < opp_row and mine['color'] == 'black')):
                defense_score += 2
    return defense_score
