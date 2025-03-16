from flask import Flask, request, jsonify
from flask_cors import CORS
from ai_logic import ai_service
import logging
import json
from copy import deepcopy
from collections import OrderedDict
import copy

app = Flask(__name__)
CORS(app, resources={r"/ai/move": {"origins": "*"}})  # Enable CORS globally

@app.route('/ai/move', methods=['POST'])
def get_ai_move():
    try:
        # Parse the incoming game state
        game_state = request.get_json()
        if not game_state:
            logging.error("Invalid or no game state provided.")
            return jsonify({'error': 'Invalid or no game state provided'}), 400

        logging.info("Received game state:\n%s", json.dumps(game_state, indent=2))

        # Process the game state with the AI logic
        updated_game_state = ai_service(game_state)

        # Validate the updated response
        if "currentBoardStatus" not in updated_game_state:
            logging.error("AI service returned incomplete data.")
            return jsonify({'error': 'Incomplete data from AI service'}), 500

        # ✅ Return the full updated game state
        logging.info("Returning updated game state:\n%s", json.dumps(updated_game_state, indent=2))
        return jsonify(updated_game_state)

    except Exception as e:
        logging.error(f"Error in AI move processing: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500
        
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    app.run(debug=True, host='0.0.0.0', port=5001)
