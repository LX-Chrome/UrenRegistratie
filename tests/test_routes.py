import unittest
from app import app, db
from models import User, TimeEntry

class TestRoutes(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = app.test_client()
        
        with app.app_context():
            db.create_all()
            # Create test user
            user = User(username='test', email='test@test.com')
            user.set_password('password')
            db.session.add(user)
            db.session.commit()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_login(self):
        response = self.client.post('/login', data={
            'email': 'test@test.com',
            'password': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Welcome', response.data)

    def test_register(self):
        response = self.client.post('/register', data={
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'password'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        with app.app_context():
            user = User.query.filter_by(email='new@test.com').first()
            self.assertIsNotNone(user)

    def test_add_time_entry(self):
        # Login first
        self.client.post('/login', data={
            'email': 'test@test.com',
            'password': 'password'
        })
        
        response = self.client.post('/time-entries', data={
            'date': '2023-01-01',
            'hours': '8',
            'description': 'Test entry',
            'project': 'Test project'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        
        with app.app_context():
            entry = TimeEntry.query.first()
            self.assertIsNotNone(entry)
            self.assertEqual(entry.hours, 8.0)

    def test_export_pdf(self):
        # Login first
        self.client.post('/login', data={
            'email': 'test@test.com',
            'password': 'password'
        })
        
        response = self.client.get('/export-pdf')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.mimetype, 'application/pdf')

if __name__ == '__main__':
    unittest.main()
