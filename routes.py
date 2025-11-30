import secrets
from functools import wraps
from flask import render_template, request, redirect, url_for, session, flash, abort
from werkzeug.security import generate_password_hash, check_password_hash


def login_required(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to continue')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return wrapper


def check_csrf():
    if request.form.get('csrf_token') != session.get('csrf_token'):
        abort(403)


def init_routes(app, get_db):

    @app.route('/')
    def index():
        return redirect(url_for('matches'))

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            check_csrf()
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
            check_csrf()
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
                return redirect(url_for('matches'))
            flash('Invalid username or password')
            return render_template('login.html')
        return render_template('login.html')

    @app.route('/logout')
    def logout():
        session.clear()
        flash('Logged out successfully')
        return redirect(url_for('login'))

    @app.route('/matches')
    def matches():
        q = request.args.get('q', '').strip()
        db = get_db()

        if q:
            like = f"%{q}%"
            matches_list = db.execute('''
                SELECT match.id, match.title, match.description, match.owner_id, user.username
                FROM match
                JOIN user ON match.owner_id = user.id
                WHERE match.title LIKE ? OR match.description LIKE ?
                ORDER BY match.id DESC
            ''', (like, like)).fetchall()
        else:
            matches_list = db.execute('''
                SELECT match.id, match.title, match.description, match.owner_id, user.username
                FROM match
                JOIN user ON match.owner_id = user.id
                ORDER BY match.id DESC
            ''').fetchall()

        return render_template('index.html', matches=matches_list, q=q)

    @app.route('/matches/new', methods=['GET', 'POST'])
    @login_required
    def new_match():
        db = get_db()
        categories = db.execute('SELECT id, name FROM category ORDER BY name').fetchall()

        if request.method == 'POST':
            check_csrf()
            title = request.form['title'].strip()
            description = request.form.get('description', '').strip()
            if not title:
                flash('Title is required')
                return render_template('new_match.html', categories=categories)

            cursor = db.execute(
                'INSERT INTO match (title, description, owner_id) VALUES (?, ?, ?)',
                (title, description, session['user_id']))
            match_id = cursor.lastrowid

            # Save selected categories
            selected_categories = request.form.getlist('categories')
            for cat_id in selected_categories:
                db.execute(
                    'INSERT INTO match_category (match_id, category_id) VALUES (?, ?)',
                    (match_id, int(cat_id)))

            db.commit()
            flash('Match added successfully')
            return redirect(url_for('matches'))
        return render_template('new_match.html', categories=categories)

    @app.route('/matches/<int:match_id>/edit', methods=['GET', 'POST'])
    @login_required
    def edit_match(match_id):
        db = get_db()
        match = db.execute(
            'SELECT id, title, description, owner_id FROM match WHERE id = ?',
            (match_id,)).fetchone()

        if not match:
            flash('Match not found')
            return redirect(url_for('matches'))

        if match['owner_id'] != session['user_id']:
            flash('You are not the owner of this match')
            return redirect(url_for('matches'))

        categories = db.execute('SELECT id, name FROM category ORDER BY name').fetchall()
        selected_categories = [
            row['category_id'] for row in db.execute(
                'SELECT category_id FROM match_category WHERE match_id = ?',
                (match_id,)).fetchall()
        ]

        if request.method == 'POST':
            check_csrf()
            title = request.form['title'].strip()
            description = request.form.get('description', '').strip()
            if not title:
                flash('Title is required')
                return render_template('edit_match.html', match=match,
                                       categories=categories,
                                       selected_categories=selected_categories)

            db.execute(
                'UPDATE match SET title = ?, description = ? WHERE id = ?',
                (title, description, match_id))

            # Update categories: delete old, insert new
            db.execute('DELETE FROM match_category WHERE match_id = ?', (match_id,))
            selected_cats = request.form.getlist('categories')
            for cat_id in selected_cats:
                db.execute(
                    'INSERT INTO match_category (match_id, category_id) VALUES (?, ?)',
                    (match_id, int(cat_id)))

            db.commit()
            flash('Match updated successfully')
            return redirect(url_for('matches'))

        return render_template('edit_match.html', match=match,
                               categories=categories, selected_categories=selected_categories)

    @app.route('/matches/<int:match_id>')
    def match_detail(match_id):
        db = get_db()
        match = db.execute('''
            SELECT match.id, match.title, match.description, match.owner_id, user.username
            FROM match
            JOIN user ON match.owner_id = user.id
            WHERE match.id = ?
        ''', (match_id,)).fetchone()

        if not match:
            flash('Ottelua ei löytynyt')
            return redirect(url_for('matches'))

        # Get categories
        categories = db.execute('''
            SELECT category.name
            FROM category
            JOIN match_category ON category.id = match_category.category_id
            WHERE match_category.match_id = ?
        ''', (match_id,)).fetchall()
        cat_names = ', '.join([c['name'] for c in categories])

        # Get comments
        comments = db.execute('''
            SELECT comment.id, comment.content, comment.created_at, user.username
            FROM comment
            JOIN user ON comment.user_id = user.id
            WHERE comment.match_id = ?
            ORDER BY comment.created_at DESC
        ''', (match_id,)).fetchall()

        return render_template('match_detail.html',
                               match=match, categories=cat_names, comments=comments)

    @app.route('/matches/<int:match_id>/comment', methods=['POST'])
    @login_required
    def add_comment(match_id):
        check_csrf()

        content = request.form.get('content', '').strip()
        if not content:
            flash('Kommentti ei voi olla tyhjä')
            return redirect(url_for('match_detail', match_id=match_id))

        db = get_db()
        # Check match exists
        match = db.execute('SELECT id FROM match WHERE id = ?', (match_id,)).fetchone()
        if not match:
            flash('Ottelua ei löytynyt')
            return redirect(url_for('matches'))

        db.execute(
            'INSERT INTO comment (match_id, user_id, content) VALUES (?, ?, ?)',
            (match_id, session['user_id'], content))
        db.commit()
        flash('Kommentti lisätty')
        return redirect(url_for('match_detail', match_id=match_id))

    @app.route('/matches/<int:match_id>/delete', methods=['POST'])
    @login_required
    def delete_match(match_id):
        db = get_db()
        match = db.execute(
            'SELECT id, owner_id FROM match WHERE id = ?',
            (match_id,)).fetchone()

        if not match:
            flash('Match not found')
            return redirect(url_for('matches'))

        if match['owner_id'] != session['user_id']:
            flash('You are not the owner of this match')
            return redirect(url_for('matches'))

        # Validate CSRF for destructive action
        check_csrf()

        db.execute('DELETE FROM match WHERE id = ?', (match_id,))
        db.commit()
        flash('Match deleted successfully')
        return redirect(url_for('matches'))

    @app.route('/user/<int:user_id>')
    def user_profile(user_id):
        db = get_db()
        user = db.execute('SELECT id, username FROM user WHERE id = ?',
                          (user_id,)).fetchone()
        if not user:
            flash('Käyttäjää ei löytynyt')
            return redirect(url_for('matches'))

        # Count matches and comments by user
        match_count = db.execute(
            'SELECT COUNT(*) as count FROM match WHERE owner_id = ?',
            (user_id,)).fetchone()['count']
        comment_count = db.execute(
            'SELECT COUNT(*) as count FROM comment WHERE user_id = ?',
            (user_id,)).fetchone()['count']

        # Get user's matches
        user_matches = db.execute(
            'SELECT id, title, description FROM match WHERE owner_id = ? ORDER BY id DESC',
            (user_id,)).fetchall()

        return render_template('user_profile.html',
                               user=user,
                               match_count=match_count,
                               comment_count=comment_count,
                               user_matches=user_matches)
