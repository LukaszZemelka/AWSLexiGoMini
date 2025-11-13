from flask import Flask, jsonify, send_from_directory, redirect, url_for, session, request
import psycopg2
import psycopg2.extras
import os
from authlib.integrations.flask_client import OAuth
from functools import wraps
import logging
import random

# Setup logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__, static_folder='public', static_url_path='')
app.secret_key = os.environ.get('SECRET_KEY', 'lexigo-secret-key-change-in-production')

# Session configuration
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = True

# OAuth configuration
oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id=os.environ.get('GOOGLE_CLIENT_ID', 'YOUR_GOOGLE_CLIENT_ID'),
    client_secret=os.environ.get('GOOGLE_CLIENT_SECRET', 'YOUR_GOOGLE_CLIENT_SECRET'),
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile'
    }
)

# Database connection configuration
DB_CONFIG = {
    'dbname': 'lexigo',
    'user': 'myuser',
    'password': 'lexigo2024',
    'host': 'localhost'
}

def get_db_connection():
    conn = psycopg2.connect(**DB_CONFIG)
    return conn

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        logger.debug(f"Checking login for {request.path}, user in session: {'user' in session}")
        if 'user' not in session:
            logger.debug("No user in session, redirecting to login")
            return redirect(url_for('login'))
        logger.debug(f"User found: {session['user']['email']}")
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login')
def login():
    logger.debug("Login page accessed")
    session.clear()
    return send_from_directory('public', 'login.html')

@app.route('/login/google')
def google_login():
    redirect_uri = url_for('google_callback', _external=True)
    logger.debug(f"Starting OAuth flow with redirect_uri: {redirect_uri}")
    return google.authorize_redirect(redirect_uri)

@app.route('/login/callback')
def google_callback():
    logger.debug("OAuth callback received")
    try:
        logger.debug("Attempting to authorize access token")
        token = google.authorize_access_token()
        logger.debug(f"Token received successfully: {bool(token)}")

        user_info = token.get('userinfo')
        if user_info:
            logger.debug(f"User info retrieved: {user_info.get('email')}")
            session['user'] = {
                'email': user_info.get('email'),
                'name': user_info.get('name'),
                'picture': user_info.get('picture')
            }
            session.permanent = True
            logger.debug("Session set, redirecting to index")
            return redirect(url_for('index'))
        else:
            logger.error("No user info in token")
    except Exception as e:
        logger.error(f'OAuth error: {str(e)}', exc_info=True)

    logger.debug("OAuth failed, redirecting to login")
    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    logger.debug("Logout called")
    session.clear()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    logger.debug("Index page accessed")
    return send_from_directory('public', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('public', path)

@app.route('/api/user')
@login_required
def get_user():
    return jsonify(session.get('user'))

@app.route('/api/words', methods=['GET'])
@login_required
def get_words():
    try:
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute('SELECT * FROM words ORDER BY id')
        words = cur.fetchall()
        cur.close()
        conn.close()
        return jsonify(words)
    except Exception as e:
        logger.error(f'Database error: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/notes/<int:word_id>', methods=['GET'])
@login_required
def get_note(word_id):
    try:
        user_email = session['user']['email']
        conn = get_db_connection()
        cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cur.execute(
            'SELECT notes FROM user_notes WHERE user_email = %s AND word_id = %s',
            (user_email, word_id)
        )
        result = cur.fetchone()
        cur.close()
        conn.close()

        if result:
            return jsonify({'notes': result['notes']})
        else:
            return jsonify({'notes': ''})
    except Exception as e:
        logger.error(f'Error fetching note: {str(e)}')
        return jsonify({'error': str(e)}), 500

@app.route('/api/notes/<int:word_id>', methods=['POST'])
@login_required
def save_note(word_id):
    try:
        user_email = session['user']['email']
        data = request.get_json()
        notes = data.get('notes', '').strip()

        conn = get_db_connection()
        cur = conn.cursor()

        if notes:
            # Insert or update note
            cur.execute('''
                INSERT INTO user_notes (user_email, word_id, notes, updated_at)
                VALUES (%s, %s, %s, CURRENT_TIMESTAMP)
                ON CONFLICT (user_email, word_id)
                DO UPDATE SET notes = EXCLUDED.notes, updated_at = CURRENT_TIMESTAMP
            ''', (user_email, word_id, notes))
        else:
            # Delete note if empty
            cur.execute(
                'DELETE FROM user_notes WHERE user_email = %s AND word_id = %s',
                (user_email, word_id)
            )

        conn.commit()
        cur.close()
        conn.close()

        return jsonify({'success': True, 'message': 'Note saved successfully'})
    except Exception as e:
        logger.error(f'Error saving note: {str(e)}')
        return jsonify({'error': str(e)}), 500

# Famous quotes collection
FAMOUS_QUOTES = [
    {"text": "The only way to do great work is to love what you do.", "author": "Steve Jobs"},
    {"text": "Success is not final, failure is not fatal: it is the courage to continue that counts.", "author": "Winston Churchill"},
    {"text": "Believe you can and you're halfway there.", "author": "Theodore Roosevelt"},
    {"text": "The future belongs to those who believe in the beauty of their dreams.", "author": "Eleanor Roosevelt"},
    {"text": "It does not matter how slowly you go as long as you do not stop.", "author": "Confucius"},
    {"text": "Education is the most powerful weapon which you can use to change the world.", "author": "Nelson Mandela"},
    {"text": "The only impossible journey is the one you never begin.", "author": "Tony Robbins"},
    {"text": "In the middle of difficulty lies opportunity.", "author": "Albert Einstein"},
    {"text": "The best time to plant a tree was 20 years ago. The second best time is now.", "author": "Chinese Proverb"},
    {"text": "You miss 100% of the shots you don't take.", "author": "Wayne Gretzky"},
    {"text": "Whether you think you can or you think you can't, you're right.", "author": "Henry Ford"},
    {"text": "The only person you are destined to become is the person you decide to be.", "author": "Ralph Waldo Emerson"},
    {"text": "Don't watch the clock; do what it does. Keep going.", "author": "Sam Levenson"},
    {"text": "Everything you've ever wanted is on the other side of fear.", "author": "George Addair"},
    {"text": "Success is not how high you have climbed, but how you make a positive difference to the world.", "author": "Roy T. Bennett"},
    {"text": "Learning never exhausts the mind.", "author": "Leonardo da Vinci"},
    {"text": "The expert in anything was once a beginner.", "author": "Helen Hayes"},
    {"text": "Don't let yesterday take up too much of today.", "author": "Will Rogers"},
    {"text": "Life is 10% what happens to you and 90% how you react to it.", "author": "Charles R. Swindoll"},
    {"text": "The way to get started is to quit talking and begin doing.", "author": "Walt Disney"}
]

@app.route('/api/quote', methods=['GET'])
@login_required
def get_quote():
    try:
        quote = random.choice(FAMOUS_QUOTES)
        return jsonify(quote)
    except Exception as e:
        logger.error(f'Error fetching quote: {str(e)}')
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
