from unittest import TestCase
from unittest.mock import Mock, patch
from user import Database, UserService, User
import sqlite3


class TestDatabase(TestCase):
    @patch('sqlite3.connect')
    def setUp(self, mock_connect):
        """Setup a mock database connection."""
        self.mock_conn = Mock()
        mock_connect.return_value = self.mock_conn
        self.mock_cursor = self.mock_conn.cursor.return_value
        self.db = Database('test.db')

    def test_insert_user(self):
        """Test insert_user method"""
        self.mock_cursor.lastrowid = 1
        user_id = self.db.insert_user('Twinkle', 25)
          # self.mock_cursor.execute.assert_called_with('INSERT INTO users (name, age) VALUES (?, ?)', ('Twinkle', 25))   
        self.assertEqual(user_id, 1)

    def test_insert_user_exception(self):
        """Test exception handling in insert_user"""
        self.mock_cursor.execute.side_effect = sqlite3.Error("Insert error")
        with self.assertRaises(sqlite3.Error):
            self.db.insert_user('Twinkle', 25)
     
    @patch('sqlite3.connect', side_effect=sqlite3.Error("Connection error"))
    def test_database_init_exception(self, mock_connect):
        """Test exception handling in Database.__init__"""
        with self.assertRaises(sqlite3.Error):
            Database('test.db')

    def test_get_user(self):
        """Test get_user method"""
        self.mock_cursor.fetchone.return_value = (1, 'Twinkle', 25)
        user = self.db.get_user(1)
        self.assertIsInstance(user, User)
           # self.mock_cursor.execute.assert_called_with('SELECT * FROM users WHERE user_id = ?', (1,))
        self.assertEqual(user.user_id, 1)
        self.assertEqual(user.name, "Twinkle")
        self.assertEqual(user.age, 25)
      

    def test_get_user_exception(self):
        """Test exception handling in get_user"""
        self.mock_cursor.execute.side_effect = sqlite3.Error("Fetch error")
        with self.assertRaises(sqlite3.Error):
            self.db.get_user(1)

    def test_get_non_existent_user(self):
        """Test retrieving a non-existent user"""
        self.mock_cursor.fetchone.return_value = None
        user = self.db.get_user(999)
        self.assertIsNone(user)
         # self.mock_db.get_user.assert_called_with(999)

    def test_update_user(self):
        """Test update_user method"""
        self.mock_cursor.rowcount = 1
        rows_affected = self.db.update_user(1, name='Jeffery')
        self.assertEqual(rows_affected, 1)
         # self.mock_cursor.execute.assert_called_with('UPDATE users SET name = ? WHERE user_id = ?', ('Jeffery', 1))

    def test_update_user_no_fields(self):
        """Test updating a user with no fields provided"""
        with self.assertRaises(ValueError):
            self.db.update_user(1)

    def test_update_user_exception(self):
        """Test exception handling in update_user"""
        self.mock_cursor.execute.side_effect = sqlite3.Error("Update error")
        with self.assertRaises(sqlite3.Error):
            self.db.update_user(1, name='Jeffery')

    def test_delete_user(self):
        """Test delete_user method"""
        self.mock_cursor.rowcount = 1
        rows_affected = self.db.delete_user(1)
        self.assertEqual(rows_affected, 1)
         # self.mock_cursor.execute.assert_called_with('DELETE FROM users WHERE user_id = ?', (1,))

    def test_delete_user_exception(self):
        """Test exception handling in delete_user"""
        self.mock_cursor.execute.side_effect = sqlite3.Error("Delete error")
        with self.assertRaises(sqlite3.Error):
            self.db.delete_user(1)

    def test_delete_non_existent_user(self):
        """Test deleting a non-existent user"""
        self.mock_cursor.rowcount = 0
        rows_affected = self.db.delete_user(999)
        self.assertEqual(rows_affected, 0)
          # self.mock_cursor.execute.assert_called_with('DELETE FROM users WHERE user_id = ?', (999,) )

    def test_close(self):
        """Test closing the database connection."""
        self.db.close()
        self.mock_conn.close.assert_called_once()

    def test_close_exception(self):
        """Test exception handling in Database.close"""
        self.mock_conn.close.side_effect = sqlite3.Error("Close error")
        with self.assertRaises(sqlite3.Error):
            self.db.close()


class TestUserService(TestCase):
    def setUp(self):
        """Setup a mock database."""
        self.mock_db = Mock()
        self.user_service = UserService(self.mock_db)

    def test_create_user(self):
        """Test UserService.create_user method"""
        self.mock_db.insert_user.return_value = 1
        result, status = self.user_service.create_user("Alice", 30)
        self.assertEqual(result, {"user_id": 1, "name": "Alice", "age": 30})
        self.assertEqual(status, 201)

    def test_create_user_invalid_name(self):
        """Test create_user with invalid name"""
        result, status = self.user_service.create_user("", 30)
        self.assertEqual(result, {"error": "Invalid name"})
        self.assertEqual(status, 400)

    def test_create_user_invalid_age(self):
        """Test create_user with invalid age"""
        result, status = self.user_service.create_user("Alice", -1)
        self.assertEqual(result, {"error": "Invalid age"})
        self.assertEqual(status, 400)

    def test_create_user_exception(self):
        """Test exception handling in create_user"""
        self.mock_db.insert_user.side_effect = Exception("Insert error")
        result, status = self.user_service.create_user("Alice", 30)
        self.assertEqual(result, {"error": "Failed to create user"})
        self.assertEqual(status, 500)

    def test_get_user(self):
        """Test UserService.get_user method"""
        self.mock_db.get_user.return_value = User(1, "Twinkle", 25)
        result, status = self.user_service.get_user(1)
        self.assertEqual(result, {"user_id": 1, "name": "Twinkle", "age": 25})
        self.assertEqual(status, 200)

    def test_get_user_exception(self):
        """Test exception handling in get_user"""
        self.mock_db.get_user.side_effect = Exception("Fetch error")
        result, status = self.user_service.get_user(1)
        self.assertEqual(result, {"error": "Failed to retrieve user"})
        self.assertEqual(status, 500)

    def test_get_non_existent_user(self):
        """Test get_user for a non-existent user"""
        self.mock_db.get_user.return_value = None
        result, status = self.user_service.get_user(999)
          # self.mock_cursor.execute.assert_called_with('SELECT * FROM users WHERE user_id = ?', (999,))
        self.assertEqual(result, {"error": "User not found"})
        self.assertEqual(status, 404)
        

    def test_service_del_exception(self):
        """Test exception handling in UserService.__del__"""
        self.mock_db.close.side_effect = Exception("Close error")
        del self.user_service
        self.mock_db.close.assert_called_once()
