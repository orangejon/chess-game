from flask import Flask, render_template, jsonify, request
from chess_engine import ChessEngine

app = Flask(__name__)
chess_engine = ChessEngine()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get_valid_moves', methods=['POST'])
def get_valid_moves():
    data = request.get_json()
    position = data.get('position')
    valid_moves = chess_engine.get_valid_moves(position)
    return jsonify({'valid_moves': valid_moves})

@app.route('/make_move', methods=['POST'])
def make_move():
    data = request.get_json()
    from_pos = data.get('from')
    to_pos = data.get('to')
    
    move_result = chess_engine.make_move(from_pos, to_pos)
    if move_result['valid']:
        # If player's move is valid, make AI move
        ai_move = chess_engine.get_ai_move()
        if ai_move:
            chess_engine.make_move(ai_move['from'], ai_move['to'])
            move_result['ai_move'] = ai_move
    
    return jsonify(move_result)

@app.route('/reset_game', methods=['POST'])
def reset_game():
    chess_engine.reset_game()
    return jsonify({'status': 'success'})

if __name__ == '__main__':
    app.run(port=7861, host='0.0.0.0', debug=True)