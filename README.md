# BackendP1 Repair Shop API

This project is a customized shop-management backend built for a repair and service business.

## Features

- Customer accounts with JWT authentication
- Mechanic accounts with protected access
- Service ticket creation and assignment workflows
- Inventory tracking for repair parts
- Rate limiting and response caching
- Pagination for customer listing endpoints

## Project setup

1. Change into the project folder.
2. Create and activate a virtual environment if needed.
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Start the API:

   ```bash
   python run.py
   ```

The API runs on http://127.0.0.1:5002

## Main endpoints

- POST /customers/
- POST /customers/login
- GET /customers/
- GET /customers/my-tickets
- POST /mechanics/
- GET /mechanics/
- POST /mechanics/login
- PUT /mechanics/<id>
- DELETE /mechanics/<id>
- GET /mechanics/most-active
- POST /inventory/
- GET /inventory/
- POST /service-tickets/
- PUT /service-tickets/<ticket_id>/assign-mechanic/<mechanic_id>
- PUT /service-tickets/<ticket_id>/remove-mechanic/<mechanic_id>
- GET /service-tickets/
- PUT /service-tickets/<ticket_id>/edit
- PUT /service-tickets/<ticket_id>/add-part/<inventory_id>

## Postman collection

- Export file included: `mechanic_shop_api.postman_collection.json`
- The collection stores endpoint tests for customer auth, mechanic CRUD, and service-ticket assignment/removal flows.
- Dynamic-ID variant included: `mechanic_shop_api_dynamic.postman_collection.json`
- The dynamic variant includes test assertions for status codes, token presence, id capture, and assign/remove mechanic relationship checks.
- Suggested run order in Postman: Create Customer -> Customer Login -> Create Mechanic -> Mechanic Login -> Update Mechanic -> Create Service Ticket -> Assign Mechanic -> Remove Mechanic -> Get All Service Tickets -> Delete Mechanic.

## Auth

Use a Bearer token in the Authorization header for protected customer and mechanic routes.
