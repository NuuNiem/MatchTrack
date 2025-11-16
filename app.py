import sys
import os
import sqlite3
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, session, flash, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf.csrf import CSRFProtect
import config

app = Flask(__name__)
# Use values from config.py when present, otherwise fall back to environment or sensible defaults
app.config['SECRET_KEY'] = getattr(config, 'SECRET_KEY', os.environ.get('SECRET_KEY', 'dev-secret-key'))
app.config['DATABASE'] = getattr(config, 'DATABASE', os.environ.get('DATABASE', 'database.db'))
csrf = CSRFProtect(app)


def get_db():
    if 'db' not in g:
        g.db = sqlite3.connect(app.config['DATABASE'])
        g.db.row_factory = sqlite3.Row
    return g.db


@app.teardown_appcontext
def close_db(error=None):
    db = g.pop('db', None)
    if db is not None:
        db.close()


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue')
            return redirect(url_for('login'))
        return func(*args, **kwargs)

    return wrapper


@app.route('/')
def index():
    return redirect(url_for('items'))


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            flash('Username and password required')
            return render_template('register.html')

        db = get_db()
        user = db.execute('SELECT id FROM user WHERE username = ?',
                         (username,)).fetchone()
        if user:
            flash('Username already taken')
            return render_template('register.html')

        password_hash = generate_password_hash(password)
        db.execute('INSERT INTO user (username, password_hash) VALUES (?, ?)',
                   (username, password_hash))
        db.commit()
        flash('Account created. Please log in.')
        return redirect(url_for('login'))
    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username'].strip()
        password = request.form['password']
        if not username or not password:
            flash('Username and password required')
            return render_template('login.html')

        db = get_db()
        user = db.execute(
            'SELECT id, username, password_hash FROM user WHERE username = ?',
            (username,)).fetchone()

        if user and check_password_hash(user['password_hash'], password):
            session['user_id'] = user['id']
            session['username'] = user['username']
            flash('Logged in successfully')
            return redirect(url_for('items'))
        flash('Invalid username or password')
        return render_template('login.html')
    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully')
    return redirect(url_for('login'))


@app.route('/items')
def items():
    q = request.args.get('q', '').strip()
    db = get_db()

    if q:
        like = f"%{q}%"
        items_list = db.execute('''
            SELECT id, title, description, owner_id
            FROM item
            WHERE title LIKE ? OR description LIKE ?
            ORDER BY id DESC
        ''', (like, like)).fetchall()
    else:
        items_list = db.execute(
            'SELECT id, title, description, owner_id FROM item ORDER BY id DESC'
        ).fetchall()

    return render_template('index.html', items=items_list, q=q)
@app.route('/items/new', methods=['GET', 'POST'])
@login_required
def new_item():
    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form.get('description', '').strip()
        if not title:
            flash('Title is required')
            return render_template('new_item.html')

        db = get_db()
        db.execute(
            'INSERT INTO item (title, description, owner_id) VALUES (?, ?, ?)',
            (title, description, session['user_id']))
        db.commit()
        flash('Item added successfully')
        return redirect(url_for('items'))
    return render_template('new_item.html')
@app.route('/items/<int:item_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_item(item_id):
    db = get_db()
    item = db.execute(
        'SELECT id, title, description, owner_id FROM item WHERE id = ?',
        (item_id,)).fetchone()

    if not item:
        flash('Item not found')
        return redirect(url_for('items'))

    if item['owner_id'] != session['user_id']:
        flash('You are not the owner of this item')
        return redirect(url_for('items'))

    if request.method == 'POST':
        title = request.form['title'].strip()
        description = request.form.get('description', '').strip()
        if not title:
            flash('Title is required')
            return render_template('edit_item.html', item=item)

        db.execute(
            'UPDATE item SET title = ?, description = ? WHERE id = ?',
            (title, description, item_id))
        db.commit()
        flash('Item updated successfully')
        return redirect(url_for('items'))

    return render_template('edit_item.html', item=item)
@app.route('/items/<int:item_id>/delete', methods=['POST'])
@login_required
def delete_item(item_id):
    db = get_db()
    item = db.execute(
        'SELECT id, owner_id FROM item WHERE id = ?',
        (item_id,)).fetchone()

    if not item:
        flash('Item not found')
        return redirect(url_for('items'))

    if item['owner_id'] != session['user_id']:
        flash('You are not the owner of this item')
        return redirect(url_for('items'))

    db.execute('DELETE FROM item WHERE id = ?', (item_id,))
    db.commit()
    flash('Item deleted successfully')
    return redirect(url_for('items'))
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

        item_count = db.execute(
            'SELECT COUNT(*) as count FROM item').fetchone()['count']
        if item_count == 0:
            sample_items = [
                ('HJK - FC Inter', 'Jännittävä kotipeli, voitto viime hetkillä',
                 user_id),
                ('IFK Mariehamn - HJK', 'Vieraspeli Maarianhaminassa, tasapeli',
                 user_id),
                ('HJK - KuPS', 'Liigaottelu Töölössä, hyvä tunnelma stadionilla',
                 user_id)
            ]
            for title, description, owner_id in sample_items:
                db.execute(
                    'INSERT INTO item (title, description, owner_id) VALUES (?, ?, ?)',
                    (title, description, owner_id))
            db.commit()
            print('Added 3 sample items')
        else:
            print('Items already present; skipping sample data')


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] in ('init-db', 'initdb'):
        init_db()
    elif len(sys.argv) > 1 and sys.argv[1] in ('seed-db', 'seeddb'):
        seed_db()
        sys.exit(0)
