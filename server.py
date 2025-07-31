"""
Flask Server for AI Game Service

This server provides an API endpoint for the AI to compute moves
in the game using the minimax algorithm.
"""

from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import logging
import json
from ai_logic import ai_service
from utils import validate_game_state, ensure_single_ball

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/ai/move', methods=['POST', 'OPTIONS'])
def get_ai_move():
    """
    Handle AI move requests.
    
    Expected JSON payload:
    {
        "game": {...},  # Current game state
        "color": "white" | "black"  # AI color
    }
    
    Returns:
        JSON: Updated game state after AI move
    """
    if request.method == 'OPTIONS':
        # Handle preflight CORS request
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    try:
        # Validate request data
        data = request.get_json()
        if not data or 'game' not in data or 'color' not in data:
            logging.error("Missing 'game' or 'color' in request")
            return jsonify({'error': 'Missing game or color'}), 400
        
        game_state = data["game"]
        ai_color = data["color"]
        
        # Validate AI color
        if ai_color not in ['white', 'black']:
            logging.error(f"Invalid AI color: {ai_color}")
            return jsonify({'error': 'Invalid color. Must be "white" or "black"'}), 400
        
        # Validate game state before processing
        is_valid, error_msg = validate_game_state(game_state)
        if not is_valid:
            logging.error(f"Invalid game state received: {error_msg}")
            # Try to fix the state
            game_state = ensure_single_ball(game_state)
            logging.info("Attempted to fix game state before AI processing")
        
        game_state["aiColor"] = ai_color

        logging.info("Received game state for AI move")
        logging.debug("Game state: %s", json.dumps(game_state, indent=2))

        # Compute AI move
        updated_game_state = ai_service(game_state, ai_color)

        # Validate response
        if "currentBoardStatus" not in updated_game_state:
            logging.error("AI service returned incomplete game state")
            return jsonify({'error': 'Incomplete game state returned'}), 500

        logging.info("AI move computed successfully")
        logging.debug("Updated game state: %s", json.dumps(updated_game_state, indent=2))
        
        return jsonify(updated_game_state)

    except Exception as e:
        logging.error("Exception during AI move computation: %s", e, exc_info=True)
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'service': 'ai-game-service'})

if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    
    # Start the server
    app.run(debug=True, host='0.0.0.0', port=5002)
