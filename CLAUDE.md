# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python Flask service that provides an AI opponent for a board game. The AI uses a minimax algorithm with alpha-beta pruning to compute optimal moves. The service receives game state JSON from a frontend (RD Frontend), processes it, and returns the updated game state after the AI's move.

## Commands

### Running the Server
```bash
python server.py                    # Development server on port 5002
gunicorn server:app                 # Production server
```

### Running Tests
```bash
python -m pytest                    # Run all tests
python -m pytest tests/             # Run tests in tests/ directory
python -m pytest tests/test_ball_validation.py  # Run specific test file
python -m unittest test_utils       # Run root-level tests
```

### Dependencies
```bash
pip install -r requirements.txt
```

## Architecture

### Core Modules

- **server.py** - Flask server with `/ai/move` (POST) and `/health` (GET) endpoints. Validates incoming game state, calls AI service, and validates response.

- **ai_logic.py** - Minimax algorithm implementation with alpha-beta pruning. Uses a transposition table for caching evaluated positions. The `evaluate_game_state()` function scores positions based on progress toward endzone, path availability to goal, and defensive positioning. White is maximizing player (positive scores), black is minimizing (negative scores).

- **game_logic.py** - Game rules implementation. Key functions:
  - `get_child_states()` - Generates all possible next states for a player
  - `is_passable_path()` - BFS-based check for valid passing chains through teammates
  - `game_over()` / `check_for_win()` - Win condition detection

- **utils.py** - Position conversion, move generation, and validation utilities. Pieces move like knights. Ball holders cannot move (must pass first).

### Game Rules

- 8x8 board with chess-style notation (a1-h8)
- Each team has 4 pieces and one ball
- Pieces move like knights (L-shaped moves)
- Ball holder cannot move - must pass to a teammate first
- Passes travel in straight lines (orthogonal/diagonal) and can relay through teammates
- Win condition: get ball to opponent's back rank (white to rank 8, black to rank 1)

### Data Structures

Game state structure:
```python
{
    "currentBoardStatus": {
        "a1": {"color": "white", "hasBall": True, "position": "a1"},
        "b1": None,  # empty square
        ...
    },
    "currentPlayerTurn": "white" | "black",
    "hasMoved": bool,
    "aiColor": "white" | "black"
}
```

## Known Issues (from README)

- AI rule compliance needs verification
- Evaluation function could be improved
- `is_passable_path()` needs `should_pass` flag integration
