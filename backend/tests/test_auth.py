"""Cookie authentication and role isolation against a temporary database."""
import tempfile
import unittest
from flask import Flask
from flask_jwt_extended import JWTManager
from werkzeug.security import generate_password_hash
import auth_app
from db import db
from models import User


class AuthenticationTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.app = Flask(__name__)
        self.app.config.update(TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite:///' + self.temp.name + '/test.db',
            JWT_SECRET_KEY='test-key-long-enough-for-hmac-signing',
            JWT_TOKEN_LOCATION=['cookies'], JWT_COOKIE_CSRF_PROTECT=True)
        db.init_app(self.app)
        JWTManager(self.app)
        for rule in auth_app.app.url_map.iter_rules():
            if rule.endpoint != 'static':
                self.app.add_url_rule(rule.rule, rule.endpoint,
                    auth_app.app.view_functions[rule.endpoint], methods=rule.methods)
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        for role in ('admin', 'staff', 'user'):
            db.session.add(User(username=role, email=role + '@test.com',
                password=generate_password_hash('password'), role=role))
        db.session.commit()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.engine.dispose()
        self.context.pop()
        self.temp.cleanup()

    def login(self, role):
        return self.client.post('/api/login', json={
            'email': role + '@test.com', 'password': 'password'})

    def test_registration_cannot_choose_privileged_role(self):
        for role in ('admin', 'staff'):
            response = self.client.post('/api/register', json={
                'username': 'New', 'email': 'new-' + role + '@test.com',
                'password': 'password', 'role': role})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(User.query.filter_by(email='new-' + role + '@test.com').one().role, 'user')

    def test_cookie_login_and_role_boundaries(self):
        self.assertEqual(self.client.get('/api/who').status_code, 401)
        for role in ('admin', 'staff', 'user'):
            self.assertEqual(self.login(role).status_code, 200)
            self.assertEqual(self.client.get('/api/who').json['user']['role'], role)
            for target in ('admin', 'staff', 'user'):
                self.assertEqual(self.client.get('/api/' + target + '/dashboard').status_code,
                                 200 if role == target else 403)
        self.client.post('/api/logout')
        self.assertEqual(self.client.get('/api/who').status_code, 401)

    def test_admin_creates_staff_with_csrf(self):
        payload = dict(username='Guide', email='guide@test.com', password='password', contact_number='1234567890')
        self.login('admin')
        self.assertEqual(self.client.post('/api/admin/staffs', json=payload).status_code, 401)
        token = self.client.get_cookie('csrf_access_token').value
        self.assertEqual(self.client.post('/api/admin/staffs', json=payload,
            headers={'X-CSRF-TOKEN': token}).status_code, 201)
        self.assertIsNotNone(User.query.filter_by(email='guide@test.com').one().staff_profile)
        self.login('user')
        token = self.client.get_cookie('csrf_access_token').value
        self.assertEqual(self.client.post('/api/admin/staffs', json=payload,
            headers={'X-CSRF-TOKEN': token}).status_code, 403)
        self.assertEqual(self.client.post('/api/login', json={
            'email': 'guide@test.com', 'password': 'password'}).status_code, 200)

    def test_blacklisted_account_and_wrong_password(self):
        self.assertEqual(self.client.post('/api/login', json={
            'email': 'user@test.com', 'password': 'wrong'}).status_code, 401)
        self.login('user')
        User.query.filter_by(role='user').one().approval_status = 'blacklist'
        db.session.commit()
        self.assertEqual(self.client.get('/api/user/dashboard').status_code, 403)
        self.assertEqual(self.login('user').status_code, 403)


if __name__ == '__main__':
    unittest.main()
