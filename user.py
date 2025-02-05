import sqlite3


class User:
    def __init__(self, user_id, name, age):
        self.user_id = user_id
        self.name = name
        self.age = age


class Database:
    def __init__(self, db_name):
        """Initialize database connection and create users table if not exists."""
        try:
            self.conn = sqlite3.connect(db_name)
            self.cursor = self.conn.cursor()
            self.cursor.execute('''
                CREATE TABLE IF NOT EXISTS users
                (user_id INTEGER PRIMARY KEY, name TEXT, age INTEGER)
            ''')
            self.conn.commit()
        except sqlite3.Error as e:
            print(f"Error connecting to the database: {e}")
            raise

    def insert_user(self, name, age):
        """Insert a new user into the database and return the new user_id."""
        try:
            self.cursor.execute('INSERT INTO users (name, age) VALUES (?, ?)', (name, age))
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            print(f"Error inserting user: {e}")
            raise

    def update_user(self, user_id, name=None, age=None):
        """Update user details in the database."""
        updates = []
        params = []

        if name:
            updates.append("name = ?")
            params.append(name)
        if age:
            updates.append("age = ?")
            params.append(age)

        if not updates:
            raise ValueError("No fields provided for update.")

        params.append(user_id)
        query = f"UPDATE users SET {', '.join(updates)} WHERE user_id = ?"

        try:
            self.cursor.execute(query, tuple(params))
            self.conn.commit()
            return self.cursor.rowcount
        except sqlite3.Error as e:
            print(f"Error updating user: {e}")
            raise

    def delete_user(self, user_id):
        """Delete user from the database and return the number of rows affected."""
        try:
            self.cursor.execute('DELETE FROM users WHERE user_id = ?', (user_id,))
            self.conn.commit()
            return self.cursor.rowcount
        except sqlite3.Error as e:
            print(f"Error deleting user: {e}")
            raise

    def get_user(self, user_id):
        """Fetch a user from the database by user_id and return a User object."""
        try:
            self.cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
            row = self.cursor.fetchone()
            return User(*row) if row else None
        except sqlite3.Error as e:
            print(f"Error fetching user: {e}")
            raise

    def close(self):
        """Close the database connection."""
        try:
            self.conn.close()
        except sqlite3.Error as e:
            print(f"Error closing database connection: {e}")
            raise


class UserService:
    def __init__(self, db):
        self.db = db

    def create_user(self, name, age):
        """Create a new user and return user details."""
        if not name or not isinstance(name, str):
            return {"error": "Invalid name"}, 400
        if not isinstance(age, int) or age <= 0:
            return {"error": "Invalid age"}, 400

        try:
            user_id = self.db.insert_user(name, age)
            return {"user_id": user_id, "name": name, "age": age}, 201
        except Exception as e:
            print(f"Error creating user: {e}")
            return {"error": "Failed to create user"}, 500

    def get_user(self, user_id):
        """Retrieve a user by ID."""
        try:
            user = self.db.get_user(user_id)
            if user:
                return {"user_id": user.user_id, "name": user.name, "age": user.age}, 200
            return {"error": "User not found"}, 404
        except Exception as e:
            print(f"Error retrieving user: {e}")
            return {"error": "Failed to retrieve user"}, 500

    def __del__(self):
        """Ensure database connection is closed when service is deleted."""
        try:
            self.db.close()
        except Exception as e:
            print(f"Error closing database connection: {e}")
