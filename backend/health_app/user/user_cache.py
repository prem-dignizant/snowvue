import redis
from django.core.cache import cache
import json


def get_cache(key):
    data = cache.get(key)
    if data:
        return json.loads(data)  # Deserialize JSON string back to dict
    return None

def set_cache(key, data, timeout=300):
    cache.set(key, json.dumps(data), timeout)


def delete_cache(key):
    cache.delete(key)