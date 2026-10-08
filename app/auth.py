import os
from functools import wraps

from flask import jsonify, request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from jose import jwt

from app.extensions import cache, db
from app.models.customer import Customer
from app.models.mechanic import Mechanic


limiter = Limiter(key_func=get_remote_address)


def encode_token(subject_id, subject_type="customer"):
    payload = {
        "customer_id": subject_id,
        "mechanic_id": None,
        "subject_type": subject_type,
    }
    if subject_type == "mechanic":
        payload["customer_id"] = None
        payload["mechanic_id"] = subject_id
    return jwt.encode(payload, os.getenv("JWT_SECRET_KEY", "advanced-api-jwt-secret"), algorithm="HS256")


def decode_token(token):
    if not token:
        return None

    try:
        token = token.replace("Bearer ", "", 1).strip()
        return jwt.decode(token, os.getenv("JWT_SECRET_KEY", "advanced-api-jwt-secret"), algorithms=["HS256"])
    except Exception:
        return None


def token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        payload = decode_token(auth_header)
        if payload is None or payload.get("subject_type") != "customer":
            return jsonify({"error": "Valid customer token required"}), 401

        customer = Customer.query.get(payload.get("customer_id"))
        if customer is None:
            return jsonify({"error": "Customer not found"}), 404

        return fn(*args, customer_id=customer.id, **kwargs)

    return wrapper


def mechanic_token_required(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        payload = decode_token(auth_header)
        if payload is None or payload.get("subject_type") != "mechanic":
            return jsonify({"error": "Valid mechanic token required"}), 401

        mechanic = Mechanic.query.get(payload.get("mechanic_id"))
        if mechanic is None:
            return jsonify({"error": "Mechanic not found"}), 404

        return fn(*args, mechanic_id=mechanic.id, **kwargs)

    return wrapper


def cache_response(timeout=60):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            cache_key = f"{fn.__name__}:{request.path}:{request.args.to_dict()}"
            cached_value = cache.get(cache_key)
            if cached_value is not None:
                return cached_value

            response = fn(*args, **kwargs)
            cache.set(cache_key, response, timeout=timeout)
            return response

        return wrapper

    return decorator
