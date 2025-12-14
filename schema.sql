PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS match (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    date TEXT,
    opponent TEXT,
    result TEXT,
    location TEXT,
    description TEXT,
    custom_category TEXT,
    owner_id INTEGER NOT NULL,
    FOREIGN KEY(owner_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_match_title ON match(title);
CREATE INDEX IF NOT EXISTS idx_match_description ON match(description);

CREATE TABLE IF NOT EXISTS category (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS match_category (
    match_id INTEGER NOT NULL,
    category_id INTEGER NOT NULL,
    PRIMARY KEY (match_id, category_id),
    FOREIGN KEY(match_id) REFERENCES match(id) ON DELETE CASCADE,
    FOREIGN KEY(category_id) REFERENCES category(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS comment (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    match_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(match_id) REFERENCES match(id) ON DELETE CASCADE,
    FOREIGN KEY(user_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_comment_match ON comment(match_id);
