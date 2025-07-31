"""
Test to debug why the ball might be getting lost.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_logic import get_child_states, update_board
from utils import apply_pass, validate_game_state, ensure_correct_ball_count, get_ball_holder, get_pieces_by_color

def debug_ball_lost():
    """Debug why the ball might be getting lost."""
    
    # Create a simple game state
    game_state = {
        "currentBoardStatus": {
            "a1": {"color": "white", "hasBall": False, "position": "a1"},
            "b1": {"color": "white", "hasBall": True, "position": "b1"},  # Ball holder
            "c1": {"color": "white", "hasBall": False, "position": "c1"},
            "d1": {"color": "white", "hasBall": False, "position": "d1"},
            "a8": {"color": "black", "hasBall": False, "position": "a8"},
            "b8": {"color": "black", "hasBall": False, "position": "b8"},
            "c8": {"color": "black", "hasBall": False, "position": "c8"},
            "d8": {"color": "black", "hasBall": False, "position": "d8"},
        },
        "currentPlayerTurn": "white",
        "hasMoved": False
    }
    
    print("=== Initial State ===")
    white_pieces = get_pieces_by_color(game_state["currentBoardStatus"], "white")
    ball_holder = get_ball_holder(white_pieces)
    print(f"Ball holder: {ball_holder['position'] if ball_holder else 'None'}")
    
    # Test validation
    is_valid, msg = validate_game_state(game_state)
    print(f"Valid: {is_valid}, Message: {msg}")
    
    # Test ensure_correct_ball_count on valid state
print("\n=== Testing ensure_correct_ball_count on valid state ===")
fixed_state = ensure_correct_ball_count(game_state)
    white_pieces = get_pieces_by_color(fixed_state["currentBoardStatus"], "white")
    ball_holder = get_ball_holder(white_pieces)
    print(f"After fix - Ball holder: {ball_holder['position'] if ball_holder else 'None'}")
    
    # Test get_child_states
    print("\n=== Testing get_child_states ===")
    child_states = get_child_states(game_state, True)  # White's turn
    print(f"Generated {len(child_states)} child states")
    
    for i, child_state in enumerate(child_states[:3]):  # Check first 3
        white_pieces = get_pieces_by_color(child_state["currentBoardStatus"], "white")
        ball_holder = get_ball_holder(white_pieces)
        print(f"Child {i} - Ball holder: {ball_holder['position'] if ball_holder else 'None'}")
        
        # Check if valid
        is_valid, msg = validate_game_state(child_state)
        if not is_valid:
            print(f"  Child {i} is invalid: {msg}")
    
    # Test a specific pass and move
    print("\n=== Testing specific pass and move ===")
    from_piece = game_state["currentBoardStatus"]["b1"]
    to_piece = game_state["currentBoardStatus"]["c1"]
    
    passed_state = apply_pass(game_state, from_piece, to_piece)
    print(f"After pass - Ball at: {get_ball_holder(get_pieces_by_color(passed_state['currentBoardStatus'], 'white'))['position']}")
    
    # Try to move the piece that no longer has the ball
    piece_without_ball = passed_state["currentBoardStatus"]["b1"]
    moved_state = update_board(passed_state, piece_without_ball, "d2")
    
    white_pieces = get_pieces_by_color(moved_state["currentBoardStatus"], "white")
    ball_holder = get_ball_holder(white_pieces)
    print(f"After move - Ball holder: {ball_holder['position'] if ball_holder else 'None'}")

if __name__ == "__main__":
    debug_ball_lost() 