from flask import jsonify, request, Blueprint
from flask_jwt_extended import jwt_required, get_jwt_identity
from models import User, Staff, Trek, Booking, StaffTrek
from datetime import date
from werkzeug.security import generate_password_hash
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy import or_, func
import re

from db import db
from cache import get_cached_data, cache_data, clear_trek_cache

admin_bp = Blueprint('admin', __name__)

from functools import wraps

def admin_required(fn):

    @wraps(fn)
    @jwt_required()
    def wrapper(*args, **kwargs):

        user_id = get_jwt_identity()
        admin = db.session.get(User, int(user_id))

        if (
            not admin
            or admin.role != 'admin'
            or admin.approval_status != 'approved'
        ):
            return jsonify({
                'message': 'Admin access required'
            }), 403

        return fn(*args, **kwargs)

    return wrapper

def staff_to_dict(staff):

    profile = staff.staff_profile

    return {
        'user_id': staff.id,
        'staff_id': profile.id if profile else None,
        'username': staff.username,
        'email': staff.email,
        'contact_number': profile.contact_number if profile else None,
        'next_available_date': (
            profile.next_available_date.isoformat()
            if profile and profile.next_available_date
            else None
        ),
        'approval_status': staff.approval_status
    }

def validate_staff_data(data):

    username = data.get('username')
    email = data.get('email')
    contact_number = data.get('contact_number')

    if (
        not isinstance(username, str)
        or not isinstance(email, str)
        or not isinstance(contact_number, str)
    ):
        return 'Invalid username, email or contact number'

    username = username.strip()
    email = email.strip().lower()
    contact_number = contact_number.strip()

    if not username or not email or not contact_number:
        return 'Username, email and contact number cannot be empty'

    return None

def user_to_dict(user):
    return {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'approval_status': user.approval_status
    }


@admin_bp.route('/users', methods=['GET'])
@admin_required
def get_users():

    query = User.query.filter_by(role='user')
    search = request.args.get('search', '').strip()
    approval_status = request.args.get('approval_status')
    if approval_status:
        if approval_status not in ('approved', 'blacklist', 'pending'):
            return jsonify({'message': 'Invalid approval status'}), 400
        query = query.filter_by(approval_status=approval_status)

    users = query.order_by(User.id.desc()).all()
    users_to_display = []

    for user in users:
        if search:
            name_matches = search.lower() in user.username.lower()
            id_matches = search == str(user.id)

            if not name_matches and not id_matches:
                continue

        users_to_display.append(user_to_dict(user))

    return jsonify({'data': users_to_display}), 200


@admin_bp.route('/users/<int:user_id>', methods=['GET'])
@admin_required
def get_user(user_id):

    user = User.query.filter_by(id=user_id, role='user').first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    return jsonify({'data': user_to_dict(user)}), 200


@admin_bp.route('/users/<int:user_id>/status', methods=['PATCH'])
@admin_required
def update_user_status(user_id):

    user = User.query.filter_by(id=user_id, role='user').first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({'message': 'Invalid request data'}), 400

    status = data.get('approval_status')

    if status not in ('approved', 'blacklist'):
        return jsonify({'message': 'Invalid approval status'}), 400

    try:
        user.approval_status = status

        if status == 'blacklist':
            bookings = Booking.query.filter_by(user_id=user.id).all()

            for booking in bookings:
                trek = booking.trek

                if trek.trek_status not in ('pending', 'approved', 'upcoming'):
                    continue

                if booking.status not in ('pending', 'confirmed'):
                    continue

                if booking.status == 'confirmed':
                    trek.booked_slots -= booking.slots_booked

                booking.status = 'cancelled'
                booking.payment_status = 'refund finished'

        db.session.commit()
        clear_trek_cache()

    except SQLAlchemyError:

        db.session.rollback()
        return jsonify({'message': 'Failed to update user status'}), 500

    return jsonify({
        'message': 'User status updated successfully', 'data': user_to_dict(user)
    }), 200


