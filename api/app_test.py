import unittest
from flask import Flask
import app  # Assuming your app is defined in a file named app.py


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()
        app.app.config["TESTING"] = True

    def test_open_login_page(self):
        response = self.app.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(
            b"Login", response.data
        )  # Ensure the word 'Login' is present in the response


if __name__ == "__main__":
    unittest.main()
