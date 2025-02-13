# ai_logic.py
from copy import deepcopy
from game_logic import game_over, get_child_states, get_pieces_by_color
from utils import get_ai_color, extract_file, extract_rank, get_ball_holder

def ai_service(game_state):
    """
    Perform the AI move by calling minimax and returning the updated game state.
    """
    depth = 1  # You can adjust the depth
    print("STARTING MINIMAX")
    result = minimax(game_state, depth, is_maximizing=False)
    best_state = result["state"]  # Extract the best state

    # Force current player turn to 'white'
    best_state['gameData']['currentPlayerTurn'] = 'white'
    # Log object at letter6 before deepcopy
    letter6_positions = ['e6', 'd6', 'f6', 'c6']  # Add relevant positions
    print("Objects at letter6 before deepcopy:")
    for pos in letter6_positions:
        print(f"{pos}: {best_state['gameData']['currentBoardStatus'].get(pos)}")
    
    print(f"Best state chosen with score: {result['score']}")
    print("About to Deepcopy the best state...")

    # Deepcopy the state
    updated_game_state = deepcopy(best_state)
    
    print("Deepcopy successful!")

    # Log object at letter 6 after deepcopy
    print("Objects at letter 6 after deepcopy:")
    for pos in letter6_positions:
        print(f"{pos}: {updated_game_state['gameData']['currentBoardStatus'].get(pos)}")

    print(f"Returned state: {updated_game_state}")
    return updated_game_state

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
    for end_piece in endzone_pieces:
        if is_passable_path(ball_holder, end_piece, get_pieces_by_color(board_status, get_ai_color(player_color)), pieces):
            print(f"🔥 AI has a forced win! {ball_holder['position']} can pass to {end_piece['position']}")
            return True  # AI can guarantee a win

    return False 



def minimax(game_state, depth, is_maximizing):
    print(f"{'Maximizing' if is_maximizing else 'Minimizing'} player at depth {depth}")

    # Base case: return evaluation score if depth is 0 or game is over
    if depth == 0 or game_over(game_state):
        return {"score": evaluate_game_state(game_state), "state": game_state}

    if is_maximizing:
        # Maximizing player's turn (AI is always Black for now)
        best_eval = float('-inf')
        best_state = None
        for child_state in get_child_states(game_state, is_maximizing):
            
            # If AI (Black) has a forced win and we are at depth 1, just take it immediately!
            if depth == 1 and has_forced_win(child_state, 'black'):
                print("AI (Black) has a forced win at depth 1! Executing immediately.")
                return {"score": 10000, "state": execute_forced_win(child_state, 'black')}

            result = minimax(child_state, depth - 1, False)  # Switch to minimizing for next turn
            if result["score"] > best_eval:
                best_eval = result["score"]
                best_state = child_state
        
        return {"score": best_eval, "state": best_state}
    
    else:
        # Minimizing player's turn (Human - White)
        best_eval = float('inf')
        best_state = None
        for child_state in get_child_states(game_state, is_maximizing):

            result = minimax(child_state, depth - 1, True)  # Switch to maximizing
            if result["score"] < best_eval:
                best_eval = result["score"]
                best_state = child_state
        
        return {"score": best_eval, "state": best_state}


def get_ball_holder(pieces):
    """
    Returns the piece that currently holds the ball.
    If no piece has the ball, returns None.
    """
    for piece in pieces:
        if piece.get('hasBall', False):  # Check if 'hasBall' exists and is True
            return piece
    return None  # No piece is holding the ball


def evaluate_game_state(game_state):
    board = game_state['gameData']['currentBoardStatus']
    white_pieces = get_pieces_by_color(board, 'white')
    black_pieces = get_pieces_by_color(board, 'black')

    white_ball_holder = get_ball_holder(white_pieces)
    black_ball_holder = get_ball_holder(black_pieces)

    # Base score: Progress toward endzone
    score = reward_progress_toward_endzone(white_pieces, black_pieces)

    # If a forced win exists, prioritize it by giving it a MASSIVE boost
    if has_forced_win(game_state, 'white'):
        score += 5000  # White is very close to winning

    if has_forced_win(game_state, 'black'):
        score -= 5000  # Black is very close to winning

    # Reward having a path to score (but NOT passing just for movement)
    if white_ball_holder:
        score += 10 * reward_path_to_goal(white_pieces, black_pieces, white_ball_holder, 'white')

    if black_ball_holder:
        score -= 10 * reward_path_to_goal(black_pieces, white_pieces, black_ball_holder, 'black')

    # Defensive Positioning (Less weight)
    score += 3 * reward_defensive_positioning(white_pieces, black_pieces)
    score -= 3 * reward_defensive_positioning(black_pieces, white_pieces)

    print(f"[Evaluation] Score: {score}")
    return score


