from flask import jsonify, request
from marshmallow import ValidationError

from app.auth import encode_token, mechanic_token_required
from app.blueprints.mechanics import mechanics_bp
from app.blueprints.mechanics.schemas import mechanic_schema, mechanics_schema
from app.extensions import cache, db, limiter
from app.models.mechanic import Mechanic
from app.models.service_ticket import ServiceTicket


@mechanics_bp.post("/")
def create_mechanic():
    try:
        mechanic = mechanic_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.add(mechanic)
    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 201


@mechanics_bp.post("/login")
@limiter.limit("5 per minute")
def login_mechanic():
    payload = request.get_json() or {}
    email = payload.get("email")
    password = payload.get("password")

    mechanic = Mechanic.query.filter_by(email=email).first()
    if mechanic is None or mechanic.password != password:
        return jsonify({"error": "Invalid email or password"}), 401

    token = encode_token(mechanic.id, "mechanic")
    return jsonify({"token": token, "mechanic": mechanic_schema.dump(mechanic)}), 200


@mechanics_bp.get("/")
@cache.cached(timeout=60)
def get_mechanics():
    mechanics = Mechanic.query.all()
    return mechanics_schema.jsonify(mechanics), 200


@mechanics_bp.get("/most-active")
def get_most_active_mechanics():
    results = (
        db.session.query(
            Mechanic.id,
            Mechanic.name,
            db.func.count(ServiceTicket.id).label("ticket_count"),
        )
        .join(ServiceTicket.mechanics)
        .group_by(Mechanic.id, Mechanic.name)
        .order_by(db.desc("ticket_count"), Mechanic.id)
        .all()
    )

    return jsonify([
        {"id": mechanic_id, "name": name, "ticket_count": ticket_count}
        for mechanic_id, name, ticket_count in results
    ]), 200


@mechanics_bp.put("/<int:id>")
@mechanic_token_required
def update_mechanic(id, mechanic_id=None):
    mechanic = Mechanic.query.get_or_404(id)
    payload = request.get_json() or {}

    for field in ["name", "specialty", "email"]:
        if field in payload:
            setattr(mechanic, field, payload[field])

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200


@mechanics_bp.delete("/<int:id>")
@mechanic_token_required
def delete_mechanic(id, mechanic_id=None):
    mechanic = Mechanic.query.get_or_404(id)
    db.session.delete(mechanic)
    db.session.commit()
    return jsonify({"message": f"Mechanic {id} deleted"}), 200
