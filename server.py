from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
import logging
import json
from ai_logic import ai_service

app = Flask(__name__)
CORS(app, supports_credentials=True)

@app.route('/ai/move', methods=['POST', 'OPTIONS'])
def get_ai_move():
    if request.method == 'OPTIONS':
        # Respond to preflight CORS request
        response = make_response()
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Methods'] = 'POST, OPTIONS'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
        return response

    try:
        game_state = request.get_json()
        if not game_state:
            logging.error("No game state received in request.")
            return jsonify({'error': 'Invalid or missing game state'}), 400

        logging.info("📥 Received game state:\n%s", json.dumps(game_state, indent=2))

        updated_game_state = ai_service(game_state)

        if "currentBoardStatus" not in updated_game_state:
            logging.error("AI service returned incomplete game state.")
            return jsonify({'error': 'Incomplete game state returned'}), 500

        logging.info("📤 Returning updated game state:\n%s", json.dumps(updated_game_state, indent=2))
        return jsonify(updated_game_state)

    except Exception as e:
        logging.error(f"💥 Exception during AI move: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    app.run(debug=True, host='0.0.0.0', port=5002)