def reward_progress_toward_endzone(white_pieces, black_pieces):
    score = 0

    #Extract ranks for all white and black pieces (ignore 'hasBall')
    white_positions = [extract_rank(piece['position']) for piece in white_pieces]
    black_positions = [extract_rank(piece['position']) for piece in black_pieces]

    print(f"White positions (ranks): {white_positions}")
    print(f"Black positions (ranks): {black_positions}")

    # Most advanced positions for each color
    most_advanced_white = max(white_positions) if white_positions else 1
    most_advanced_black = min(black_positions) if black_positions else 8

    print(f"Most Advanced White: {most_advanced_white}")
    print(f"Most Advanced Black: {most_advanced_black}")

    # Progress toward end zones
    white_progress = most_advanced_white - 1
    black_progress = 8 - most_advanced_black

    print(f"White progress: {white_progress}")
    print(f"Black progress: {black_progress}")

    # Final score
    score += white_progress
    score -= black_progress

    print(f"Final score: {score}")
    return score

def reward_path_to_goal(pieces, opponent_pieces, ball_holder, player_color):
    """
    Rewards the AI if there exists a clear passing path between the piece 
    holding the ball and a teammate in the endzone without an opponent blocking.
    """
    goal_row = 8 if player_color == 'white' else 1  # Define target row
    path_score = 0

    # Find all pieces in the endzone
    endzone_pieces = [p for p in pieces if extract_rank(p['position']) == goal_row]

    if not endzone_pieces:
        return 0  # No pieces in the endzone, no possible goal path

    # Check if a valid pass sequence exists
    for end_piece in endzone_pieces:
        if is_passable_path(ball_holder, end_piece, opponent_pieces, pieces):
            path_score += 10  # Reward having a path to score

    return path_score

def is_passable_path(start_piece, target_piece, opponent_pieces, my_pieces):
    """
    Determines if there is an open passing path from start_piece to target_piece.
    """
    # Get all pieces blocking the straight-line pass
    blocking_pieces = get_pieces_between(start_piece['position'], target_piece['position'], opponent_pieces + my_pieces)

    # If only friendly pieces are in the way, it's a valid pass chain
    for piece in blocking_pieces:
        if piece in opponent_pieces:
            return False  # Opponent blocking the way

    return True  # A passable path exists

def get_pieces_between(pos1, pos2, all_pieces):
    """
    Returns a list of pieces positioned between two given positions.
    """
    pieces_between = []
    row1, col1 = extract_row_col(pos1)
    row2, col2 = extract_row_col(pos2)

    for piece in all_pieces:
        piece_row, piece_col = extract_row_col(piece['position'])

        # Check if the piece is in between the two given positions
        if min(row1, row2) < piece_row < max(row1, row2) and min(col1, col2) < piece_col < max(col1, col2):
            pieces_between.append(piece)

    return pieces_between

def reward_defensive_positioning(my_pieces, opponent_pieces):
    """
    Reward pieces that are well-placed to block opponent movement and passing lanes.
    """
    defense_score = 0

    for opp_piece in opponent_pieces:
        opp_row = extract_rank(opp_piece['position'])
        opp_col = extract_file(opp_piece['position'])

        # Check if any of our pieces are blocking passes
        for my_piece in my_pieces:
            my_row = extract_rank(my_piece['position'])
            my_col = extract_file(my_piece['position'])

            # If my piece is in front of the opponent (same file but closer to the opponent's goal), it's blocking
            if my_col == opp_col and ((my_row > opp_row and my_piece['color'] == 'white') or (my_row < opp_row and my_piece['color'] == 'black')):
                defense_score += 3  # Blocking vertical movement

            # If my piece is diagonally in front, it might be interfering with a pass
            if abs(my_col - opp_col) == 1 and ((my_row > opp_row and my_piece['color'] == 'white') or (my_row < opp_row and my_piece['color'] == 'black')):
                defense_score += 2  # Slightly less important than direct blocking

    return defense_score
