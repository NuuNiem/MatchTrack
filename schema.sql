PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS item (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    date TEXT,
    opponent TEXT,
    result TEXT,
    location TEXT,
    description TEXT,
    owner_id INTEGER NOT NULL,
    FOREIGN KEY(owner_id) REFERENCES user(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_item_title ON item(title);
CREATE INDEX IF NOT EXISTS idx_item_description ON item(description);
