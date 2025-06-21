import unittest
import json
from app import app, DATA_FILE
import os

class CalendarAppTestCase(unittest.TestCase):
    def setUp(self):
        # Set up test client
        self.app = app.test_client()
        self.app.testing = True
        # Backup existing data file if exists
        if os.path.exists(DATA_FILE):
            os.rename(DATA_FILE, DATA_FILE + '.bak')

    def tearDown(self):
        # Remove test data file
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        # Restore backup if exists
        if os.path.exists(DATA_FILE + '.bak'):
            os.rename(DATA_FILE + '.bak', DATA_FILE)

    def test_get_schedules_missing_params(self):
        response = self.app.get('/api/schedules')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_get_schedules_invalid_params(self):
        response = self.app.get('/api/schedules?year=2025&month=13')
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_post_schedule_invalid_json(self):
        response = self.app.post('/api/schedules', data='notjson', content_type='application/json')
        self.assertEqual(response.status_code, 400)

    def test_post_schedule_missing_fields(self):
        response = self.app.post('/api/schedules', json={})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_post_schedule_invalid_date(self):
        response = self.app.post('/api/schedules', json={'date': '2025-02-30', 'text': 'Test'})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertIn('error', data)

    def test_post_and_get_schedule(self):
        # Post a schedule
        post_data = {'date': '2025-06-21', 'text': 'Test schedule'}
        response = self.app.post('/api/schedules', json=post_data)
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('message', data)

        # Get schedules for June 2025
        response = self.app.get('/api/schedules?year=2025&month=6')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('2025-06-21', data)
        self.assertEqual(data['2025-06-21'], 'Test schedule')

    def test_post_empty_text_removes_schedule(self):
        # Add schedule first
        post_data = {'date': '2025-06-22', 'text': 'To be removed'}
        self.app.post('/api/schedules', json=post_data)

        # Remove schedule by posting empty text
        post_data = {'date': '2025-06-22', 'text': ''}
        response = self.app.post('/api/schedules', json=post_data)
        self.assertEqual(response.status_code, 200)

        # Check schedule is removed
        response = self.app.get('/api/schedules?year=2025&month=6')
        data = json.loads(response.data)
        self.assertNotIn('2025-06-22', data)

if __name__ == '__main__':
    unittest.main()
