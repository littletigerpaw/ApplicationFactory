from marshmallow import fields

from app.extensions import ma
from app.models.customer import Customer


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True
        ordered = True

    password = fields.String(load_only=True)
    service_ticket_ids = fields.Method("get_service_ticket_ids", dump_only=True)

    def get_service_ticket_ids(self, obj):
        return [ticket.id for ticket in obj.service_tickets]


class LoginSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Customer
        load_instance = True
        ordered = True
        fields = ("email", "password")


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = LoginSchema()
