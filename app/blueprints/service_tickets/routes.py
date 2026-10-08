from flask import jsonify, request

from app.auth import token_required
from app.blueprints.service_tickets import service_tickets_bp
from app.blueprints.service_tickets.schemas import service_ticket_schema, service_tickets_schema
from app.extensions import cache, db
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.mechanic import Mechanic
from app.models.service_ticket import ServiceTicket


@service_tickets_bp.post("/")
@token_required
def create_service_ticket(customer_id):
    payload = request.get_json() or {}
    required_fields = ["vin", "issue_description"]
    missing = [field for field in required_fields if field not in payload]

    if missing:
        return jsonify({"error": f"Missing fields: {', '.join(missing)}"}), 400

    ticket = ServiceTicket(
        customer_id=customer_id,
        vin=payload["vin"],
        issue_description=payload["issue_description"],
        status=payload.get("status", "open"),
    )

    db.session.add(ticket)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 201


@service_tickets_bp.put("/<int:ticket_id>/assign-mechanic/<int:mechanic_id>")
@token_required
def assign_mechanic(customer_id, ticket_id, mechanic_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    mechanic = Mechanic.query.get_or_404(mechanic_id)

    if mechanic in ticket.mechanics:
        return jsonify({"message": "Mechanic already assigned"}), 200

    ticket.mechanics.append(mechanic)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.put("/<int:ticket_id>/remove-mechanic/<int:mechanic_id>")
@token_required
def remove_mechanic(customer_id, ticket_id, mechanic_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    mechanic = Mechanic.query.get_or_404(mechanic_id)

    if mechanic not in ticket.mechanics:
        return jsonify({"message": "Mechanic was not assigned to this ticket"}), 404

    ticket.mechanics.remove(mechanic)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.put("/<int:ticket_id>/edit")
@token_required
def edit_ticket_mechanics(customer_id, ticket_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    payload = request.get_json() or {}

    remove_ids = payload.get("remove_ids", [])
    add_ids = payload.get("add_ids", [])

    for mechanic_id in remove_ids:
        mechanic = Mechanic.query.get(mechanic_id)
        if mechanic and mechanic in ticket.mechanics:
            ticket.mechanics.remove(mechanic)

    for mechanic_id in add_ids:
        mechanic = Mechanic.query.get(mechanic_id)
        if mechanic and mechanic not in ticket.mechanics:
            ticket.mechanics.append(mechanic)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.put("/<int:ticket_id>/add-part/<int:inventory_id>")
def add_part_to_ticket(ticket_id, inventory_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    inventory_item = Inventory.query.get_or_404(inventory_id)

    if inventory_item in ticket.inventory:
        return jsonify({"message": "Part already added to this ticket"}), 200

    ticket.inventory.append(inventory_item)
    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.get("/")
@cache.cached(timeout=60)
def get_service_tickets():
    tickets = ServiceTicket.query.all()
    return service_tickets_schema.jsonify(tickets), 200


@service_tickets_bp.get("/<int:ticket_id>")
def get_service_ticket(ticket_id):
    ticket = ServiceTicket.query.get_or_404(ticket_id)
    return service_ticket_schema.jsonify(ticket), 200
