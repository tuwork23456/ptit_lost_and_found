import os
import sqlite3


def has_column(cursor: sqlite3.Cursor, table: str, column: str) -> bool:
    cursor.execute(f"PRAGMA table_info({table})")
    cols = [row[1] for row in cursor.fetchall()]
    return column in cols


def main():
    db_path = os.path.join(os.path.dirname(__file__), "lostfound.db")
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        if not has_column(cur, "users", "role"):
            cur.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'USER'")
            print("Added users.role")

        if not has_column(cur, "posts", "moderation_status"):
            cur.execute("ALTER TABLE posts ADD COLUMN moderation_status TEXT DEFAULT 'APPROVED'")
            print("Added posts.moderation_status")

        if not has_column(cur, "posts", "moderation_note"):
            cur.execute("ALTER TABLE posts ADD COLUMN moderation_note TEXT")
            print("Added posts.moderation_note")

        if not has_column(cur, "posts", "moderated_by"):
            cur.execute("ALTER TABLE posts ADD COLUMN moderated_by INTEGER")
            print("Added posts.moderated_by")

        if not has_column(cur, "posts", "moderated_at"):
            cur.execute("ALTER TABLE posts ADD COLUMN moderated_at DATETIME")
            print("Added posts.moderated_at")

        cur.execute("UPDATE users SET role = 'USER' WHERE role IS NULL OR TRIM(role) = ''")
        cur.execute("UPDATE users SET role = 'ADMIN' WHERE lower(email) IN ('admin@ptit.edu.vn', 'user1@example.com')")
        cur.execute("UPDATE posts SET moderation_status = 'APPROVED' WHERE moderation_status IS NULL OR TRIM(moderation_status) = ''")

        conn.commit()
        print("Migration completed successfully.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
