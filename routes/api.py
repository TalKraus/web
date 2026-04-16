# api.py - REST API blueprint with Swagger documentation
# TechRent Pro - Equipment Rental Platform

from datetime import datetime

from flask import Blueprint, Response, jsonify, request

import db

api_bp = Blueprint("api", __name__)


# ===================== Equipment API =====================


@api_bp.route("/api/equipment", methods=["GET"])
def api_get_equipment() -> tuple[Response, int]:
    """
    List all equipment items.
    ---
    tags:
      - Equipment
    responses:
      200:
        description: Array of all equipment items
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: integer
              name:
                type: string
              category:
                type: string
              daily_rate:
                type: number
              quantity:
                type: integer
              description:
                type: string
              available:
                type: boolean
    """
    return jsonify(db.get_all_equipment()), 200


@api_bp.route("/api/equipment", methods=["POST"])
def api_create_equipment() -> tuple[Response, int]:
    """
    Create a new equipment item.
    ---
    tags:
      - Equipment
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - category
            - daily_rate
            - quantity
          properties:
            name:
              type: string
            category:
              type: string
            daily_rate:
              type: number
            quantity:
              type: integer
            description:
              type: string
            available:
              type: boolean
    responses:
      201:
        description: Equipment created successfully
      400:
        description: Invalid input
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    errors = []
    if not data.get("name"):
        errors.append("Name is required")
    if not data.get("category"):
        errors.append("Category is required")
    try:
        if float(data.get("daily_rate", 0)) <= 0:
            errors.append("Daily rate must be greater than 0")
    except (ValueError, TypeError):
        errors.append("Daily rate must be a valid number")
    try:
        if int(data.get("quantity", 0)) < 1:
            errors.append("Quantity must be at least 1")
    except (ValueError, TypeError):
        errors.append("Quantity must be a valid number")

    if errors:
        return jsonify({"error": ", ".join(errors)}), 400

    item = db.create_equipment(data)
    return jsonify(item), 201


@api_bp.route("/api/equipment/<int:eq_id>", methods=["GET"])
def api_get_equipment_by_id(eq_id: int) -> tuple[Response, int]:
    """
    Get a single equipment item by ID.
    ---
    tags:
      - Equipment
    parameters:
      - in: path
        name: eq_id
        type: integer
        required: true
    responses:
      200:
        description: Equipment item found
      404:
        description: Equipment not found
    """
    item = db.get_equipment_by_id(eq_id)
    if not item:
        return jsonify({"error": "Equipment not found"}), 404
    return jsonify(item), 200


@api_bp.route("/api/equipment/<int:eq_id>", methods=["PUT"])
def api_update_equipment(eq_id: int) -> tuple[Response, int]:
    """
    Update an equipment item.
    ---
    tags:
      - Equipment
    parameters:
      - in: path
        name: eq_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            category:
              type: string
            daily_rate:
              type: number
            quantity:
              type: integer
            description:
              type: string
            available:
              type: boolean
    responses:
      200:
        description: Equipment updated successfully
      404:
        description: Equipment not found
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    result = db.update_equipment(eq_id, data)
    if not result:
        return jsonify({"error": "Equipment not found"}), 404
    return jsonify(result), 200


@api_bp.route("/api/equipment/<int:eq_id>", methods=["DELETE"])
def api_delete_equipment(eq_id: int) -> tuple[Response, int]:
    """
    Delete an equipment item.
    ---
    tags:
      - Equipment
    parameters:
      - in: path
        name: eq_id
        type: integer
        required: true
    responses:
      200:
        description: Equipment deleted
      404:
        description: Equipment not found
    """
    if db.delete_equipment(eq_id):
        return jsonify({"message": "Equipment deleted"}), 200
    return jsonify({"error": "Equipment not found"}), 404


# ===================== Customers API =====================


@api_bp.route("/api/customers", methods=["GET"])
def api_get_customers() -> tuple[Response, int]:
    """
    List all customers.
    ---
    tags:
      - Customers
    responses:
      200:
        description: Array of all customers
    """
    return jsonify(db.get_all_customers()), 200


