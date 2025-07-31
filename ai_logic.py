"""
AI Logic Module for the Game AI Service

This module implements the minimax algorithm with alpha-beta pruning
and transposition table caching for the game AI.
"""

import time
import logging
from copy import deepcopy
from game_logic import (
    check_and_return_win_for_ai,
    game_over,
    get_child_states,
    get_pieces_by_color,
    check_for_win,
    is_passable_path
)
from utils import hash_game_state, extract_file, extract_rank, get_ball_holder, validate_game_state, ensure_correct_ball_count

# Global transposition table for caching evaluated positions
transposition_table = {}

def ai_service(game_state, ai_color):
    """
    Compute the AI move using minimax and return the updated game state.
    
    Args:
        game_state (dict): Current game state
        ai_color (str): Color of the AI player ('white' or 'black')
    
    Returns:
        dict: Updated game state after AI move
    """
    # Validate input game state
    is_valid, error_msg = validate_game_state(game_state)
    if not is_valid:
        logging.error(f"Invalid game state: {error_msg}")
        # Try to fix the state
        game_state = ensure_correct_ball_count(game_state)
    
    depth = 3  # Search depth for minimax
    is_maximizing = ai_color == "white"
    
    # Check for immediate forced win
    winning_state = check_and_return_win_for_ai(game_state, ai_color)
    if winning_state:
        winning_state["status"] = 'completed'
        winning_state["winner"] = 'AI'
        winning_state["aiColor"] = ai_color
        return deepcopy(winning_state)

    # Run minimax search
    result = minimax(game_state, ai_color, depth, is_maximizing, alpha=float('-inf'), beta=float('inf'))

    # Prepare the result
    best_state = result["state"]
    best_state["currentPlayerTurn"] = "white" if ai_color == "black" else "black"
    best_state["hasMoved"] = False
    best_state["aiColor"] = ai_color
    
    # Validate and fix the result state
    is_valid, error_msg = validate_game_state(best_state)
    if not is_valid:
        logging.error(f"AI generated invalid state: {error_msg}")
        best_state = ensure_correct_ball_count(best_state)
        logging.info("Fixed AI-generated game state")
    
    return deepcopy(best_state)

def minimax(game_state, ai_color, depth, is_maximizing, alpha, beta):
    """
    Minimax algorithm with alpha-beta pruning and transposition table caching.
    
    Args:
        game_state (dict): Current game state
        ai_color (str): Color of the AI player
        depth (int): Current search depth
        is_maximizing (bool): True if maximizing player's turn
        alpha (float): Alpha value for pruning
        beta (float): Beta value for pruning
    
    Returns:
        dict: Best score and state found
    """
    # Check transposition table for cached result
    state_hash = hash_game_state(game_state)
    if state_hash in transposition_table:
        return transposition_table[state_hash]

    # Base case: leaf node or game over
    if depth == 0 or game_over(game_state):
        score = evaluate_game_state(game_state)
        result = {"score": score, "state": game_state}
        transposition_table[state_hash] = result
        return result

    best_state = None

    if is_maximizing:
        best_score = float('-inf')
        for child_state in get_child_states(game_state, is_maximizing):
            result = minimax(child_state, ai_color, depth - 1, False, alpha, beta)
            if result["score"] > best_score:
                best_score = result["score"]
                best_state = child_state
            alpha = max(alpha, best_score)
            if beta <= alpha:
                break  # Beta cutoff
    else:
        best_score = float('inf')
        for child_state in get_child_states(game_state, is_maximizing):
            result = minimax(child_state, ai_color, depth - 1, True, alpha, beta)
            if result["score"] < best_score:
                best_score = result["score"]
                best_state = child_state
            beta = min(beta, best_score)
            if beta <= alpha:
                break  # Alpha cutoff
    
    result = {"score": best_score, "state": best_state}
    transposition_table[state_hash] = result
    return result

def evaluate_game_state(game_state):
    """
    Evaluate the board state and return a numerical score.
    Positive scores favor white; negative scores favor black.
    
    Args:
        game_state (dict): Current game state
    
    Returns:
        float: Evaluation score
    """
    board = game_state['currentBoardStatus']
    white_pieces = get_pieces_by_color(board, 'white')
    black_pieces = get_pieces_by_color(board, 'black')

    white_holder = get_ball_holder(white_pieces)
    black_holder = get_ball_holder(black_pieces)
    
    # Base evaluation based on progress toward the endzone
    score = reward_progress_toward_endzone(white_pieces, black_pieces)
    
    # Adjust if a win is near
    if check_for_win(game_state, 'white'):
        score += 5000
    if check_for_win(game_state, 'black'):
        score -= 5000
    
    # Reward clear passing paths
    if white_holder:
        score += 10 * reward_path_to_goal(white_pieces, black_pieces, white_holder, 'white')
    if black_holder:
        score -= 10 * reward_path_to_goal(black_pieces, white_pieces, black_holder, 'black')
    
    # Add defensive positioning bonus
    score += 3 * reward_defensive_positioning(white_pieces, black_pieces)
    score -= 3 * reward_defensive_positioning(black_pieces, white_pieces)
    
    return score

def reward_progress_toward_endzone(white_pieces, black_pieces):
    """
    Reward pieces for advancing toward their respective endzones.
    
    Args:
        white_pieces (list): White pieces
        black_pieces (list): Black pieces
    
    Returns:
        float: Progress score
    """
    white_positions = [extract_rank(piece['position']) for piece in white_pieces]
    black_positions = [extract_rank(piece['position']) for piece in black_pieces]
    
    most_adv_white = max(white_positions) if white_positions else 1
    most_adv_black = min(black_positions) if black_positions else 8
    
    white_progress = most_adv_white - 1
    black_progress = 8 - most_adv_black
    
    return white_progress - black_progress

def reward_path_to_goal(pieces, opponent_pieces, ball_holder, player_color):
    """
    Reward having a clear passing path to the goal.
    
    Args:
        pieces (list): Player's pieces
        opponent_pieces (list): Opponent's pieces
        ball_holder (dict): Piece holding the ball
        player_color (str): Color of the player
    
    Returns:
        float: Path score
    """
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
    """
    Reward pieces for good defensive positioning against opponents.
    
    Args:
        my_pieces (list): Player's pieces
        opponent_pieces (list): Opponent's pieces
    
    Returns:
        float: Defensive score
    """
    defense_score = 0
    
    for opp in opponent_pieces:
        opp_row = extract_rank(opp['position'])
        opp_col = extract_file(opp['position'])
        
        for mine in my_pieces:
            my_row = extract_rank(mine['position'])
            my_col = extract_file(mine['position'])
            
            # Direct blocking (same column, ahead of opponent)
            if my_col == opp_col and (
                (my_row > opp_row and mine['color'] == 'white') or 
                (my_row < opp_row and mine['color'] == 'black')
            ):
                defense_score += 3
            
            # Adjacent blocking (one column away)
            if abs(my_col - opp_col) == 1 and (
                (my_row > opp_row and mine['color'] == 'white') or 
                (my_row < opp_row and mine['color'] == 'black')
            ):
                defense_score += 2
    
    return defense_score
