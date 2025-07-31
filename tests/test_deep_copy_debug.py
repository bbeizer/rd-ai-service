"""
Test to demonstrate the deep copy issue clearly.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_logic import get_child_states, update_board
from utils import apply_pass, validate_game_state

def debug_deep_copy_issue():
    """Demonstrate the deep copy issue step by step."""
    
    # Step 1: Create original state
    game_state = {
        "currentBoardStatus": {
            "a1": {"color": "white", "hasBall": False, "position": "a1"},
            "b1": {"color": "white", "hasBall": True, "position": "b1"},  # Ball holder
            "c1": {"color": "white", "hasBall": False, "position": "c1"},
            "d1": {"color": "white", "hasBall": False, "position": "d1"},
        },
        "currentPlayerTurn": "white",
        "hasMoved": False
    }
    
    print("=== STEP 1: Original State ===")
    piece = game_state['currentBoardStatus']['b1']
    print(f"Original piece at b1: hasBall = {piece['hasBall']}")
    
    # Step 2: Pass the ball
    print("\n=== STEP 2: After Pass ===")
    passed_state = apply_pass(game_state, piece, game_state['currentBoardStatus']['c1'])
    print(f"Passed state - b1 hasBall: {passed_state['currentBoardStatus']['b1']['hasBall']}")
    print(f"Passed state - c1 hasBall: {passed_state['currentBoardStatus']['c1']['hasBall']}")
    
    # Step 3: Show the issue
    print("\n=== STEP 3: The Problem ===")
    print(f"Original piece object still has: hasBall = {piece['hasBall']}")
    print(f"But passed_state['b1'] has: hasBall = {passed_state['currentBoardStatus']['b1']['hasBall']}")
    print("These are DIFFERENT objects!")
    
    # Step 4: Demonstrate the bug
    print("\n=== STEP 4: Demonstrating the Bug ===")
    print("If we use the original piece object in update_board...")
    
    # This is what was happening before the fix
    moved_state = update_board(passed_state, piece, "d2")
    
    print(f"Result - b1: {moved_state['currentBoardStatus']['b1']}")
    print(f"Result - c1: {moved_state['currentBoardStatus']['c1']}")
    print(f"Result - d2: {moved_state['currentBoardStatus']['d2']}")
    
    # Check for multiple balls
    ball_holders = []
    for pos, p in moved_state['currentBoardStatus'].items():
        if p and p.get('hasBall', False):
            ball_holders.append(pos)
    
    print(f"Ball holders: {ball_holders}")
    print(f"Multiple balls: {len(ball_holders) > 1}")
    
    # Step 5: Show the fix
    print("\n=== STEP 5: The Fix ===")
    print("Using piece from passed_state instead of original piece...")
    
    piece_from_passed_state = passed_state['currentBoardStatus']['b1']
    print(f"Piece from passed_state has: hasBall = {piece_from_passed_state['hasBall']}")
    
    fixed_state = update_board(passed_state, piece_from_passed_state, "d2")
    
    ball_holders_fixed = []
    for pos, p in fixed_state['currentBoardStatus'].items():
        if p and p.get('hasBall', False):
            ball_holders_fixed.append(pos)
    
    print(f"Fixed result - ball holders: {ball_holders_fixed}")
    print(f"Multiple balls: {len(ball_holders_fixed) > 1}")

if __name__ == "__main__":
    debug_deep_copy_issue() 