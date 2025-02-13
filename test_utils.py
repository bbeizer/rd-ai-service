import unittest
from utils import position_to_coords, coords_to_position

class TestAILogic(unittest.TestCase):

    def test_position_to_coords(self):
        """Test the position_to_coords function."""
        self.assertEqual(position_to_coords("h8"), (7, 0))  # Top-right corner
        self.assertEqual(position_to_coords("a1"), (0, 7))  # Bottom-left corner
        self.assertEqual(position_to_coords("d4"), (3, 4))  # Middle of the board

    def test_coords_to_position(self):
        """Test the coords_to_position function."""
        self.assertEqual(coords_to_position(7, 0), "h8")  # Top-right corner
        self.assertEqual(coords_to_position(0, 7), "a1")  # Bottom-left corner
        self.assertEqual(coords_to_position(3, 4), "d4")  # Middle of the board
        self.assertEqual(coords_to_position(1, 1), "b7")  # Near top-left corner

    def test_position_to_coords_and_back(self):
        """Ensure converting position -> coords -> position works as expected."""
        test_cases = [
            ("a8", (0, 0)),
            ("h8", (7, 0)),
            ("a1", (0, 7)),
            ("h1", (7, 7)),
            ("d4", (3, 4)),
        ]

        for pos, coords in test_cases:
            with self.subTest(pos=pos, coords=coords):
                self.assertEqual(position_to_coords(pos), coords)
                self.assertEqual(coords_to_position(*coords), pos)

if __name__ == "__main__":
    unittest.main()