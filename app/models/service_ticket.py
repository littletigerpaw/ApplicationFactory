from datetime import date

from app.extensions import db


ticket_mechanics = db.Table(
    "ticket_mechanics",
    db.Column("ticket_id", db.Integer, db.ForeignKey("service_tickets.id"), primary_key=True),
    db.Column("mechanic_id", db.Integer, db.ForeignKey("mechanics.id"), primary_key=True),
)

ticket_inventory = db.Table(
    "ticket_inventory",
    db.Column("ticket_id", db.Integer, db.ForeignKey("service_tickets.id"), primary_key=True),
    db.Column("inventory_id", db.Integer, db.ForeignKey("inventory.id"), primary_key=True),
)


class ServiceTicket(db.Model):
    __tablename__ = "service_tickets"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    vin = db.Column(db.String(64), nullable=False)
    issue_description = db.Column(db.Text, nullable=False)
    service_date = db.Column(db.Date, nullable=False, default=date.today)
    status = db.Column(db.String(50), nullable=False, default="open")

    customer = db.relationship("Customer", back_populates="service_tickets")
    mechanics = db.relationship(
        "Mechanic",
        secondary=ticket_mechanics,
        back_populates="service_tickets",
        lazy=True,
    )
    inventory = db.relationship(
        "Inventory",
        secondary=ticket_inventory,
        back_populates="service_tickets",
        lazy=True,
    )
