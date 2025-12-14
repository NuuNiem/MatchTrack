"""
Seed database with test data.
This module creates test users, categories, matches, and comments.
"""
import random
from werkzeug.security import generate_password_hash
from app import app, get_db


def seed_db():
    """Populate database with test data."""
    with app.app_context():
        db = get_db()

        usernames = [
            'test', 'matti', 'liisa', 'jussi', 'anna', 'mikko', 'maria',
            'timo', 'sanna', 'pekka', 'laura', 'ville', 'kaisa', 'janne',
            'helena', 'erkki', 'nina', 'petri', 'hanna', 'juha'
        ]

        teams = [
            'HJK', 'KuPS', 'FC Inter', 'IFK Mariehamn', 'Ilves', 'FC Lahti',
            'SJK', 'VPS', 'Haka', 'HIFK', 'AC Oulu', 'FC Honka'
        ]

        match_descriptions = [
            'Jännittävä ottelu, voitto viime hetkillä!',
            'Tasapeli, molemmat joukkueet pelasivat hyvin',
            'Hyvä tunnelma stadionilla',
            'Komea voitto kotikentällä',
            'Vaikea tappio vieraissa',
            'Upea ilta jalkapalloa',
            'Mahtavat maalit, hienoa pelaamista',
            'Säät olivat huonot mutta peli oli hyvä',
            'Erinomainen esitys molemmilta joukkueilta',
            'Intensiivinen peli loppuun asti',
            'Fanien kannustus oli huikea',
            'Historiallinen ottelu',
            'Nuoret pelaajat loistivat',
            'Kaunis ilta kesäisellä stadionilla',
            'Värikäs tapahtuma koko perheelle'
        ]

        comment_texts = [
            'Hieno ottelu!',
            'Olin myös paikalla, mahtava tunnelma!',
            'Harmi että hävittiin',
            'Paras ottelu tällä kaudella',
            'Haluaisin nähdä uusintaottelun',
            'Maalintekijä pelasi loistavasti',
            'Kannattaa käydä katsomassa',
            'Liput oli järkevän hintaisia',
            'Stadion oli täynnä',
            'Kyllä tämä oli kokemisen arvoinen'
        ]

        print('Creating users...')
        user_ids = []
        for username in usernames:
            existing = db.execute(
                'SELECT id FROM user WHERE username = ?',
                (username,)).fetchone()

            if existing:
                user_ids.append(existing['id'])
                print(f'User {username} already exists')
            else:
                db.execute(
                    'INSERT INTO user (username, password_hash) VALUES (?, ?)',
                    (username, generate_password_hash('testpass123')))
                db.commit()
                user = db.execute(
                    'SELECT id FROM user WHERE username = ?',
                    (username,)).fetchone()
                user_ids.append(user['id'])
                print(f'Created user: {username} / testpass123')

        print('\nCreating categories...')
        categories = ['Liiga', 'Cupin ottelu', 'Harjoituspeli', 'Ystävyysottelu']
        category_ids = []

        for cat_name in categories:
            existing = db.execute(
                'SELECT id FROM category WHERE name = ?',
                (cat_name,)).fetchone()

            if existing:
                category_ids.append(existing['id'])
            else:
                db.execute('INSERT INTO category (name) VALUES (?)', (cat_name,))
                db.commit()
                cat = db.execute(
                    'SELECT id FROM category WHERE name = ?',
                    (cat_name,)).fetchone()
                category_ids.append(cat['id'])

        print(f'Categories ready: {len(category_ids)} categories')

        print('\nCreating matches...')
        match_count = db.execute(
            'SELECT COUNT(*) as count FROM match').fetchone()['count']

        if match_count > 0:
            print(f'{match_count} matches already exist. Skipping match creation.')
        else:
            for i in range(60):
                home_team = random.choice(teams)
                away_team = random.choice([t for t in teams if t != home_team])
                title = f'{home_team} - {away_team}'
                description = random.choice(match_descriptions)
                owner_id = random.choice(user_ids)

                cursor = db.execute(
                    'INSERT INTO match (title, description, owner_id) VALUES (?, ?, ?)',
                    (title, description, owner_id))
                match_id = cursor.lastrowid

                num_categories = random.randint(1, 2)
                selected_cats = random.sample(category_ids, num_categories)
                for cat_id in selected_cats:
                    db.execute(
                        'INSERT INTO match_category (match_id, category_id) VALUES (?, ?)',
                        (match_id, cat_id))

                db.commit()

            print(f'Created 60 matches')

        print('\n✓ Database seeded successfully!')
        print(f'  Users: {len(user_ids)}')
        print(f'  Categories: {len(category_ids)}')
        print(f'  Matches: 60')
        print('\nAll users have password: testpass123')


if __name__ == '__main__':
    seed_db()
