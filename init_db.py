# Import the sqlite3 module, which is built into Python's standard library.
# It allows us to interact with SQLite databases using SQL queries.
import sqlite3

def init_database():
    # Connect to the SQLite database file named 'taskmanager.db'.
    # If the file does not exist, SQLite will automatically create it in the same directory.
    conn = sqlite3.connect('taskmanager.db')
    print("Database connection opened successfully.")

    # Create a cursor object. The cursor is used to execute SQL statements
    # and fetch results from the database.
    cursor = conn.cursor()

    # Execute a SQL query to create the 'users' table if it does not already exist.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT, -- A unique auto-incrementing number for each user
            fullname TEXT NOT NULL,                -- The user's full name (cannot be blank)
            username TEXT UNIQUE NOT NULL,         -- A unique login username (cannot be duplicated or blank)
            email TEXT UNIQUE NOT NULL,            -- A unique email address (cannot be duplicated or blank)
            password TEXT NOT NULL                 -- The hashed password string (never store plain text!)
        )
    ''')
    print("Table 'users' verified/created successfully.")

    # Execute a SQL query to create the 'tasks' table if it does not already exist.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,        -- Unique ID for each task
            title TEXT NOT NULL,                         -- Title of the task (cannot be blank)
            description TEXT,                            -- Brief details about the task
            priority TEXT NOT NULL,                      -- Priority level: 'Low', 'Medium', or 'High'
            due_date TEXT,                               -- Due date formatted as YYYY-MM-DD
            status TEXT DEFAULT 'Pending',               -- Status: 'Pending' or 'Completed'
            user_id INTEGER,                             -- Foreign key referencing the users table
            FOREIGN KEY (user_id) REFERENCES users(id)   -- Restricts user_id to valid IDs in users
        )
    ''')
    print("Table 'tasks' verified/created successfully.")

    # Save (commit) the changes we made to the database.
    conn.commit()

    # Close the database connection to free up system resources.
    conn.close()
    print("Database connection closed successfully.")

# Check if this script is executed directly (not imported as a module)
if __name__ == '__main__':
    init_database()
