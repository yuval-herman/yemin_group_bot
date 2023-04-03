import sqlite3

# Create a connection to the database
with sqlite3.connect("yemin_bot.db") as conn:
    # Create a cursor to execute SQL queries
    c = conn.cursor()

    # Create the table if it doesn't already exist
    c.execute(
        """
       CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            warnings INTEGER DEFAULT 1,
            last_warning_date TEXT
        )
    """
    )
    conn.commit()

    # Insert a new user into the table
    def create_user(user_id):
        c.execute("INSERT INTO users (user_id) VALUES (?)", (user_id,))
        conn.commit()

    # Get a list of all users in the table
    def read_users():
        c.execute("SELECT * FROM users")
        return c.fetchall()

    # Check if a user exists and return the number of warnings they have
    def get_user_warnings(user_id) -> int | None:
        c.execute("SELECT warnings FROM users WHERE user_id = ?", (user_id,))
        result = c.fetchone()
        if result is None:
            return None  # User not found
        else:
            return result[0]

    # Update a user's warning count
    def update_warnings(user_id: int, warnings: int):
        c.execute(
            "UPDATE users SET warnings = ? WHERE user_id = ?", (warnings, user_id)
        )
        conn.commit()

    # Delete a user from the table
    def delete_user(user_id):
        c.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
