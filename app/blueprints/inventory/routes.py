from flask import jsonify, request
from marshmallow import ValidationError

from app.auth import mechanic_token_required
from app.blueprints.inventory import inventory_bp
from app.blueprints.inventory.schemas import inventory_schema, inventories_schema
from app.extensions import cache, db
from app.models.inventory import Inventory


@inventory_bp.post("/")
@mechanic_token_required
def create_inventory_item(mechanic_id):
    try:
        item = inventory_schema.load(request.get_json() or {})
    except ValidationError as err:
        return jsonify(err.messages), 400

    db.session.add(item)
    db.session.commit()
    return inventory_schema.jsonify(item), 201


@inventory_bp.get("/")
@cache.cached(timeout=60)
def get_inventory_items():
    items = Inventory.query.all()
    return inventories_schema.jsonify(items), 200


@inventory_bp.get("/<int:item_id>")
def get_inventory_item(item_id):
    item = Inventory.query.get_or_404(item_id)
    return inventory_schema.jsonify(item), 200


@inventory_bp.put("/<int:item_id>")
@mechanic_token_required
def update_inventory_item(item_id, mechanic_id):
    item = Inventory.query.get_or_404(item_id)
    payload = request.get_json() or {}

    for field in ["name", "price"]:
        if field in payload:
            setattr(item, field, payload[field])

    db.session.commit()
    return inventory_schema.jsonify(item), 200


@inventory_bp.delete("/<int:item_id>")
@mechanic_token_required
def delete_inventory_item(item_id, mechanic_id):
    item = Inventory.query.get_or_404(item_id)
    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": f"Inventory item {item_id} deleted"}), 200
