import sys
import os
import sqlite3
import secrets
from flask import Flask, session, g
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


init_routes(app, get_db)


def init_db():
    with app.app_context():
        db = get_db()
        with open('schema.sql', encoding='utf-8') as f:
            db.executescript(f.read())
        db.commit()
    print('Database initialized (created tables)')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('init-db', 'initdb'):
        init_db()
    elif len(sys.argv) > 1 and sys.argv[1] in ('seed-db', 'seeddb'):
        from seed import seed_db
        seed_db()
        sys.exit(0)