@admin_bp.route('/users/<int:user_id>/bookings', methods=['GET'])
@admin_required
def get_user_bookings(user_id):

    user = User.query.filter_by(id=user_id, role='user').first()

    if not user:
        return jsonify({'message': 'User not found'}), 404

    bookings = []

    status = request.args.get('status')
    trek_status = request.args.get('trek_status')
    if status and status not in ('pending', 'confirmed', 'cancelled', 'completed'):
        return jsonify({'message': 'Invalid booking status'}), 400
    if trek_status and trek_status not in ('pending', 'approved', 'upcoming', 'ongoing', 'completed', 'cancelled'):
        return jsonify({'message': 'Invalid trek status'}), 400
    for booking in user.bookings:
        if status and booking.status != status:
            continue
        if trek_status and booking.trek.trek_status != trek_status:
            continue
        bookings.append({
        'id': booking.id,
        'user_id': booking.user_id,
        'booking_date': booking.booking_date.isoformat(),
        'status': booking.status,
        'payment_status': booking.payment_status,
        'slots_booked': booking.slots_booked,
        'trek': {
            'id': booking.trek.id,
            'display_id': booking.trek.display_id,
            'trek_name': booking.trek.trek_name,
            'location': booking.trek.location,
            'start_date': booking.trek.start_date.isoformat(),
            'end_date': booking.trek.end_date.isoformat(),
            'trek_status': booking.trek.trek_status
        }})

    return jsonify({
        'message': 'Bookings retrieved successfully',
        'data': bookings }), 200


@admin_bp.route('/dashboard',  methods=['GET'])
@admin_required
def admin_dashboard():


    total_treks = Trek.query.count()
    total_users = User.query.filter_by(role='user').count()
    total_staffs = User.query.filter_by(role='staff').count()
    total_bookings = Booking.query.count()

    recent_treks = Trek.query.order_by(Trek.id.desc()).limit(5).all()

    treks_to_display = []

    for trek in recent_treks:
        treks_to_display.append({
            'id': trek.id,
            'display_id': trek.display_id,
            'trek_name': trek.trek_name,
            'location': trek.location,
            'start_date': trek.start_date.strftime('%b %d'),
            'available_slots': trek.total_slots - trek.booked_slots,
            'bookings_open': trek.bookings_open,
            'trek_status': trek.trek_status
        })


    return jsonify({
        'message': 'Admin logged in successfully',
        'data': {
            'total_treks': total_treks,
            'total_users': total_users,
            'total_staffs': total_staffs,
            'total_bookings': total_bookings,
            'recent_treks':  treks_to_display
        }
    }), 200


@admin_bp.route('/treks', methods=['GET'])
@admin_required
def get_treks():

    search = request.args.get('search', '').strip().lower()
    cache_key = f'admin:listing:{search}'
    cached_data = get_cached_data(cache_key)
    if cached_data is not None:
        return jsonify(cached_data), 200

    treks = Trek.query.all()

    treks_to_display = []

    for trek in treks:
        if search:
            name_matches = search.lower() in trek.trek_name.lower()
            id_matches = search == str(trek.id)
            display_id_matches = search.lower() == trek.display_id.lower()

            if not name_matches and not id_matches and not display_id_matches:
                continue

        treks_to_display.append({
            'id': trek.id,
            'display_id': trek.display_id,
            'trek_name': trek.trek_name,
            'location': trek.location,
            'start_date': trek.start_date.strftime('%b %d'),
            'available_slots': trek.total_slots - trek.booked_slots,
            'bookings_open': trek.bookings_open,
            'trek_status': trek.trek_status
        })

    data = {'data': treks_to_display}
    cache_data(cache_key, data)
    return jsonify(data), 200


@admin_bp.route('/treks/<int:trek_id>', methods=['GET'])
@admin_required
def get_trek_info(trek_id):

    trek = Trek.query.get(trek_id)

    if trek is None:

        return jsonify({
            'message': "No trek found"
        }), 404

    return jsonify({

        'data':{
            'id': trek.id,
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
            'price': trek.price,
            'description': trek.description,
            'bookings_open': trek.bookings_open,
            'trek_status': trek.trek_status
            }
        }), 200


