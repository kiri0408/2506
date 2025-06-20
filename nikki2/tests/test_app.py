import unittest
import json
from app import app, DATA_FILE
import os

class DiaryAppTestCase(unittest.TestCase):
    def setUp(self):
        # Set up test client
        self.app = app.test_client()
        self.app.testing = True
        # Backup existing diary file if exists
        if os.path.exists(DATA_FILE):
            os.rename(DATA_FILE, DATA_FILE + '.bak')

    def tearDown(self):
        # Remove test diary file
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        # Restore backup if exists
        if os.path.exists(DATA_FILE + '.bak'):
            os.rename(DATA_FILE + '.bak', DATA_FILE)

    def test_get_diary_missing_params(self):
        response = self.app.get('/api/diary')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_get_diary_empty(self):
        response = self.app.get('/api/diary?year=2025&month=6')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, dict)
        self.assertEqual(len(data), 0)

    def test_post_and_get_diary(self):
        # Post a diary entry
        post_data = {
            'date': '2025-06-20',
            'content': '今日はテストを書きました。'
        }
        response = self.app.post('/api/diary', json=post_data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)

        # Get diary for June 2025
        response = self.app.get('/api/diary?year=2025&month=6')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('2025-06-20', data)
        self.assertEqual(data['2025-06-20'], '今日はテストを書きました。')

    def test_post_invalid_date(self):
        post_data = {
            'date': '2025-13-01',
            'content': '不正な日付'
        }
        response = self.app.post('/api/diary', json=post_data)
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_post_missing_fields(self):
        response = self.app.post('/api/diary', json={})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

if __name__ == '__main__':
    unittest.main()
