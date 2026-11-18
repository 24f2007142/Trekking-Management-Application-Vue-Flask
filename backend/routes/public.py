from datetime import date

from flask import Blueprint, current_app, jsonify, render_template

from cache import get_cached_data, cache_data
from models import Trek


public_bp = Blueprint('public', __name__)


def get_public_statistics():
    # Check Redis before reading the database.
    cached_data = get_cached_data('public:statistics')
    if cached_data is not None:
        return cached_data

    treks = Trek.query.filter(Trek.trek_status != 'cancelled').all()

    upcoming_treks = 0
    completed_treks = 0
    locations = []

    for trek in treks:
        if trek.trek_status == 'upcoming':
            upcoming_treks += 1

        if trek.trek_status == 'completed':
            completed_treks += 1

        # Count each location only once.
        if trek.location not in locations:
            locations.append(trek.location)

    stats = {
        'upcoming_treks': upcoming_treks,
        'completed_treks': completed_treks,
        'destinations': len(locations)
    }

    cache_data('public:statistics', stats)
    return stats


@public_bp.route('/', methods=['GET'])
def landing_page():
    stats = get_public_statistics()
    year = date.today().year
    frontend_url = current_app.config['FRONTEND_URL'].rstrip('/')

    return render_template(
        'landing_page.html',
        stats=stats,
        year=year,
        frontend_url=frontend_url
    )


@public_bp.route('/api/public/statistics', methods=['GET'])
def public_statistics():
    stats = get_public_statistics()

    return jsonify({'data': stats}), 200