@admin_bp.route('/treks', methods=['POST'])
@admin_required
def create_trek():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            'message': 'Invalid request data'
        }), 400

    required_fields = [
        'trek_name',
        'location',
        'difficulty',
        'duration',
        'start_date',
        'end_date',
        'total_slots',
        'price'
    ]

    for field in required_fields:
        if data.get(field) is None or data.get(field) == '':
            return jsonify({
                'message': f'{field} is required'
            }), 400

    try:
        start_date = date.fromisoformat(data['start_date'])
        end_date = date.fromisoformat(data['end_date'])

        duration = int(data['duration'])
        total_slots = int(data['total_slots'])
        price = float(data['price'])

    except (ValueError, TypeError):
        return jsonify({
            'message': 'Invalid date or numeric value'
        }), 400

    if end_date < start_date:
        return jsonify({
            'message': 'End date cannot be before start date'
        }), 400

    if duration <= 0 or total_slots <= 0 or price < 0:
        return jsonify({
            'message': 'Invalid duration, slots, or price'
        }), 400

    if data['difficulty'] not in ('easy', 'moderate', 'hard'):
        return jsonify({
            'message': 'Invalid difficulty level'
        }), 400

    trek = Trek(
        trek_name=data['trek_name'],
        location=data['location'],
        difficulty=data['difficulty'],
        duration=duration,
        start_date=start_date,
        end_date=end_date,
        total_slots=total_slots,
        booked_slots=0,
        price=price,
        bookings_open=False,
        description=data.get('description'),
        trek_status='pending'
    )

    db.session.add(trek)
    db.session.commit()
    clear_trek_cache()

    return jsonify({
        'message': 'Trek added successfully',
        'trek_id': trek.id
    }), 201


@admin_bp.route('/treks/<int:trek_id>', methods=['PUT'])
@admin_required
def edit_trek(trek_id):


    trek = db.session.get(Trek, trek_id)

    if trek is None:
        return jsonify({
            'message': 'Trek not found'
        }), 404


    if trek.trek_status in ('completed', 'cancelled'):
        return jsonify({'message': 'Completed and cancelled trek details are read-only'}), 409

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            'message': 'Invalid request data'
        }), 400


    required_fields = [
        'trek_name',
        'location',
        'difficulty',
        'duration',
        'start_date',
        'end_date',
        'total_slots',
        'price'
    ]

    for field in required_fields:
        if data.get(field) is None or data.get(field) == '':
            return jsonify({
                'message': f'{field} is required'
            }), 400


    try:
        start_date = date.fromisoformat(data['start_date'])
        end_date = date.fromisoformat(data['end_date'])


        duration = int(data['duration'])
        total_slots = int(data['total_slots'])
        price = float(data['price'])

        if (
            isinstance(data['duration'], bool)
            or isinstance(data['total_slots'], bool)
            or str(duration) != str(data['duration'])
            or str(total_slots) != str(data['total_slots'])
        ):
            raise ValueError

    except (ValueError, TypeError):
        return jsonify({
            'message': 'Invalid date or numeric value'
        }), 400


    if end_date < start_date:
        return jsonify({
            'message': 'End date cannot be before start date'
        }), 400


    from math import isfinite

    if duration <= 0 or total_slots <= 0 or not isfinite(price) or price < 0:
        return jsonify({
            'message': 'Invalid duration, slots, or price'
        }), 400


    if data['difficulty'] not in ('easy', 'moderate', 'hard'):
        return jsonify({
            'message': 'Invalid difficulty level'
        }), 400


    trek_name = data['trek_name']
    location = data['location']
    description = data.get('description') or ''

    if (
        not isinstance(trek_name, str)
        or not trek_name.strip()
        or len(trek_name) > 100
        or not isinstance(location, str)
        or not location.strip()
        or len(location) > 100
        or not isinstance(description, str)
        or len(description) > 100
    ):
        return jsonify({
            'message': 'Invalid trek name, location, or description'
        }), 400


    bookings_open = data.get('bookings_open', trek.bookings_open)

    if not isinstance(bookings_open, bool):
        return jsonify({
            'message': 'bookings_open must be true or false'
        }), 400

    if total_slots < trek.booked_slots:
        return jsonify({
            'message': 'Total slots cannot be less than booked slots'
        }), 400


    if bookings_open and trek.trek_status not in ('approved', 'upcoming'):
        return jsonify({'message': 'Approve the trek before opening bookings'}), 409

    trek.trek_name = trek_name.strip()
    trek.location = location.strip()
    trek.difficulty = data['difficulty']
    trek.duration = duration
    trek.start_date = start_date
    trek.end_date = end_date
    trek.total_slots = total_slots
    trek.price = price
    trek.description = description
    if bookings_open and trek.trek_status == 'approved':
        trek.trek_status = 'upcoming'
    trek.bookings_open = bookings_open


    try:
        db.session.commit()
        clear_trek_cache()

    except Exception:
        db.session.rollback()
        return jsonify({
            'message': 'Failed to update trek'
        }), 500

    return jsonify({
        'message': 'Trek updated successfully',
        'trek_id': trek.id
    }), 200