@api_bp.route("/api/customers", methods=["POST"])
def api_create_customer() -> tuple[Response, int]:
    """
    Create a new customer.
    ---
    tags:
      - Customers
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - name
            - email
            - phone
          properties:
            name:
              type: string
            email:
              type: string
            phone:
              type: string
    responses:
      201:
        description: Customer created
      400:
        description: Invalid input
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    errors = []
    if not data.get("name"):
        errors.append("Name is required")
    email = data.get("email", "")
    if not email:
        errors.append("Email is required")
    elif "@" not in email or "." not in email:
        errors.append("Invalid email format")
    elif not db.is_email_unique(email):
        errors.append("Email already registered")
    if not data.get("phone"):
        errors.append("Phone is required")

    if errors:
        return jsonify({"error": ", ".join(errors)}), 400

    cust = db.create_customer(data)
    return jsonify(cust), 201


@api_bp.route("/api/customers/<int:cust_id>", methods=["PUT"])
def api_update_customer(cust_id: int) -> tuple[Response, int]:
    """
    Update a customer.
    ---
    tags:
      - Customers
    parameters:
      - in: path
        name: cust_id
        type: integer
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
            email:
              type: string
            phone:
              type: string
    responses:
      200:
        description: Customer updated
      404:
        description: Customer not found
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # Check email uniqueness if email is being changed
    email = data.get("email")
    if email and not db.is_email_unique(email, exclude_id=cust_id):
        return jsonify({"error": "Email already registered"}), 400

    result = db.update_customer(cust_id, data)
    if not result:
        return jsonify({"error": "Customer not found"}), 404
    return jsonify(result), 200


@api_bp.route("/api/customers/<int:cust_id>", methods=["DELETE"])
def api_delete_customer(cust_id: int) -> tuple[Response, int]:
    """
    Delete a customer.
    ---
    tags:
      - Customers
    parameters:
      - in: path
        name: cust_id
        type: integer
        required: true
    responses:
      200:
        description: Customer deleted
      400:
        description: Customer has active rentals
      404:
        description: Customer not found
    """
    if db.has_active_rentals(cust_id):
        return jsonify(
            {"error": "Cannot delete customer with active rentals"}
        ), 400

    if db.delete_customer(cust_id):
        return jsonify({"message": "Customer deleted"}), 200
    return jsonify({"error": "Customer not found"}), 404


# ===================== Rentals API =====================


@api_bp.route("/api/rentals", methods=["GET"])
def api_get_rentals() -> tuple[Response, int]:
    """
    List all rentals.
    ---
    tags:
      - Rentals
    responses:
      200:
        description: Array of all rentals
    """
    return jsonify(db.get_all_rentals()), 200


@api_bp.route("/api/rentals", methods=["POST"])
def api_create_rental() -> tuple[Response, int]:
    """
    Create a new rental.
    ---
    tags:
      - Rentals
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          required:
            - equipment_id
            - customer_id
            - start_date
            - end_date
          properties:
            equipment_id:
              type: integer
            customer_id:
              type: integer
            start_date:
              type: string
              description: ISO date (YYYY-MM-DD)
            end_date:
              type: string
              description: ISO date (YYYY-MM-DD)
    responses:
      201:
        description: Rental created
      400:
        description: Invalid input
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    eq_id = data.get("equipment_id")
    cust_id = data.get("customer_id")
    start_date = data.get("start_date", "")
    end_date = data.get("end_date", "")

    errors = []
    if not eq_id:
        errors.append("Equipment ID is required")
    elif not db.get_equipment_by_id(eq_id):
        errors.append("Equipment not found")

    if not cust_id:
        errors.append("Customer ID is required")
    elif not db.get_customer_by_id(cust_id):
        errors.append("Customer not found")

    days = 0
    if not start_date or not end_date:
        errors.append("Start and end dates are required")
    else:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            days = (end - start).days
            if days <= 0:
                errors.append("End date must be after start date")
        except ValueError:
            errors.append("Invalid date format")

    if not errors and eq_id:
        if db.check_overlap(eq_id, start_date, end_date):
            errors.append("Equipment already booked for these dates")

    if errors:
        return jsonify({"error": ", ".join(errors)}), 400

    # Compute total cost (eq validated above, always exists)
    eq = db.get_equipment_by_id(eq_id)
    total_cost = eq["daily_rate"] * days  # type: ignore

    rental = db.create_rental(
        {
            "equipment_id": eq_id,
            "customer_id": cust_id,
            "start_date": start_date,
            "end_date": end_date,
            "total_cost": total_cost,
        }
    )
    return jsonify(rental), 201


@api_bp.route("/api/rentals/<int:rental_id>/return", methods=["PUT"])
def api_mark_returned(rental_id: int) -> tuple[Response, int]:
    """
    Mark a rental as returned.
    ---
    tags:
      - Rentals
    parameters:
      - in: path
        name: rental_id
        type: integer
        required: true
    responses:
      200:
        description: Rental marked as returned
      404:
        description: Rental not found or already returned
    """
    result = db.mark_rental_returned(rental_id)
    if result:
        return jsonify(result), 200
    return jsonify({"error": "Rental not found or already returned"}), 404
