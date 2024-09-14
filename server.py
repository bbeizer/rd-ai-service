from flask import Flask, request, jsonify
from ai_logic import ai_service

app = Flask(__name__)

@app.route('/ai/move', methods=['POST'])
def get_ai_move():
    game_state_json = request.get_json()
    
    ai_move = ai_service(game_state_json)
    
    return jsonify({"move": ai_move})

# Run the app on localhost:5000
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