@admin_bp.route('/treks/<int:trek_id>', methods=['DELETE'])
@admin_required
def delete_trek(trek_id):

    trek = db.session.get(Trek, trek_id)

    if trek is None:
        return jsonify({
            'message': 'Trek not found'
        }), 404

    if trek.trek_status == 'completed':
        return jsonify({'message': 'Completed treks must be kept for history'}), 409

    existing_booking = Booking.query.filter_by(trek_id=trek_id).first()

    if existing_booking:

        trek.trek_status = 'cancelled'
        trek.bookings_open = False
        for booking in trek.booking:
            if booking.status != 'completed':
                booking.status = 'cancelled'
                booking.payment_status = 'refund finished'
        trek.booked_slots = 0
        for assignment in trek.staff_assignments:
            assignment.status = 'cancelled'

        db.session.commit()
        clear_trek_cache()

        return jsonify({
            'message': 'Trek has existing bookings and was cancelled instead of deleted'
        }), 200

    db.session.delete(trek)
    db.session.commit()
    clear_trek_cache()

    return jsonify({
        'message': 'Trek deleted successfully'
    }), 200


@admin_bp.route('/treks/<int:trek_id>/staff', methods=['POST'])
@admin_required
def assign_staff(trek_id):

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({'message': 'Invalid request data'}), 400

    staff_id = data.get('staff_id')

    trek = Trek.query.get(trek_id)
    staff = Staff.query.get(staff_id)

    if not trek or not staff:
        return jsonify({'message': 'Trek or staff not found'}), 404

    if staff.user.approval_status != 'approved':
        return jsonify({'message': 'Staff is not approved'}), 403

    if trek.trek_status not in ('pending', 'approved', 'upcoming'):
        return jsonify({'message': 'Trek is not upcoming'}), 400

    active_assignments = StaffTrek.query.filter_by(
        staff_id=staff_id,
        status='assigned'
    ).all()

    for assignment in active_assignments:

        other_trek = assignment.trek

        if (
            other_trek
            and other_trek.trek_status in ('pending', 'approved', 'upcoming', 'ongoing')
            and trek.start_date <= other_trek.end_date
            and trek.end_date >= other_trek.start_date
        ):
            return jsonify({
                'message': 'Staff is assigned to another trek on these dates'
            }), 409

    if staff.next_available_date and staff.next_available_date > trek.start_date:
        return jsonify({
            'message': 'Staff is not available on the trek start date'
        }), 400

    assignment = StaffTrek(
        staff_id=staff_id,
        trek_id=trek_id,
        status='assigned'
    )

    trek.staffing_status = 'assigned'

    try:
        db.session.add(assignment)
        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'message': 'Failed to assign staff'}), 500

    return jsonify({
        'message': 'Staff assigned successfully',
        'assignment_id': assignment.id,
        'trek_id': assignment.trek_id,
        'staff_id': assignment.staff_id
    }), 201


