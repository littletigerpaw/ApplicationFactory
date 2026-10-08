from flask import Flask

from app.auth import limiter
from app.extensions import cache, db, ma
from app.models.customer import Customer
from app.models.inventory import Inventory
from app.models.mechanic import Mechanic
from app.models.service_ticket import ServiceTicket
from config import Config


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    ma.init_app(app)
    cache.init_app(app)
    limiter.init_app(app)

    from app.blueprints.customers import customers_bp
    from app.blueprints.inventory import inventory_bp
    from app.blueprints.mechanics import mechanics_bp
    from app.blueprints.service_tickets import service_tickets_bp

    app.register_blueprint(customers_bp, url_prefix="/customers")
    app.register_blueprint(mechanics_bp, url_prefix="/mechanics")
    app.register_blueprint(service_tickets_bp, url_prefix="/service-tickets")
    app.register_blueprint(inventory_bp, url_prefix="/inventory")

    with app.app_context():
        db.create_all()

    @app.get("/")
    def health_check():
        return {
            "project": "BackendP1",
            "service": "Repair Shop API",
            "status": "running",
            "message": "BackendP1 Repair API is running"
        }, 200

    return app
