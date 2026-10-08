from marshmallow import fields

from app.extensions import ma
from app.models.mechanic import Mechanic


class MechanicSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = True
        ordered = True

    password = fields.String(load_only=True)
    ticket_ids = fields.Method("get_ticket_ids", dump_only=True)

    def get_ticket_ids(self, obj):
        return [ticket.id for ticket in obj.service_tickets]


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
