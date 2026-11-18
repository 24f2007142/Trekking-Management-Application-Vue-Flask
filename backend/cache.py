import json

from flask import current_app
from redis import Redis
from redis.exceptions import RedisError


# Celery uses databases 0 and 1. API caching uses database 2.
redis_cache = Redis(
    host='127.0.0.1', port=6379, db=2, decode_responses=True,
    socket_connect_timeout=1, socket_timeout=1,
)
CACHE_EXPIRY = 300  # Five minutes, measured from when the data is saved.
CACHE_PREFIX = 'hi-trek:treks:'


def get_cached_data(key):
    try:
        data = redis_cache.get(CACHE_PREFIX + key)
        if data is not None:
            return json.loads(data)
    except (RedisError, ValueError):
        current_app.logger.warning('Cache read failed; loading from the database.')
    return None


def cache_data(key, data):
    try:
        redis_cache.setex(CACHE_PREFIX + key, CACHE_EXPIRY, json.dumps(data))
    except RedisError:
        current_app.logger.warning('Cache write failed; returning database data.')


def clear_trek_cache():
    # Clear all trek cache variants when called after relevant data changes.
    # This also clears other users' listings when available slots change.
    try:
        for key in redis_cache.scan_iter(match=CACHE_PREFIX + '*'):
            redis_cache.delete(key)
    except RedisError:
        current_app.logger.warning('Cache refresh failed; old entries will expire within five minutes.')