@admin_bp.route('/treks/<int:trek_id>/staff', methods=['GET'])
@admin_required
def get_assigned_staff(trek_id):

    trek = Trek.query.get(trek_id)

    if not trek:
        return jsonify({'message': 'Trek not found'}), 404

    assignments = StaffTrek.query.filter_by(
        trek_id=trek_id,
        status='assigned'
    ).all()

    result = []

    for assignment in assignments:
        result.append({
            'assignment_id': assignment.id,
            'trek_id': assignment.trek_id,
            'staff_id': assignment.staff_id,
            'username': assignment.staff.user.username,
            'contact_number': assignment.staff.contact_number
        })


    return jsonify({'data': result}), 200


@admin_bp.route('/cancel-assignments/<int:assignment_id>', methods=['PATCH'])
@admin_required
def cancel_staff_assignment(assignment_id):

    assignment = StaffTrek.query.get(assignment_id)

    if not assignment:
            return jsonify({'message': 'Assignment not found'}), 404

    trek = Trek.query.get(assignment.trek_id)

    if assignment.status != 'assigned':
        return jsonify({'message': 'Assignment is not active'}), 400

    if assignment.trek.trek_status not in ('pending', 'approved', 'upcoming'):
        return jsonify({
            'message': 'Only upcoming trek assignments can be cancelled here'
        }), 400

    try:
        assignment.status = 'cancelled'

        remaining_staff = StaffTrek.query.filter_by(
            trek_id=assignment.trek_id,
            status='assigned'
        ).first()

        if not remaining_staff:

            trek.staffing_status = 'pending'

        db.session.commit()

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({'message': 'Failed to cancel assignment'}), 500

    return jsonify({
        'message': 'Staff assignment cancelled successfully'
    }), 200


@admin_bp.route('/staffs', methods=['GET'])
@admin_required
def get_staffs():

    staffs = User.query.filter_by(role='staff').all()
    search = request.args.get('search', '').strip()

    staff_to_display = []

    for staff in staffs:
        if search:
            name_matches = search.lower() in staff.username.lower()
            user_id_matches = search == str(staff.id)
            staff_id_matches = False

            if staff.staff_profile:
                staff_id_matches = search == str(staff.staff_profile.id)

            if not name_matches and not user_id_matches and not staff_id_matches:
                continue

        staff_to_display.append(staff_to_dict(staff))

    return jsonify({
        'data': staff_to_display
    }), 200


@admin_bp.route('/staffs', methods=['POST'])
@admin_required
def create_staff():

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            'message': 'Invalid request data'
        }), 400

    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    contact_number = data.get('contact_number')
    available_date = data.get('next_available_date')

    error = validate_staff_data(data)

    if error:
        return jsonify({'message': error}), 400

    username = username.strip()
    email = email.strip().lower()

    if not username or not email or not isinstance(password, str) or not password.strip():
        return jsonify({
            'message': 'Username, email and password cannot be empty'
        }), 400

    if not contact_number:
        return jsonify({
            'message': 'Contact number is required'
        }), 400

    if available_date:

        try:
            available_date = date.fromisoformat(available_date)

        except (ValueError, TypeError):
            return jsonify({
                'message': 'Invalid available date'
            }), 400

    else:
        available_date = None

    existing_user = User.query.filter_by(email=email).first()

    if existing_user:
        return jsonify({
            'message': 'Email already registered'
        }), 409

    user = User(
        username=username,
        email=email,
        password=generate_password_hash(password),
        role='staff',
        approval_status='approved'
    )

    staff_profile = Staff(
        contact_number=contact_number,
        next_available_date=available_date
    )

    user.staff_profile = staff_profile

    try:
        db.session.add(user)
        db.session.commit()

    except IntegrityError:
        db.session.rollback()

        return jsonify({
            'message': 'Staff account could not be created because of conflicting data'
        }), 409

    except SQLAlchemyError:
        db.session.rollback()

        return jsonify({
            'message': 'Failed to create staff'
        }), 500

    return jsonify({
        'message': 'Staff created successfully',
        'data': {
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'role': user.role,
            'approval_status': user.approval_status
        }
    }), 201


