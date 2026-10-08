from flask import Blueprint

mechanics_bp = Blueprint("mechanics", __name__)

from app.blueprints.mechanics import routes
