from flask import jsonify, request
from marshmallow import ValidationError

from app.auth import encode_token, token_required
from app.blueprints.customers import customers_bp
from app.blueprints.customers.schemas import customer_schema, customers_schema, login_schema
from app.extensions import db, limiter
from app.models.customer import Customer
from app.models.service_ticket import ServiceTicket


@customers_bp.post("/")
def create_customer():
    try:
        payload = request.get_json() or {}
        customer = customer_schema.load(payload)
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.add(customer)
    db.session.commit()
    return customer_schema.jsonify(customer), 201


@customers_bp.post("/login")
@limiter.limit("5 per minute")
def login_customer():
    try:
        payload = request.get_json() or {}
        login_data = login_schema.load(payload)
    except ValidationError as err:
        return jsonify(err.messages), 400

    customer = Customer.query.filter_by(email=login_data.email).first()
    if customer is None or customer.password != login_data.password:
        return jsonify({"error": "Invalid email or password"}), 401

    token = encode_token(customer.id, "customer")
    return jsonify({"token": token, "customer": customer_schema.dump(customer)}), 200


@customers_bp.get("/")
def get_customers():
    page = request.args.get("page", default=1, type=int)
    per_page = request.args.get("per_page", default=10, type=int)
    pagination = Customer.query.paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "items": customers_schema.dump(pagination.items),
        "page": pagination.page,
        "per_page": pagination.per_page,
        "total": pagination.total,
        "pages": pagination.pages,
    }), 200


@customers_bp.get("/<int:customer_id>")
def get_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    return customer_schema.jsonify(customer), 200


@customers_bp.put("/<int:customer_id>")
@token_required
def update_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    payload = request.get_json() or {}

    for field in ["name", "email", "phone"]:
        if field in payload:
            setattr(customer, field, payload[field])

    db.session.commit()
    return customer_schema.jsonify(customer), 200


@customers_bp.delete("/<int:customer_id>")
@token_required
def delete_customer(customer_id):
    customer = Customer.query.get_or_404(customer_id)
    db.session.delete(customer)
    db.session.commit()
    return jsonify({"message": f"Customer {customer_id} deleted"}), 200


@customers_bp.get("/my-tickets")
@token_required
def get_my_tickets(customer_id):
    tickets = ServiceTicket.query.filter_by(customer_id=customer_id).all()
    return jsonify([{
        "id": ticket.id,
        "vin": ticket.vin,
        "issue_description": ticket.issue_description,
        "status": ticket.status,
        "service_date": str(ticket.service_date),
        "mechanic_ids": [mechanic.id for mechanic in ticket.mechanics],
    } for ticket in tickets]), 200