@admin_bp.route('/staffs/<int:user_id>', methods=['GET'])
@admin_required
def get_staff(user_id):

    staff = User.query.get(user_id)

    if not staff or staff.role != 'staff':
        return jsonify({
            'message': 'Staff not found'
        }), 404

    return jsonify(staff_to_dict(staff)), 200


@admin_bp.route('/staffs/<int:user_id>', methods=['PUT'])
@admin_required
def edit_staff(user_id):

    staff = User.query.get(user_id)

    if not staff or staff.role != 'staff':
        return jsonify({
            'message': 'Staff not found'
        }), 404

    profile = staff.staff_profile

    if not profile:
        return jsonify({
            'message': 'Staff profile not found'
        }), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            'message': 'Invalid request data'
        }), 400

    username = data.get('username')
    email = data.get('email')
    contact_number = data.get('contact_number')
    available_date = data.get('next_available_date')

    error = validate_staff_data(data)

    if error:
        return jsonify({'message': error}), 400

    username = username.strip()
    email = email.strip().lower()
    contact_number = contact_number.strip()

    if not username or not email or not contact_number:
        return jsonify({
            'message': 'Username, email and contact number cannot be empty'
        }), 400

    if available_date is None or available_date == '':
        available_date = None

    elif isinstance(available_date, str):
        try:
            available_date = date.fromisoformat(available_date)
        except ValueError:
            return jsonify({
                'message': 'Invalid available date'
            }), 400

    else:
        return jsonify({
            'message': 'Invalid available date'
        }), 400

    existing_user = User.query.filter_by(email=email).first()

    if existing_user and existing_user.id != staff.id:
        return jsonify({
            'message': 'Email already registered'
        }), 409

    staff.username = username
    staff.email = email

    profile.contact_number = contact_number
    profile.next_available_date = available_date

    try:
        db.session.commit()

    except IntegrityError:
        db.session.rollback()
        return jsonify({
            'message': 'Email already registered or conflicting data'
        }), 409

    except SQLAlchemyError:
        db.session.rollback()
        return jsonify({
            'message': 'Failed to update staff'
        }), 500

    return jsonify({
        'message': 'Staff updated successfully',
        'data': {
            'id': staff.id,
            'username': staff.username,
            'email': staff.email,
            'contact_number': profile.contact_number,
            'next_available_date': (
                profile.next_available_date.isoformat()
                if profile.next_available_date
                else None
            )
        }
    }), 200


@admin_bp.route('/staffs/<int:user_id>/assignments', methods=['GET'])
@admin_required
def get_staff_assignment_history(user_id):

    staff_user = User.query.filter_by(id=user_id, role='staff').first()

    if not staff_user:
        return jsonify({'message': 'Staff not found'}), 404

    if not staff_user.staff_profile:
        return jsonify({'data': []}), 200

    assignments = StaffTrek.query.filter_by(
        staff_id=staff_user.staff_profile.id
    ).order_by(StaffTrek.id.desc()).all()

    history = []

    for assignment in assignments:
        history.append({
            'assignment_id': assignment.id,
            'status': assignment.status,
            'trek': {
                'id': assignment.trek.id,
                'display_id': assignment.trek.display_id,
                'trek_name': assignment.trek.trek_name,
                'location': assignment.trek.location,
                'start_date': assignment.trek.start_date.isoformat(),
                'end_date': assignment.trek.end_date.isoformat(),
                'trek_status': assignment.trek.trek_status
            }
        })

    return jsonify({
        'message': 'Staff assignment history retrieved successfully',
        'data': history
    }), 200


