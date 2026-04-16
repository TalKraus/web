# rentals.py - Rental blueprint with CRUD routes
# TechRent Pro - Equipment Rental Platform

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from werkzeug.wrappers import Response

import db

rentals_bp = Blueprint("rentals", __name__)


@rentals_bp.route("/rentals")
def rental_list() -> str:
    """
    List all rentals with optional status filtering.

    Returns:
        str: Rendered rentals/list.html.
    """
    status_filter = request.args.get("status", "all")
    rentals = db.get_all_rentals()

    # Resolve names
    enriched = []
    for rental in rentals:
        entry = dict(rental)
        customer = db.get_customer_by_id(rental["customer_id"])
        equipment = db.get_equipment_by_id(rental["equipment_id"])
        entry["customer_name"] = customer["name"] if customer else "Unknown"
        entry["equipment_name"] = equipment["name"] if equipment else "Unknown"
        enriched.append(entry)

    if status_filter != "all":
        enriched = [
            rental for rental in enriched if rental["status"] == status_filter
        ]

    return render_template(
        "rentals/list.html",
        rentals=enriched,
        selected_status=status_filter,
    )


@rentals_bp.route("/rentals/new")
def rental_new_form() -> str:
    """
    Show form for creating a new rental.

    Returns:
        str: Rendered rentals/form.html.
    """
    equipment = db.get_available_equipment_for_rental()
    customers = db.get_all_customers()
    return render_template(
        "rentals/form.html",
        equipment_list=equipment,
        customers=customers,
        errors={},
        form_data={},
    )


@rentals_bp.route("/rentals/new", methods=["POST"])
def rental_new_submit() -> str | Response:
    """
    Handle new rental form submission.

    Returns:
        str: Redirect on success, re-render on error.
    """
    errors = {}
    form_data = {}

    customer_id = request.form.get("customer_id", "")
    equipment_id = request.form.get("equipment_id", "")
    start_date = request.form.get("start_date", "")
    end_date = request.form.get("end_date", "")

    form_data["customer_id"] = customer_id
    form_data["equipment_id"] = equipment_id
    form_data["start_date"] = start_date
    form_data["end_date"] = end_date

    if not customer_id:
        errors["customer_id"] = "Customer is required"
    elif not db.get_customer_by_id(int(customer_id)):
        errors["customer_id"] = "Customer not found"
    if not equipment_id:
        errors["equipment_id"] = "Equipment is required"
    elif not db.get_equipment_by_id(int(equipment_id)):
        errors["equipment_id"] = "Equipment not found"
    if not start_date:
        errors["start_date"] = "Start date is required"
    if not end_date:
        errors["end_date"] = "End date is required"

    days = 0
    if not errors:
        try:
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            days = (end - start).days
            if days <= 0:
                errors["end_date"] = "End date must be after start date"
        except ValueError:
            errors["start_date"] = "Invalid date format"

    if not errors:
        eq_id = int(equipment_id)
        if db.check_overlap(eq_id, start_date, end_date):
            errors["equipment_id"] = (
                "This equipment is already booked for the selected dates"
            )

    if errors:
        equipment = db.get_available_equipment_for_rental()
        customers = db.get_all_customers()
        return render_template(
            "rentals/form.html",
            equipment_list=equipment,
            customers=customers,
            errors=errors,
            form_data=form_data,
        )

    # Compute total cost
    eq = db.get_equipment_by_id(int(equipment_id))
    total_cost = eq["daily_rate"] * days  # type: ignore

    db.create_rental(
        {
            "equipment_id": int(equipment_id),
            "customer_id": int(customer_id),
            "start_date": start_date,
            "end_date": end_date,
            "total_cost": total_cost,
        }
    )
    flash("Rental created successfully!", "success")
    return redirect(url_for("rentals.rental_list"))


@rentals_bp.route("/rentals/<int:rental_id>/return", methods=["POST"])
def rental_mark_returned(rental_id: int) -> Response:
    """
    Mark a rental as returned.

    Args:
        rental_id (int): The rental ID.

    Returns:
        str: Redirect to rental list.
    """
    result = db.mark_rental_returned(rental_id)
    if result:
        flash("Rental marked as returned!", "success")
    else:
        flash(
            "Rental not found or already returned.",
            "danger",
        )
    return redirect(url_for("rentals.rental_list"))
