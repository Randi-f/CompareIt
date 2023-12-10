"""
Author: shihan
Date: 2023-12-07 21:37:25
version: 1.0
description: 
"""
import unittest
from flask import Flask
import app
from app import translate_to_english


class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.app.test_client()
        app.app.config["TESTING"] = True

    def test_open_login_page(self):
        response = self.app.get("/login")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Login", response.data)


# def test_translate_to_english():
#     assert (  # test locally, cannot test on github because the api needs authentication of ip, but the github test ip changes each time
#         translate_to_english("接入举例") == "Access examples"
#     )

# if __name__ == "__main__":
#     unittest.main()
