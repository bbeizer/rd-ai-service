# ai_logic.py
from copy import deepcopy
from game_logic import game_over, get_child_states, get_pieces_by_color, check_and_return_win, is_passable_path
from utils import get_ai_color, extract_file, extract_rank, get_ball_holder, extract_row_col, generate_piece_moves

def ai_service(game_state):
    """
    Perform the AI move by calling minimax and returning the updated game state.
    """
    depth = 1  # You can adjust the depth
    print("STARTING MINIMAX")
    result = minimax(game_state, depth, is_maximizing=False)
    best_state = result["state"]  # Extract the best state

    # Force current player turn to 'white'
    best_state['currentPlayerTurn'] = 'white'
    # Log object at letter6 before deepcopy
    letter6_positions = ['e6', 'd6', 'f6', 'c6']  # Add relevant positions
    print("Objects at letter6 before deepcopy:")
    for pos in letter6_positions:
        print(f"{pos}: {best_state['currentBoardStatus'].get(pos)}")
    
    print(f"Best state chosen with score: {result['score']}")
    print("About to Deepcopy the best state...")

    # Deepcopy the state
    updated_game_state = deepcopy(best_state)
    
    print("Deepcopy successful!")

    # Log object at letter 6 after deepcopy
    print("Objects at letter 6 after deepcopy:")
    for pos in letter6_positions:
        print(f"{pos}: {updated_game_state['currentBoardStatus'].get(pos)}")

    print(f"Returned state: {updated_game_state}")
    return updated_game_state

def minimax(game_state, depth, is_maximizing):
    print(f"{'Maximizing' if is_maximizing else 'Minimizing'} player at depth {depth}")

    # **Step 1: Check if AI (Black) has a forced win**
    if depth == 1:
        check_and_return_win(game_state, 'black')  # Returns (from_pos, to_pos) or None

    # **Step 2: Base case: return evaluation score if depth is 0 or game is over**
    if depth == 0 or game_over(game_state):
        return {"score": evaluate_game_state(game_state), "state": game_state}

    if is_maximizing:
        # **Maximizing (AI - Black)**
        best_eval = float('-inf')
        best_state = None
        for child_state in get_child_states(game_state, is_maximizing):
            result = minimax(child_state, depth - 1, False)  # Switch to minimizing
            if result["score"] > best_eval:
                best_eval = result["score"]
                best_state = child_state
        
        return {"score": best_eval, "state": best_state}
    
    else:
        # **Minimizing (Human - White)**
        best_eval = float('inf')
        best_state = None
        for child_state in get_child_states(game_state, is_maximizing):
            result = minimax(child_state, depth - 1, True)  # Switch to maximizing
            if result["score"] < best_eval:
                best_eval = result["score"]
                best_state = child_state
        
        return {"score": best_eval, "state": best_state}


def execute_forced_win(game_state, player_color, winning_move):
    """
    Executes the forced win by passing the ball to the winning piece in the endzone.
    Returns the updated game state with the winner declared.
    """
    print(f"🔥 {player_color.upper()} EXECUTING FORCED WIN!")

    updated_state = deepcopy(game_state)  # Ensure we don't mutate the original state
    board_status = updated_state['currentBoardStatus']
    print("Printing Winning Move:")
    print(winning_move)
    from_pos, to_pos = winning_move

    # Ensure valid positions
    if from_pos not in board_status or to_pos not in board_status:
        print(f"❌ ERROR: Invalid move from {from_pos} to {to_pos}")
        return game_state  # Something went wrong, return the original state

    # **Step 1: Remove the ball from the previous holder**
    board_status[from_pos]['hasBall'] = False

    # **Step 2: Give the ball to the scoring piece**
    board_status[to_pos]['hasBall'] = True

    # **Step 3: Declare the winner**
    updated_state['winner'] = player_color
    updated_state['status'] = 'won'

    print(f"🏆 Ball passed from {from_pos} to {to_pos} — {player_color.upper()} WINS!")
    return updated_state




def evaluate_game_state(game_state):
    board = game_state['currentBoardStatus']
    white_pieces = get_pieces_by_color(board, 'white')
    black_pieces = get_pieces_by_color(board, 'black')

    white_ball_holder = get_ball_holder(white_pieces)
    black_ball_holder = get_ball_holder(black_pieces)

    # Base score: Progress toward endzone
    score = reward_progress_toward_endzone(white_pieces, black_pieces)

    # If a forced win exists, prioritize it by giving it a MASSIVE boost
    if check_and_return_win(game_state, 'white'):
        score += 5000  # White is very close to winning

    if check_and_return_win(game_state, 'black'):
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
