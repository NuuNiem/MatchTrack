import sys
import os
import sqlite3
import secrets
from flask import Flask, session, g
from werkzeug.security import generate_password_hash
import config
from routes import init_routes

app = Flask(__name__)
app.config['SECRET_KEY'] = getattr(
    config, 'SECRET_KEY', os.environ.get('SECRET_KEY', 'dev-secret-key'))
app.config['DATABASE'] = getattr(
    config, 'DATABASE', os.environ.get('DATABASE', 'database.db'))


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):  # pylint: disable=unused-argument
    db = g.pop('db', None)
    if db is not None:
        db.close()


@app.before_request
def csrf_protect():
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_hex(16)


# Alusta reitit
init_routes(app, get_db)


def init_db():
    with app.app_context():
        db = get_db()
        with open('schema.sql', encoding='utf-8') as f:
            db.executescript(f.read())
        db.commit()
    print('Database initialized (created tables)')


def seed_db():
    with app.app_context():
        db = get_db()

        username = 'test'
        user = db.execute(
            'SELECT id FROM user WHERE username = ?',
            (username,)).fetchone()

        if not user:
            db.execute(
                'INSERT INTO user (username, password_hash) VALUES (?, ?)',
                (username, generate_password_hash('test')))
            db.commit()
            user = db.execute(
                'SELECT id FROM user WHERE username = ?',
                (username,)).fetchone()
            print(f"Created sample user: {username} / test")
        else:
            print(f"Sample user '{username}' already exists")

        user_id = user['id']

        cat_count = db.execute(
            'SELECT COUNT(*) as count FROM category').fetchone()['count']
        if cat_count == 0:
            sample_categories = ['Liiga', 'Cupin ottelu', 'Harjoituspeli', 'Ystävyysottelu']
            for cat_name in sample_categories:
                db.execute('INSERT INTO category (name) VALUES (?)', (cat_name,))
            db.commit()
            print(f'Added {len(sample_categories)} sample categories')
        else:
            print('Categories already present; skipping sample data')

        match_count = db.execute(
            'SELECT COUNT(*) as count FROM match').fetchone()['count']
        if match_count == 0:
            sample_matches = [
                ('HJK - FC Inter', 'Jännittävä kotipeli, voitto viime hetkillä',
                 user_id),
                ('IFK Mariehamn - HJK', 'Vieraspeli Maarianhaminassa, tasapeli',
                 user_id),
                ('HJK - KuPS', 'Liigaottelu Töölössä, hyvä tunnelma stadionilla',
                 user_id)
            ]
            for title, description, owner_id in sample_matches:
                db.execute(
                    'INSERT INTO match (title, description, owner_id) VALUES (?, ?, ?)',
                    (title, description, owner_id))
            db.commit()
            print('Added 3 sample matches')
        else:
            print('Matches already present; skipping sample data')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('init-db', 'initdb'):
        init_db()
    elif len(sys.argv) > 1 and sys.argv[1] in ('seed-db', 'seeddb'):
        seed_db()
        sys.exit(0)