@admin_bp.route('/staffs/<int:user_id>/status', methods=['PATCH'])
@admin_required
def update_staff_status(user_id):

    staff = User.query.get(user_id)

    if not staff or staff.role != 'staff':
        return jsonify({
            'message': 'Staff not found'
        }), 404

    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            'message': 'Invalid request data'
        }), 400

    new_status = data.get('approval_status')

    if new_status not in ('approved', 'blacklist'):
        return jsonify({
            'message': 'Invalid approval status'
        }), 400

    if staff.approval_status == new_status:
        return jsonify({
            'message': f'Staff is already {new_status}'
        }), 200

    staff.approval_status = new_status

    affected_treks = []

    try:

        if new_status == 'blacklist':

            profile = staff.staff_profile

            if profile:

                assignments = StaffTrek.query.filter_by(
                    staff_id=profile.id,
                    status='assigned'
                ).all()

                for assignment in assignments:

                    trek = db.session.get(Trek, assignment.trek_id)

                    if trek and trek.trek_status in ('pending', 'approved', 'upcoming'):

                        assignment.status = 'cancelled'

                        affected_treks.append({
                            'id': trek.id,
                            'trek_name': trek.trek_name
                        })

                        remaining_staff = StaffTrek.query.filter_by(
                                trek_id=trek.id,
                                status='assigned'
                            ).first()

                        if not remaining_staff:

                            trek.staffing_status = 'pending'


        db.session.commit()

    except SQLAlchemyError:

        db.session.rollback()

        return jsonify({
            'message': 'Failed to update staff status'
        }), 500

    return jsonify({
        'message': 'Staff status updated successfully',
        'data': {
            'id': staff.id,
            'username': staff.username,
            'approval_status': staff.approval_status,
            'affected_treks': affected_treks
        }
    }), 200


@admin_bp.route('/all-bookings', methods=['GET'])
@admin_required
def all_bookings():

    records = Booking.query.all()

    if not records:

        return jsonify({
            'message': 'No bookings yet',
            'data': []
        }), 200

    bookings = []

    for book in records:

        bookings.append({
                'id': book.id,
                'user_id': book.user_id,
                'trek_id': book.trek_id,
                'booking_date': book.booking_date.isoformat(),
                'status': book.status,
                'payment_status': book.payment_status,
                'slots_booked': book.slots_booked,
                })

    return jsonify({
        'message': 'Bookings retrieved successfully',
        'data': bookings }), 200



@admin_bp.route('/treks/<int:trek_id>/approve', methods=['PATCH'])
@admin_required
def approve_trek(trek_id):
    trek = db.session.get(Trek, trek_id)
    if not trek:
        return jsonify({'message': 'Trek not found'}), 404
    if trek.trek_status != 'pending':
        return jsonify({'message': 'Only pending treks can be approved'}), 409
    trek.trek_status = 'approved'
    trek.bookings_open = False
    db.session.commit()
    clear_trek_cache()
    return jsonify({'message': 'Trek approved. Bookings can now be opened.'}), 200


@admin_bp.route('/reports', methods=['GET'])
@admin_required
def reports():
    def counts(model, field, statuses, query=None):
        query = query if query is not None else model.query
        return [{'label': status, 'count': query.filter(field == status).count()}
                for status in statuses]

    return jsonify({'data': [
        {'title': 'Treks', 'items': counts(Trek, Trek.trek_status,
            ('pending', 'approved', 'upcoming', 'ongoing', 'completed', 'cancelled'))},
        {'title': 'Users (trekkers)', 'items': counts(User, User.approval_status,
            ('approved', 'blacklist', 'pending'), User.query.filter_by(role='user'))},
        {'title': 'Bookings', 'items': counts(Booking, Booking.status,
            ('pending', 'confirmed', 'completed', 'cancelled'))},
    ]}), 200


@admin_bp.route('/profile', methods=['GET', 'PUT'])
@admin_required
def admin_profile():
    admin = db.session.get(User, int(get_jwt_identity()))
    if request.method == 'PUT':
        data = request.get_json(silent=True)
        if not isinstance(data, dict) or set(data) != {'username'}:
            return jsonify({'message': 'Only the display name can be updated'}), 400
        name = data['username']
        if not isinstance(name, str) or not 1 <= len(name.strip()) <= 100:
            return jsonify({'message': 'Name must contain 1 to 100 characters'}), 400
        admin.username = name.strip()
        try:
            db.session.commit()
        except SQLAlchemyError:
            db.session.rollback()
            return jsonify({'message': 'Could not save display name'}), 500
    return jsonify({'data': {'username': admin.username}}), 200
