"""
Test to reproduce the multiple balls issue and identify the root cause.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_logic import get_child_states, update_board
from utils import apply_pass, validate_game_state, get_pieces_by_color, get_ball_holder

class TestMultipleBallsReproduction(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.game_state = {
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
    
    def test_apply_pass_doesnt_create_multiple_balls(self):
        """Test that apply_pass doesn't create multiple balls."""
        from_piece = self.game_state["currentBoardStatus"]["b1"]
        to_piece = self.game_state["currentBoardStatus"]["c1"]
        
        result = apply_pass(self.game_state, from_piece, to_piece)
        
        # Validate the result
        is_valid, error_msg = validate_game_state(result)
        self.assertTrue(is_valid, f"apply_pass created invalid state: {error_msg}")
        
        # Check ball positions
        ball_holders = []
        for pos, piece in result["currentBoardStatus"].items():
            if piece and piece.get('hasBall', False):
                ball_holders.append(pos)
        
        self.assertEqual(len(ball_holders), 1, f"Should have exactly 1 ball, found {len(ball_holders)}")
        self.assertEqual(ball_holders[0], "c1", "Ball should be at c1 after pass")
        self.assertFalse(result["currentBoardStatus"]["b1"]["hasBall"], "Original piece should not have ball")
    
    def test_update_board_doesnt_create_multiple_balls(self):
        """Test that update_board doesn't create multiple balls."""
        piece = self.game_state["currentBoardStatus"]["b1"]  # Ball holder
        new_position = "c2"
        
        result = update_board(self.game_state, piece, new_position)
        
        # Validate the result
        is_valid, error_msg = validate_game_state(result)
        self.assertTrue(is_valid, f"update_board created invalid state: {error_msg}")
        
        # Check ball positions
        ball_holders = []
        for pos, piece in result["currentBoardStatus"].items():
            if piece and piece.get('hasBall', False):
                ball_holders.append(pos)
        
        self.assertEqual(len(ball_holders), 1, f"Should have exactly 1 ball, found {len(ball_holders)}")
        self.assertEqual(ball_holders[0], "c2", "Ball should be at c2 after move")
        self.assertIsNone(result["currentBoardStatus"]["b1"], "Original position should be empty")
    
    def test_get_child_states_doesnt_create_multiple_balls(self):
        """Test that get_child_states doesn't create multiple balls."""
        child_states = get_child_states(self.game_state, True)  # White's turn
        
        for i, child_state in enumerate(child_states):
            is_valid, error_msg = validate_game_state(child_state)
            if not is_valid:
                print(f"Child state {i} is invalid: {error_msg}")
                print(f"Child state: {child_state}")
                self.fail(f"Child state {i} created invalid state: {error_msg}")
            
            # Check ball count
            ball_holders = []
            for pos, piece in child_state["currentBoardStatus"].items():
                if piece and piece.get('hasBall', False):
                    ball_holders.append(pos)
            
            self.assertEqual(len(ball_holders), 1, 
                           f"Child state {i} should have exactly 1 ball, found {len(ball_holders)} at {ball_holders}")
    
    def test_deep_copy_issue_reproduction(self):
        """Test to reproduce potential deep copy issues."""
        # This test simulates what might happen in the AI
        original_state = self.game_state.copy()
        
        # Simulate multiple operations on the same state
        piece1 = original_state["currentBoardStatus"]["b1"]
        piece2 = original_state["currentBoardStatus"]["c1"]
        
        # Apply pass
        state_after_pass = apply_pass(original_state, piece1, piece2)
        
        # Try to move the original piece (this might be the issue!)
        try:
            # This should fail because piece1 is from the original state
            # but we're trying to move it in state_after_pass
            result = update_board(state_after_pass, piece1, "d2")
            
            # If we get here, check if it created multiple balls
            is_valid, error_msg = validate_game_state(result)
            if not is_valid:
                print(f"Found issue! {error_msg}")
                print(f"Result state: {result}")
                self.fail(f"Deep copy issue reproduced: {error_msg}")
                
        except Exception as e:
            print(f"Expected error when moving piece from original state: {e}")
            # This is actually expected behavior

if __name__ == '__main__':
    unittest.main() 