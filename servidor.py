# servidor.py
from flask import Flask, render_template, request
from flask_socketio import SocketIO, emit
from generador import generate_board
import threading

app = Flask(__name__)
app.config['SECRET_KEY'] = 'sopa_secreta'
# Use threading async mode so we rely on Python threads (matches requirement)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Almacenamos tableros por session id (sid)
games = {}
games_lock = threading.Lock()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/resolver/<sid>')
def resolver_page(sid):
    # sencilla página que consulta la solución via socket desde el cliente
    return render_template('resolver.html', sid=sid)

@socketio.on('start_game')
def handle_start_game(data):
    """
    data expected:
    {
      'words': ['PALABRA1', 'PALABRA2', ...],
      'size': 12
    }
    """
    sid = request.sid
    words = data.get('words', [])
    size = int(data.get('size', 12))
    # sanitize words: uppercase and remove empty
    words = [w.strip().upper() for w in words if w.strip()]
    if not words:
        emit('error', {'msg': 'No words provided'})
        return

    # generate a board (generator uses threads internally)
    grid, positions = generate_board(words, size)

    with games_lock:
        games[sid] = {
            'grid': grid,
            'positions': positions,   # dict: word -> list of [(r,c),...]
            'found': set()
        }

    # send board and word list to client
    emit('board', {'grid': grid, 'words': words})

@socketio.on('submit_word')
def handle_submit_word(data):
    """
    data expected:
    {
      'word': 'PALABRA',
      'coords': [(r1,c1),(r2,c2),...]  # list of tuples
    }
    """
    sid = request.sid
    word = data.get('word','').strip().upper()
    coords = data.get('coords', [])
    if not word or not coords:
        emit('word_result', {'ok': False, 'msg': 'Invalid submission'})
        return

    with games_lock:
        game = games.get(sid)
    if not game:
        emit('word_result', {'ok': False, 'msg': 'Game not found'})
        return

    positions = game['positions']
    expected = positions.get(word)
    # Accept either order (forward or reversed) to be more user-friendly
    if expected and (expected == coords or list(reversed(expected)) == coords):
        game['found'].add(word)
        emit('word_result', {'ok': True, 'word': word})
    else:
        emit('word_result', {'ok': False, 'word': word, 'msg': 'Incorrect'})

@socketio.on('request_solve')
def handle_request_solve():
    sid = request.sid
    with games_lock:
        game = games.get(sid)
    if not game:
        emit('solve_result', {'ok': False, 'msg': 'Game not found'})
        return
    # return all positions
    emit('solve_result', {'ok': True, 'positions': game['positions']})


@socketio.on('request_solve_for')
def handle_request_solve_for(data):
    """Allow fetching the solution for another session by sid.
    This is used by the `/resolver/<sid>` page to request the solution
    for a specific game session.
    data: {'sid': '<target_sid>'}
    """
    target_sid = data.get('sid')
    if not target_sid:
        emit('solve_result', {'ok': False, 'msg': 'No sid provided'})
        return
    with games_lock:
        game = games.get(target_sid)
    if not game:
        emit('solve_result', {'ok': False, 'msg': 'Game not found'})
        return
    emit('solve_result', {'ok': True, 'positions': game['positions']})


@socketio.on('disconnect')
def handle_disconnect():
    sid = request.sid
    with games_lock:
        if sid in games:
            del games[sid]
    print(f"Client disconnected: {sid}")

if __name__ == '__main__':
    PORT = 5000
    print(f"\n Servidor iniciado en http://localhost:{PORT}")
    print(f" Escuchando en el puerto {PORT}...\n")
    
    socketio.run(app, host='0.0.0.0', port=PORT)
