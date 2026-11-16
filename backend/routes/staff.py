from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy.exc import SQLAlchemyError
from db import db
from models import User, Staff, Trek, Booking, StaffTrek

from functools import wraps
from datetime import date

staff_bp = Blueprint('staff', __name__)

def staff_required(fn):

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):

        user_id = get_jwt_identity()
        staff = User.query.get(int(user_id))

        if (
            not staff
            or staff.role != 'staff'
            or staff.approval_status != 'approved'
        ):
            return jsonify({
                'message': 'Staff access required'
            }), 403

        return fn(*args, **kwargs)

    return wrapper

@staff_bp.route('/dashboard', methods=['GET'])
@staff_required
def staff_dashboard():

    user_id = get_jwt_identity()
    staff = Staff.query.filter_by(user_id=int(user_id)).first()

    if not staff:
        return jsonify({'message': 'Staff profile not found'}), 404

    staff_name = staff.user.username

    assignments = StaffTrek.query.filter(
        StaffTrek.staff_id == staff.id,
        StaffTrek.status != 'cancelled').all()


    total_treks = len(assignments)
    upcoming_treks_list = []
    total_participants = 0

    for assignment in assignments:

        total_participants += assignment.trek.booked_slots

        if assignment.trek.trek_status == 'upcoming':
            upcoming_treks_list.append({
                'trek_id': assignment.trek.id,
                'trek_name': assignment.trek.trek_name,
                'location': assignment.trek.location,
                'difficulty': assignment.trek.difficulty,
                'duration': assignment.trek.duration,
                'start_date': assignment.trek.start_date.isoformat(),
                'end_date': assignment.trek.end_date.isoformat(),
                'total_slots': assignment.trek.total_slots,
                'booked_slots':assignment.trek.booked_slots,
                'available_slots': assignment.trek.total_slots - assignment.trek.booked_slots,
                'bookings_open': assignment.trek.bookings_open,
                'trek_status': assignment.trek.trek_status,
                'assignment_status': assignment.status
                })
    upcoming_treks_count = len(upcoming_treks_list)


    return jsonify(
        {
            'data':
            {

                'staff_name': staff_name,
                'total_trek': total_treks,
                'upcoming_treks_count': upcoming_treks_count,
                'total_participants': total_participants,
                'upcoming_treks_list' : upcoming_treks_list
            }
        }
    ), 200


@staff_bp.route('/treks', methods=['GET'])
@staff_required
def get_assigned_treks():

    user_id = get_jwt_identity()
    staff = Staff.query.filter_by(user_id=int(user_id)).first()

    if not staff:
        return jsonify({'message': 'Staff profile not found'}), 404

    assignments = StaffTrek.query.filter(
        StaffTrek.staff_id == staff.id
    ).order_by(StaffTrek.id.desc()).all()

    treks = []

    for assignment in assignments:
        trek = assignment.trek
        treks.append({
            'trek_id': trek.id,
            'display_id': trek.display_id,
            'trek_name': trek.trek_name,
            'location': trek.location,
            'difficulty': trek.difficulty,
            'duration': trek.duration,
            'start_date': trek.start_date.isoformat(),
            'end_date': trek.end_date.isoformat(),
            'total_slots': trek.total_slots,
            'booked_slots': trek.booked_slots,
            'available_slots': trek.total_slots - trek.booked_slots,
            'bookings_open': trek.bookings_open,
            'trek_status': trek.trek_status,
            'assignment_status': assignment.status
        })

    return jsonify({'data': treks}), 200


@staff_bp.route('/treks/<int:trek_id>', methods=['GET'])
@staff_required
def get_trek_info(trek_id):
    user_id = get_jwt_identity()
    staff = Staff.query.filter_by(user_id=int(user_id)).first()

    if not staff:
        return jsonify({'message': 'Staff profile not found'}), 404

    assignment = StaffTrek.query.filter(
        StaffTrek.staff_id == staff.id,
        StaffTrek.trek_id == trek_id,
        StaffTrek.status.in_(('assigned', 'completed'))
    ).first()

    if not assignment:
        return jsonify({'message': 'Non-cancelled trek assignment required'}), 403

    trek = assignment.trek

    return jsonify({'data': {
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
        'trek_status': trek.trek_status,
        'assignment_status': assignment.status
    }}), 200


