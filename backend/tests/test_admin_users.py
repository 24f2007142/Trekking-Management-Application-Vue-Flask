import unittest
from datetime import date

from flask import Flask
from flask_jwt_extended import JWTManager, create_access_token
from werkzeug.security import generate_password_hash

from db import db
from models import User, Trek, Booking
from routes.admin import admin_bp


class AdminUserRoutesTest(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.config.update(
            TESTING=True,
            SQLALCHEMY_DATABASE_URI='sqlite://',
            JWT_SECRET_KEY='isolated-test-secret-key-at-least-32-characters',
            JWT_TOKEN_LOCATION=['headers'],
        )
        db.init_app(self.app)
        JWTManager(self.app)
        self.app.register_blueprint(admin_bp, url_prefix='/api/admin')
        self.context = self.app.app_context()
        self.context.push()
        db.create_all()
        self.admin = User(username='Admin', email='admin@example.com',
                          password=generate_password_hash('test'), role='admin',
                          approval_status='approved')
        self.user = User(username='Alice', email='alice@example.com',
                         password='unused', role='user', approval_status='approved')
        self.staff = User(username='Alice Guide', email='guide@example.com',
                          password='unused', role='staff', approval_status='approved')
        db.session.add_all([self.admin, self.user, self.staff])
        db.session.commit()
        self.client = self.app.test_client()
        self.headers = self.auth(self.admin)
        self.url = f'/api/admin/users/{self.user.id}'

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def auth(self, user):
        return {'Authorization': 'Bearer ' + create_access_token(identity=str(user.id))}

    def test_admin_display_name_only(self):
        url = '/api/admin/profile'
        old_password = self.admin.password
        self.assertEqual(self.client.get(url).status_code, 401)
        self.assertEqual(self.client.put(url, headers=self.auth(self.user),
                                        json={'username': 'Changed'}).status_code, 403)
        for payload in ({'username': ' '}, {'username': 123}, {'username': 'x' * 101},
                        {'username': 'New', 'role': 'user'}, {'username': 'New', 'email': 'new@test'}):
            self.assertEqual(self.client.put(url, headers=self.headers, json=payload).status_code, 400)
        response = self.client.put(url, headers=self.headers, json={'username': ' New Admin '})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.client.get(url, headers=self.headers).json['data']['username'], 'New Admin')
        self.assertEqual(self.admin.email, 'admin@example.com')
        self.assertEqual(self.admin.password, old_password)
        self.assertEqual(self.admin.role, 'admin')
        self.assertEqual(User.query.filter_by(role='admin').first().id, self.admin.id)

    def test_admin_access_required(self):
        routes = [('GET', '/api/admin/users', None), ('GET', self.url, None),
                  ('PATCH', self.url + '/status', {'approval_status': 'blacklist'}),
                  ('GET', self.url + '/bookings', None)]
        for method, url, payload in routes:
            with self.subTest(method=method, url=url):
                self.assertEqual(self.client.open(url, method=method, json=payload).status_code, 401)
                self.assertEqual(self.client.open(url, method=method, json=payload,
                                                 headers=self.auth(self.user)).status_code, 403)
        self.admin.approval_status = 'blacklist'
        db.session.commit()
        self.assertEqual(self.client.get('/api/admin/users', headers=self.headers).status_code, 403)

    def test_listing_search_and_status_filter(self):
        for query in ('', '?search=ALIce', f'?search={self.user.id}'):
            response = self.client.get('/api/admin/users' + query, headers=self.headers)
            self.assertEqual(response.status_code, 200)
            self.assertEqual([u['id'] for u in response.json['data']], [self.user.id])
            self.assertNotIn('password', response.json['data'][0])
        for query in ('?search=missing', '?search=%25', '?approval_status=blacklist'):
            self.assertEqual(self.client.get('/api/admin/users' + query,
                                            headers=self.headers).json['data'], [])
        self.assertEqual(self.client.get('/api/admin/users?approval_status=bad',
                                         headers=self.headers).status_code, 400)

    def test_role_boundaries_and_missing_users(self):
        for user_id in (self.admin.id, self.staff.id, 9999):
            url = f'/api/admin/users/{user_id}'
            for method, suffix in [('GET', ''), ('PATCH', '/status'),
                                   ('GET', '/bookings')]:
                response = self.client.open(url + suffix, method=method,
                                            headers=self.headers, json={})
                self.assertEqual(response.status_code, 404)

    def test_admin_cannot_edit_user_profile(self):
        response = self.client.put(self.url, headers=self.headers,
                                   json={'username': 'Changed', 'email': 'new@example.com'})
        self.assertEqual(response.status_code, 405)
        self.assertEqual(db.session.get(User, self.user.id).username, 'Alice')

    def test_blacklist_reactivation_and_booking_history(self):
        trek = Trek(trek_name='Hill Trek', location='Hills', difficulty='easy', duration=1,
                    start_date=date(2026, 1, 1), end_date=date(2026, 1, 1),
                    total_slots=10, booked_slots=1, price=100, trek_status='completed')
        db.session.add(trek)
        db.session.flush()
        booking = Booking(user_id=self.user.id, trek_id=trek.id,
                          booking_date=date(2025, 12, 1), status='confirmed', slots_booked=1)
        other = User(username='Other', email='other@example.com', password='unused', role='user')
        db.session.add_all([booking, other])
        db.session.flush()
        db.session.add(Booking(user_id=other.id, trek_id=trek.id,
                               booking_date=date(2025, 12, 2), status='cancelled'))
        db.session.commit()
        for status in ('blacklist', 'blacklist', 'approved'):
            response = self.client.patch(self.url + '/status', headers=self.headers,
                                         json={'approval_status': status})
            self.assertEqual(response.status_code, 200)
            self.assertEqual(db.session.get(User, self.user.id).approval_status, status)
            self.assertEqual(db.session.get(Booking, booking.id).status, 'confirmed')
        self.assertEqual(self.client.patch(self.url + '/status', headers=self.headers,
                                          json={'approval_status': 'pending'}).status_code, 400)
        response = self.client.get(self.url + '/bookings?trek_status=completed&status=confirmed',
                                   headers=self.headers)
        self.assertEqual(response.status_code, 200)
        self.assertEqual([b['id'] for b in response.json['data']], [booking.id])
        self.assertEqual(response.json['data'][0]['trek']['start_date'], '2026-01-01')
        self.assertEqual(self.client.get(self.url + '/bookings?trek_status=upcoming',
                                        headers=self.headers).json['data'], [])
        for query in ('?status=bad', '?trek_status=bad'):
            self.assertEqual(self.client.get(self.url + '/bookings' + query,
                                            headers=self.headers).status_code, 400)


    def test_trek_create_edit_search_delete(self):
        payload = dict(trek_name='Valley Walk', location='Valley', difficulty='easy',
                       duration=1, start_date='2027-02-01', end_date='2027-02-01',
                       total_slots=10, price=100)
        result = self.client.post('/api/admin/treks', headers=self.headers, json=payload)
        self.assertEqual(result.status_code, 201)
        trek_id = result.json['trek_id']
        url = f'/api/admin/treks/{trek_id}'
        self.assertEqual(self.client.patch(url + '/approve', headers=self.headers).status_code, 200)
        payload.update(trek_name='Updated Valley', bookings_open=True, description='A walk')
        self.assertEqual(self.client.put(url, headers=self.headers, json=payload).status_code, 200)
        for search in ('Updated', str(trek_id), f'T{trek_id:03d}'):
            result = self.client.get('/api/admin/treks', headers=self.headers, query_string={'search': search})
            self.assertEqual(len(result.json['data']), 1)
        self.assertEqual(self.client.delete(url, headers=self.headers).status_code, 200)
        self.assertIsNone(db.session.get(Trek, trek_id))

    def test_staff_assignment_and_blacklisting(self):
        from models import Staff, StaffTrek
        payload = dict(username='New Guide', email='newguide@test.com', password='test-password',
                       contact_number='1234567890')
        result = self.client.post('/api/admin/staffs', headers=self.headers, json=payload)
        self.assertEqual(result.status_code, 201)
        guide = User.query.filter_by(email=payload['email']).one()
        for search in ('New Guide', str(guide.id)):
            result = self.client.get('/api/admin/staffs', headers=self.headers, query_string={'search': search})
            self.assertTrue(any(item['user_id'] == guide.id for item in result.json['data']))
        trek = Trek(trek_name='Hill', location='Hills', difficulty='easy', duration=1,
                    start_date=date(2027, 2, 1), end_date=date(2027, 2, 1),
                    total_slots=10, price=100)
        db.session.add(trek)
        db.session.commit()
        url = f'/api/admin/treks/{trek.id}/staff'
        assignment = self.client.post(url, headers=self.headers, json={'staff_id': guide.staff_profile.id})
        self.assertEqual(assignment.status_code, 201)
        self.assertEqual(self.client.post(url, headers=self.headers,
            json={'staff_id': guide.staff_profile.id}).status_code, 409)
        self.assertEqual(self.client.patch(f'/api/admin/staffs/{guide.id}/status',
            headers=self.headers, json={'approval_status': 'blacklist'}).status_code, 200)
        self.assertEqual(StaffTrek.query.one().status, 'cancelled')
        self.assertEqual(self.client.post(url, headers=self.headers,
            json={'staff_id': guide.staff_profile.id}).status_code, 403)

    def test_dashboard_reports_and_all_bookings_are_admin_only(self):
        for path in ('dashboard', 'reports', 'all-bookings', 'treks', 'staffs'):
            url = '/api/admin/' + path
            self.assertEqual(self.client.get(url).status_code, 401)
            self.assertEqual(self.client.get(url, headers=self.auth(self.staff)).status_code, 403)
            self.assertEqual(self.client.get(url, headers=self.headers).status_code, 200)
        data = self.client.get('/api/admin/dashboard', headers=self.headers).json['data']
        self.assertEqual(data['total_users'], 1)
        self.assertEqual(data['total_staffs'], 1)
        self.assertEqual(data['total_treks'], 0)


if __name__ == '__main__':
    unittest.main()
