"""
Tests for ball validation and game state integrity.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils import validate_game_state, ensure_single_ball, get_ball_holder, get_pieces_by_color
from ai_logic import ai_service

class TestBallValidation(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_game_state = {
            "currentBoardStatus": {
                "a1": {"color": "white", "hasBall": False, "position": "a1"},
                "b1": {"color": "white", "hasBall": True, "position": "b1"},  # Only ball
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
    
    def test_valid_game_state(self):
        """Test that a valid game state passes validation."""
        is_valid, message = validate_game_state(self.valid_game_state)
        self.assertTrue(is_valid, f"Valid state failed validation: {message}")
    
    def test_multiple_balls_detection(self):
        """Test that multiple balls are detected and reported."""
        # Create state with multiple balls
        bad_state = self.valid_game_state.copy()
        bad_state["currentBoardStatus"]["b1"]["hasBall"] = True
        bad_state["currentBoardStatus"]["c1"]["hasBall"] = True  # Second ball!
        
        is_valid, message = validate_game_state(bad_state)
        self.assertFalse(is_valid, "Multiple balls should be detected")
        self.assertIn("Multiple balls detected", message)
        self.assertIn("2", message)  # Should mention count
    
    def test_no_ball_detection(self):
        """Test that no ball is detected and reported."""
        # Create state with no ball
        no_ball_state = self.valid_game_state.copy()
        no_ball_state["currentBoardStatus"]["b1"]["hasBall"] = False
        
        is_valid, message = validate_game_state(no_ball_state)
        self.assertFalse(is_valid, "No ball should be detected")
        self.assertIn("No ball found", message)
    
    def test_ensure_single_ball_fixes_multiple(self):
        """Test that ensure_single_ball fixes multiple ball issues."""
        # Create state with multiple balls
        bad_state = self.valid_game_state.copy()
        bad_state["currentBoardStatus"]["b1"]["hasBall"] = True
        bad_state["currentBoardStatus"]["c1"]["hasBall"] = True
        bad_state["currentBoardStatus"]["d1"]["hasBall"] = True  # Third ball!
        
        # Fix the state
        fixed_state = ensure_single_ball(bad_state)
        
        # Check that only one ball remains
        ball_holders = []
        for pos, piece in fixed_state["currentBoardStatus"].items():
            if piece and piece.get('hasBall', False):
                ball_holders.append(pos)
        
        self.assertEqual(len(ball_holders), 1, f"Should have exactly 1 ball, found {len(ball_holders)}")
        self.assertEqual(ball_holders[0], "b1", "Should keep the first ball found")
    
    def test_ai_service_handles_invalid_state(self):
        """Test that AI service handles invalid game states gracefully."""
        # Create state with multiple balls
        bad_state = self.valid_game_state.copy()
        bad_state["currentBoardStatus"]["b1"]["hasBall"] = True
        bad_state["currentBoardStatus"]["c1"]["hasBall"] = True
        
        # AI service should not crash and should fix the state
        try:
            result = ai_service(bad_state, "white")
            self.assertIsNotNone(result, "AI service should return a result")
            
            # Check that the result has only one ball
            ball_holders = []
            for pos, piece in result["currentBoardStatus"].items():
                if piece and piece.get('hasBall', False):
                    ball_holders.append(pos)
            
            self.assertEqual(len(ball_holders), 1, f"AI result should have exactly 1 ball, found {len(ball_holders)}")
            
        except Exception as e:
            self.fail(f"AI service crashed with invalid state: {e}")
    
    def test_invalid_piece_data(self):
        """Test validation of piece data integrity."""
        # Test missing color
        bad_state = self.valid_game_state.copy()
        bad_state["currentBoardStatus"]["b1"].pop("color")
        
        is_valid, message = validate_game_state(bad_state)
        self.assertFalse(is_valid, "Missing color should be detected")
        self.assertIn("missing color", message)
        
        # Test invalid color
        bad_state = self.valid_game_state.copy()
        bad_state["currentBoardStatus"]["b1"]["color"] = "purple"
        
        is_valid, message = validate_game_state(bad_state)
        self.assertFalse(is_valid, "Invalid color should be detected")
        self.assertIn("Invalid color", message)
    
    def test_ball_holder_consistency(self):
        """Test that get_ball_holder and validation are consistent."""
        # Valid state
        white_pieces = get_pieces_by_color(self.valid_game_state["currentBoardStatus"], "white")
        ball_holder = get_ball_holder(white_pieces)
        
        self.assertIsNotNone(ball_holder, "Should find ball holder in valid state")
        self.assertEqual(ball_holder["position"], "b1", "Ball should be at b1")
        
        # Invalid state with multiple balls
        bad_state = self.valid_game_state.copy()
        bad_state["currentBoardStatus"]["b1"]["hasBall"] = True
        bad_state["currentBoardStatus"]["c1"]["hasBall"] = True
        
        white_pieces = get_pieces_by_color(bad_state["currentBoardStatus"], "white")
        ball_holder = get_ball_holder(white_pieces)
        
        # get_ball_holder should return the first one it finds
        self.assertIsNotNone(ball_holder, "Should still find a ball holder")
        self.assertTrue(ball_holder["hasBall"], "Found ball holder should have ball")

if __name__ == '__main__':
    unittest.main() 