@staff_bp.route('/treks/<int:trek_id>/slots', methods=['PATCH'])
@staff_required
def update_trek_slots(trek_id):
    user_id = get_jwt_identity()
    staff = Staff.query.filter_by(user_id=int(user_id)).first()

    if not staff:
        return jsonify({'message': 'Staff profile not found'}), 404

    assignment = StaffTrek.query.filter_by(
        staff_id=staff.id, trek_id=trek_id, status='assigned'
    ).first()

    if not assignment:
        return jsonify({'message': 'Active trek assignment required'}), 403

    trek = assignment.trek

    if trek.trek_status not in ('approved', 'upcoming'):
        return jsonify({'message': 'Only upcoming treks can be managed'}), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({'message': 'Invalid request data'}), 400

    total_slots = data.get('total_slots')

    if type(total_slots) is not int or total_slots <= 0:
        return jsonify({'message': 'Total slots must be a positive integer'}), 400

    if total_slots < trek.booked_slots:
        return jsonify({'message': 'Total slots cannot be less than booked slots'}), 400

    try:
        trek.total_slots = total_slots
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'message': 'Failed to update trek slots'}), 500

    return jsonify({
        'message': 'Trek slots updated successfully',
        'data': {
            'trek_id': trek.id,
            'total_slots': trek.total_slots,
            'booked_slots': trek.booked_slots,
            'available_slots': trek.total_slots - trek.booked_slots
        }
    }), 200



@staff_bp.route('/treks/<int:trek_id>/bookings-status', methods=['PATCH'])
@staff_required
def update_bookings_status(trek_id):
    user_id = get_jwt_identity()
    staff = Staff.query.filter_by(user_id=int(user_id)).first()

    if not staff:
        return jsonify({'message': 'Staff profile not found'}), 404

    assignment = StaffTrek.query.filter_by(
        staff_id=staff.id, trek_id=trek_id, status='assigned'
    ).first()

    if not assignment:
        return jsonify({'message': 'Active trek assignment required'}), 403

    trek = assignment.trek

    if trek.trek_status not in ('approved', 'upcoming'):
        return jsonify({'message': 'Only upcoming treks can change booking status'}), 403

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({'message': 'Invalid request data'}), 400

    bookings_open = data.get('bookings_open')

    if not isinstance(bookings_open, bool):
        return jsonify({'message': 'bookings_open must be true or false'}), 400

    try:
        trek.bookings_open = bookings_open
        if bookings_open:
            trek.trek_status = 'upcoming'
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'message': 'Failed to update booking status'}), 500

    return jsonify({
        'message': 'Booking status updated successfully',
        'data': {
            'trek_id': trek.id,
            'bookings_open': trek.bookings_open,
            'trek_status': trek.trek_status
        }
    }), 200



@staff_bp.route('/treks/<int:trek_id>/status', methods=['PATCH'])
@staff_required
def update_trek_status(trek_id):
    user_id = get_jwt_identity()
    staff = Staff.query.filter_by(user_id=int(user_id)).first()

    if not staff:
        return jsonify({'message': 'Staff profile not found'}), 404

    assignment = StaffTrek.query.filter(
        StaffTrek.staff_id == staff.id,
        StaffTrek.trek_id == trek_id,
        StaffTrek.status.in_(('assigned', 'completed'))
    ).first()

    if not assignment:
        return jsonify({'message': 'Non-cancelled trek assignment required'}), 403

    trek = assignment.trek
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({'message': 'Invalid request data'}), 400

    status = data.get('trek_status')

    if status not in ('upcoming', 'ongoing', 'completed', 'cancelled'):
        return jsonify({'message': 'Invalid trek status'}), 400

    transitions = {
        'pending': ('cancelled',),
        'approved': ('cancelled',),
        'upcoming': ('ongoing', 'completed', 'cancelled'),
        'ongoing': ('completed', 'cancelled'),
        'completed': (), 'cancelled': (),
    }
    if status != trek.trek_status and status not in transitions.get(trek.trek_status, ()):
        return jsonify({'message': 'Invalid trek status transition'}), 409

    try:
        trek.trek_status = status
        if status == 'completed':
            for booking in trek.booking:
                if booking.status == 'confirmed':
                    booking.status = 'completed'
        elif status == 'cancelled':
            for booking in trek.booking:
                if booking.status in ('pending', 'confirmed'):
                    booking.status = 'cancelled'
                    booking.payment_status = 'refund initiated'
                    booking.removed_by_staff_name = staff.user.username
            trek.booked_slots = 0
        if status != 'upcoming':
            trek.bookings_open = False

        assignments = StaffTrek.query.filter(
            StaffTrek.trek_id == trek.id,
            StaffTrek.status.in_(('assigned', 'completed'))
        ).all()
        for staff_assignment in assignments:
            staff_assignment.status = status if status in ('completed', 'cancelled') else 'assigned'

        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'message': 'Failed to update trek status'}), 500

    return jsonify({
        'message': 'Trek status updated successfully',
        'data': {
            'trek_id': trek.id,
            'trek_status': trek.trek_status,
            'bookings_open': trek.bookings_open,
            'assignment_status': assignment.status
        }
    }), 200


@staff_bp.route('/participants', methods=['GET'])
@staff_required
def get_participants():
    return jsonify({'message': 'Select a trek to view participants'}), 400


