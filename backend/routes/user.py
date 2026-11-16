from functools import wraps
from datetime import date

from flask import Blueprint, jsonify, request
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from flask_jwt_extended import jwt_required, get_jwt_identity
from db import db
from models import User, Booking, Trek


user_bp = Blueprint('user', __name__)


def user_required(fn):
    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):
        user = db.session.get(User, int(get_jwt_identity()))

        if not user or user.role != 'user' or user.approval_status != 'approved':
            return jsonify({'message': 'User access required'}), 403

        return fn(*args, **kwargs)

    return wrapper


@user_bp.route('/dashboard', methods=['GET'])
@user_required
def user_dashboard():
    user_id = int(get_jwt_identity())
    user = User.query.get(user_id)
    bookings = Booking.query.filter_by(
        user_id = user_id
    ).order_by(Booking.id.desc()).all()

    upcoming_treks_list = []
    completed_trek_ids = set()

    for booking in bookings:
        trek = booking.trek

        if booking.status == 'cancelled':
            continue

        if trek.trek_status == 'completed' and booking.status in ('confirmed', 'completed'):
            completed_trek_ids.add(trek.id)

        if trek.trek_status == 'upcoming':
            upcoming_treks_list.append({
                'booking_id': booking.id,
                'trek_id': trek.id,
                'trek_name': trek.trek_name,
                'location': trek.location,
                'start_date': trek.start_date.isoformat(),
                'end_date': trek.end_date.isoformat(),
                'slots_booked': booking.slots_booked,
                'booking_status': booking.status,
                'payment_status': booking.payment_status,
                'trek_status': trek.trek_status
            })

    booked_trek = []

    for booking in bookings:
          if booking.status != 'cancelled':
            booked_trek.append(booking.trek_id)

    recent_treks = Trek.query.filter(
        Trek.trek_status == 'upcoming',
        Trek.booked_slots < Trek.total_slots
    ).order_by(Trek.id.desc()).limit(5).all()

    recent_treks_list = []

    for trek in recent_treks:

        if trek.bookings_open:

            recent_treks_list.append({
                'trek_id': trek.id,
                'trek_name': trek.trek_name,
                'location': trek.location,
                'difficulty': trek.difficulty,
                'duration': trek.duration,
                'start_date': trek.start_date.isoformat(),
                'price': trek.price,
                'available_slots': trek.total_slots - trek.booked_slots,
                'already_booked': True if trek.id in booked_trek else False
            })

    return jsonify({'data': {
        'user_name': user.username,
        'notifications': [
            {'booking_id': b.id, 'trek_name': b.trek.trek_name,
             'staff_name': b.removed_by_staff_name, 'payment_status': b.payment_status}
            for b in bookings if b.removed_by_staff_name
        ],
        'recent_treks_list': recent_treks_list,
        'total_bookings': len(bookings),
        'upcoming_treks_count': len({trek['trek_id'] for trek in upcoming_treks_list}),
        'completed_treks_count': len(completed_trek_ids),
        'upcoming_treks_list': upcoming_treks_list
    }}), 200


@user_bp.route('/treks', methods=['GET'])
@user_required
def get_available_treks():
    user_id = int(get_jwt_identity())

    bookings = Booking.query.filter(
        Booking.user_id == user_id, Booking.status != 'cancelled'
    ).all()
    bookings_by_trek = {booking.trek_id: booking for booking in bookings}
    treks = Trek.query.filter(Trek.trek_status == "upcoming").all()

    upcoming_treks = []

    for trek in treks:
        booking = bookings_by_trek.get(trek.id)
        if (
            trek.booked_slots >= trek.total_slots
            or not trek.bookings_open
        ) and not booking:
            continue

        upcoming_treks.append({
            'booking_id': booking.id if booking else None,
            'already_booked': booking is not None,
            'slots_booked': booking.slots_booked if booking else 0,
            'trek_id': trek.id,
            'display_id': trek.display_id,
            'trek_name': trek.trek_name,
            'location': trek.location,
            'difficulty': trek.difficulty,
            'duration': trek.duration,
            'start_date': trek.start_date.isoformat(),
            'end_date': trek.end_date.isoformat(),
            'description': trek.description,
            'price': trek.price,
            'total_slots': trek.total_slots,
            'booked_slots': trek.booked_slots,
            'available_slots': trek.total_slots - trek.booked_slots,
            'bookings_open': trek.bookings_open,
            'trek_status': trek.trek_status
        })

    data = {'data': {'upcoming_treks': upcoming_treks}}
    return jsonify(data), 200


