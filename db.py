import sqlite3
from time import time
from typing import List, Union

# Create a connection to the database
with sqlite3.connect("yemin_bot.db") as conn:
    conn.row_factory = sqlite3.Row
    # Create a cursor to execute SQL queries
    c = conn.cursor()

    # Create the table if it doesn't already exist
    c.execute(
        """
       CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            user_id INTEGER NOT NULL,
            warnings INTEGER DEFAULT 1,
            last_warning_date INTEGER NOT NULL
        )"""
    )
    c.execute(
        """
        CREATE TABLE IF NOT EXISTS censored_strings (
        id INTEGER PRIMARY KEY,
        string TEXT UNIQUE NOT NULL
        );"""
    )
    conn.commit()

    # Insert a new censor_string into the table
    def add_censor_string(str: str):
        try:
            c.execute(
                "INSERT INTO censored_strings (string) VALUES (?)",
                (str,),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass

    # Remove a censor_string from the table
    def remove_censor_string(str: str):
        try:
            c.execute(
                "DELETE FROM censored_strings WHERE string = ?",
                (str,),
            )
            conn.commit()
        except sqlite3.IntegrityError:
            pass

    # Insert a new censor_string into the table
    def read_censor_strings() -> List[sqlite3.Row]:
        c.execute("SELECT * FROM censored_strings")
        return c.fetchall()

    # Insert a new user into the table
    def create_user(user_id):
        c.execute(
            "INSERT INTO users (user_id, last_warning_date) VALUES (?, ?)",
            (user_id, int(time())),
        )
        conn.commit()

    # Get a list of all users in the table
    def read_users():
        c.execute("SELECT * FROM users")
        return c.fetchall()

    # Check if a user exists and return the number of warnings they have
    def get_user(user_id) -> Union[sqlite3.Row, None]:
        c.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        return c.fetchone()

    # Update a user's warning count
    def update_warnings(user_id: int, warnings: int):
        c.execute(
            "UPDATE users SET warnings = ?, last_warning_date = ? WHERE user_id = ?",
            (warnings, int(time()), user_id),
        )
        conn.commit()

    # Delete a user from the table
    def delete_user(user_id):
        c.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
        conn.commit()