@staff_bp.route('/treks/<int:trek_id>/participants', methods=['GET'])
@staff_required
def get_trek_participants(trek_id):
    user_id = get_jwt_identity()
    staff = Staff.query.filter_by(user_id=int(user_id)).first()

    if not staff:
        return jsonify({'message': 'Staff profile not found'}), 404

    assignment = StaffTrek.query.filter(
        StaffTrek.staff_id == staff.id,
        StaffTrek.trek_id == trek_id,
        StaffTrek.status.in_(('assigned', 'completed'))
    ).first()

    if not assignment:
        return jsonify({'message': 'You do not have access to this trek'}), 403

    search = request.args.get('search', '').strip().lower()
    bookings = Booking.query.filter_by(trek_id=trek_id).order_by(Booking.id.desc()).all()
    participants = []
    total_confirmed = 0

    for booking in bookings:
        if booking.status in ('confirmed', 'completed'):
            total_confirmed += booking.slots_booked

        if search:
            name_matches = search in booking.user.username.lower()
            id_matches = search == str(booking.id)
            if not name_matches and not id_matches:
                continue

        participants.append({
            'booking_id': booking.id,
            'username': booking.user.username,
            'email': booking.user.email,
            'slots_booked': booking.slots_booked,
            'booking_status': booking.status,
            'payment_status': booking.payment_status,
            'can_remove': assignment.status == 'assigned' and trek_id == booking.trek_id
                and assignment.trek.trek_status in ('upcoming', 'ongoing')
                and booking.status == 'confirmed'
        })

    return jsonify({
        'data': participants,
        'total_confirmed': total_confirmed
    }), 200


@staff_bp.route('/treks/<int:trek_id>/participants/<int:booking_id>', methods=['PATCH'])
@staff_required
def update_participant(trek_id, booking_id):
    staff = Staff.query.filter_by(user_id=int(get_jwt_identity())).first()
    if not staff:
        return jsonify({'message': 'Staff profile not found'}), 404
    assignment = StaffTrek.query.filter_by(
        staff_id=staff.id, trek_id=trek_id, status='assigned'
    ).first()
    if not assignment:
        return jsonify({'message': 'Active trek assignment required'}), 403
    if assignment.trek.trek_status not in ('upcoming', 'ongoing'):
        return jsonify({'message': 'This trek no longer accepts participant changes'}), 409
    data = request.get_json(silent=True)
    if not isinstance(data, dict) or data.get('action') != 'remove':
        return jsonify({'message': 'Use the remove action'}), 400
    booking = Booking.query.filter_by(id=booking_id, trek_id=trek_id).first()
    if not booking:
        return jsonify({'message': 'Booking not found'}), 404
    try:
        changed = Booking.query.filter_by(id=booking.id, status='confirmed').update({
            Booking.status: 'cancelled', Booking.payment_status: 'refund initiated',
            Booking.removed_by_staff_name: staff.user.username,
        }, synchronize_session=False)
        if not changed:
            db.session.rollback()
            return jsonify({'message': 'Only confirmed participants can be removed'}), 409
        Trek.query.filter_by(id=trek_id).update({
            Trek.booked_slots: Trek.booked_slots - booking.slots_booked
        }, synchronize_session=False)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'message': 'Could not remove participant'}), 500
    return jsonify({'message': 'Participant removed. Refund initiated.'}), 200


@staff_bp.route('/profile', methods=['GET'])
@staff_required
def get_staff_profile():
    staff = Staff.query.filter_by(user_id=int(get_jwt_identity())).first()
    if not staff:
        return jsonify({'message': 'Staff profile not found'}), 404

    return jsonify({'data': {
        'username': staff.user.username,
        'email': staff.user.email,
        'contact_number': staff.contact_number,
        'next_available_date': staff.next_available_date.isoformat() if staff.next_available_date else None
    }}), 200


@staff_bp.route('/profile', methods=['PUT'])
@staff_required
def update_staff_profile():
    staff = Staff.query.filter_by(user_id=int(get_jwt_identity())).first()
    if not staff:
        return jsonify({'message': 'Staff profile not found'}), 404

    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify({'message': 'Invalid request data'}), 400

    username = data.get('username')
    contact_number = data.get('contact_number')
    available_date = data.get('next_available_date')

    if not isinstance(username, str) or not 1 <= len(username.strip()) <= 100:
        return jsonify({'message': 'Name must contain 1 to 100 characters'}), 400

    if not isinstance(contact_number, str) or not 1 <= len(contact_number.strip()) <= 15:
        return jsonify({'message': 'Contact number must contain 1 to 15 characters'}), 400

    contact_number = contact_number.strip()
    if not any(character.isdigit() for character in contact_number):
        return jsonify({'message': 'Enter a valid contact number'}), 400
    for character in contact_number:
        if character not in '0123456789+ -()':
            return jsonify({'message': 'Enter a valid contact number'}), 400

    if available_date is None or available_date == '':
        available_date = None
    else:
        try:
            available_date = date.fromisoformat(available_date)
        except (ValueError, TypeError):
            return jsonify({'message': 'Enter a valid availability date'}), 400

    try:
        staff.user.username = username.strip()
        staff.contact_number = contact_number
        staff.next_available_date = available_date
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'message': 'Failed to update profile'}), 500

    return jsonify({'message': 'Profile updated successfully'}), 200