@user_bp.route('/treks/<int:trek_id>', methods=['GET'])
@user_required
def get_trek_details(trek_id):

    trek = Trek.query.get(trek_id)

    if not trek:
        return jsonify({'message': 'Trek not found'}), 404

    data = {'data': {
        'trek_id': trek.id,
        'display_id': trek.display_id,
        'trek_name': trek.trek_name,
        'location': trek.location,
        'difficulty': trek.difficulty,
        'duration': trek.duration,
        'start_date': trek.start_date.isoformat(),
        'end_date': trek.end_date.isoformat(),
        'description': trek.description,
        'price': trek.price,
        'total_slots': trek.total_slots,
        'booked_slots': trek.booked_slots,
        'available_slots': trek.total_slots - trek.booked_slots,
        'bookings_open': trek.bookings_open,
        'trek_status': trek.trek_status
    }}
    return jsonify(data), 200


@user_bp.route('/treks/<int:trek_id>/book', methods=['POST'])
@user_required
def book_trek(trek_id):
    user_id = int(get_jwt_identity())
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({'message': 'Invalid request data'}), 400

    slots_booked = data.get('slots_booked')
    if type(slots_booked) is not int or slots_booked <= 0:
        return jsonify({'message': 'Slots booked must be a positive integer'}), 400

    try:
        trek = Trek.query.get(trek_id)
        if not trek:
            return jsonify({'message': 'Trek not found'}), 404

        existing_booking = Booking.query.filter(
            Booking.trek_id == trek_id,
            Booking.user_id == user_id,
            Booking.status != 'cancelled'
        )

        if existing_booking.first():
            return jsonify({'message': 'Trek already booked'}), 409

        if trek.trek_status != 'upcoming' or not trek.bookings_open:
            return jsonify({'message': 'Bookings are closed for this trek'}), 409

        if slots_booked > trek.total_slots - trek.booked_slots:
            return jsonify({'message': 'Not enough available slots'}), 409

        # One conditional UPDATE checks capacity and duplicates while reserving slots.
        duplicate = db.session.query(Booking.id).filter(
            Booking.trek_id == trek_id, Booking.user_id == user_id,
            Booking.status != 'cancelled'
        ).exists()
        reserved = Trek.query.filter(
            Trek.id == trek_id, Trek.trek_status == 'upcoming',
            Trek.bookings_open.is_(True),
            Trek.booked_slots + slots_booked <= Trek.total_slots,
            ~duplicate,
        ).update({Trek.booked_slots: Trek.booked_slots + slots_booked},
                 synchronize_session=False)
        if reserved != 1:
            db.session.rollback()
            return jsonify({'message': 'Trek is full, closed, or already booked'}), 409

        book = Booking(
            user_id=user_id,
            trek_id=trek_id,
            status='confirmed',
            slots_booked=slots_booked,
            booking_date=date.today()
        )
        db.session.add(book)
        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'message': 'Failed to book trek'}), 500

    return jsonify({
        'message': 'Trek booked successfully'
    }), 201


@user_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@user_required
def cancel_booking(booking_id):
    user_id = int(get_jwt_identity())

    try:
        booking = Booking.query.filter_by(id=booking_id, user_id=user_id).first()

        if not booking:
            return jsonify({'message': 'Booking not found'}), 404

        if booking.status == 'cancelled':
            return jsonify({'message': 'Booking already cancelled'}), 409

        trek = booking.trek

        if trek.trek_status != 'upcoming':
            return jsonify({'message': 'Only upcoming trek bookings can be cancelled'}), 409

        if booking.status == 'confirmed':
            if trek.booked_slots < booking.slots_booked:
                return jsonify({'message': 'Invalid booked slot count'}), 409

            trek.booked_slots -= booking.slots_booked

        booking.status = 'cancelled'
        booking.payment_status = 'refund finished'
        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'message': 'Failed to cancel booking'}), 500

    return jsonify({'message': 'Booking cancelled successfully'}), 200


@user_bp.route('/bookings', methods=['GET'])
@user_required
def get_user_bookings():
    user_id = int(get_jwt_identity())
    bookings = Booking.query.filter_by(user_id=user_id).order_by(Booking.id.desc()).all()
    data = []

    for booking in bookings:
        trek = booking.trek
        data.append({
            'booking_id': booking.id,
            'booking_date': booking.booking_date.isoformat(),
            'booking_status': booking.status,
            'payment_status': booking.payment_status,
            'slots_booked': booking.slots_booked,
            'trek_id': trek.id,
            'trek_name': trek.trek_name,
            'location': trek.location,
            'start_date': trek.start_date.isoformat(),
            'end_date': trek.end_date.isoformat(),
            'bookings_open': trek.bookings_open,
            'trek_status': trek.trek_status
        })

    return jsonify({'data': data}), 200


@user_bp.route('/history', methods=['GET'])
@user_required
def get_trekking_history():
    user_id = int(get_jwt_identity())
    bookings = Booking.query.filter(
        Booking.user_id == user_id
    ).order_by(Booking.id.desc()).all()
    history = []

    for booking in bookings:
        trek = booking.trek
        if booking.status != 'cancelled' and trek.trek_status != 'completed':
            continue

        history.append({
            'booking_id': booking.id,
            'booking_date': booking.booking_date.isoformat(),
            'booking_status': booking.status,
            'payment_status': booking.payment_status,
            'slots_booked': booking.slots_booked,
            'trek_id': trek.id,
            'trek_name': trek.trek_name,
            'location': trek.location,
            'difficulty': trek.difficulty,
            'duration': trek.duration,
            'start_date': trek.start_date.isoformat(),
            'end_date': trek.end_date.isoformat(),
            'bookings_open': trek.bookings_open,
            'trek_status': trek.trek_status
        })

    return jsonify({'data': history}), 200


@user_bp.route('/profile', methods=['GET'])
@user_required
def get_user_profile():
    user = db.session.get(User, int(get_jwt_identity()))

    return jsonify({'data': {
        'user_id': user.id,
        'username': user.username,
        'email': user.email
    }}), 200


@user_bp.route('/profile', methods=['PUT'])
@user_required
def update_user_profile():
    user = db.session.get(User, int(get_jwt_identity()))
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({'message': 'Invalid request data'}), 400

    if set(data) - {'username', 'email'}:
        return jsonify({'message': 'Only username and email can be updated'}), 400

    username = data.get('username')
    email = data.get('email')

    if not isinstance(username, str) or not 1 <= len(username.strip()) <= 100:
        return jsonify({'message': 'Name must contain 1 to 100 characters'}), 400

    if not isinstance(email, str):
        return jsonify({'message': 'Enter a valid email address'}), 400

    email = email.strip().lower()
    if (
        not 1 <= len(email) <= 100
        or email.count('@') != 1
    ):
        return jsonify({'message': 'Enter a valid email address'}), 400


    existing_user = User.query.filter(User.email == email,
        User.id != user.id
    ).first()
    if existing_user:
        return jsonify({'message': 'Email already exists'}), 409

    try:
        user.username = username.strip()
        user.email = email
        db.session.commit()
    except IntegrityError:
        db.session.rollback()
        return jsonify({'message': 'Email already exists'}), 409
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'message': 'Failed to update profile'}), 500

    return jsonify({
        'message': 'Profile updated successfully',
        'data': {
            'user_id': user.id,
            'username': user.username,
            'email': user.email
        }
    }), 200


from tasks import export_trekking_history
from kombu.exceptions import OperationalError

@user_bp.route('/history/export', methods=['POST'])
@user_required
def request_history_export():
    user_id = int(get_jwt_identity())

    try:
        task = export_trekking_history.delay(user_id)
    except OperationalError:
        return jsonify({
            'message': 'Export service is unavailable. Please try again later.'
        }), 503

    return jsonify({
        'message': 'Export requested. You will receive an email when it is ready.',
        'task_id': task.id,
    }), 202
