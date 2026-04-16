# equipment.py - Equipment blueprint with CRUD routes
# TechRent Pro - Equipment Rental Platform

from flask import (
    Blueprint,
    render_template,
    request,
    abort,
    flash,
    redirect,
    url_for,
)

from werkzeug.wrappers import Response

import db

equipment_bp = Blueprint("equipment", __name__)

def validate_equipment_form(
    form_data: dict,
) -> tuple[dict, dict]:
    """
    Validate equipment form data server-side.

    Args:
        form_data: Flask request.form dict.

    Returns:
        tuple[dict, dict]: (cleaned_data, errors).
    """
    errors = {}
    cleaned = {}

    name = form_data.get("name", "").strip()
    if not name:
        errors["name"] = "Name is required"
    cleaned["name"] = name

    category = form_data.get("category", "").strip()
    if not category:
        errors["category"] = "Category is required"
    cleaned["category"] = category

    description = form_data.get("description", "").strip()
    cleaned["description"] = description

    try:
        daily_rate = float(form_data.get("daily_rate", 0))
        if daily_rate <= 0:
            errors["daily_rate"] = "Daily rate must be greater than 0"
        cleaned["daily_rate"] = daily_rate
    except (ValueError, TypeError):
        errors["daily_rate"] = "Daily rate must be a valid number"
        cleaned["daily_rate"] = form_data.get("daily_rate", "")

    try:
        quantity = int(form_data.get("quantity", 0))
        if quantity < 1:
            errors["quantity"] = "Quantity must be at least 1"
        cleaned["quantity"] = quantity
    except (ValueError, TypeError):
        errors["quantity"] = "Quantity must be a valid number"
        cleaned["quantity"] = form_data.get("quantity", "")

    cleaned["available"] = form_data.get("available") == "on"

    return cleaned, errors


@equipment_bp.route("/equipment")
def equipment_list() -> str:
    """
    List all equipment with optional filtering.

    Returns:
        str: Rendered equipment/list.html.
    """
    category = request.args.get("category", "")
    search = request.args.get("search", "").strip()

    items = db.get_all_equipment()

    if category:
        items = [
            equipment
            for equipment in items
            if equipment["category"] == category
        ]
    if search:
        items = [
            equipment
            for equipment in items
            if search.lower() in equipment["name"].lower()
        ]

    categories = db.get_equipment_categories()
    return render_template(
        "equipment/list.html",
        equipment_list=items,
        categories=categories,
        selected_category=category,
        search_query=search,
    )



@equipment_bp.route("/equipment/<int:eq_id>")
def equipment_detail(eq_id: int) -> str:
    """
    Show detail page for a single equipment item.

    Args:
        eq_id (int): The equipment ID.

    Returns:
        str: Rendered equipment/detail.html or 404.
    """
    item = db.get_equipment_by_id(eq_id)
    if not item:
        abort(404)

    history = db.get_rentals_for_equipment(eq_id)
    active_count = sum(1 for rental in history if rental["status"] == "active")
    available_qty = item["quantity"] - active_count

    return render_template(
        "equipment/detail.html",
        equipment=item,
        history=history,
        available_qty=available_qty,
    )



@equipment_bp.route("/equipment/new")
def equipment_new_form() -> str:
    """
    Show empty form for creating new equipment.

    Returns:
        str: Rendered equipment/form.html in create mode.
    """
    categories = db.get_equipment_categories()
    return render_template(
        "equipment/form.html",
        equipment=None,
        errors={},
        categories=categories,
        form_data={},
    )

@equipment_bp.route("/equipment/new", methods=["POST"])
def equipment_new_submit() -> str | Response:
    """
    Handle new equipment form submission.

    Returns:
        str: Redirect on success, re-render form on error.
    """
    cleaned, errors = validate_equipment_form(request.form)

    if errors:
        categories = db.get_equipment_categories()
        return render_template(
            "equipment/form.html",
            equipment=None,
            errors=errors,
            categories=categories,
            form_data=cleaned,
        )

    db.create_equipment(cleaned)
    flash("Equipment added successfully!", "success")
    return redirect(url_for("equipment.equipment_list"))



@equipment_bp.route("/equipment/<int:eq_id>/edit")
def equipment_edit_form(eq_id: int) -> str:
    """
    Show pre-filled form for editing equipment.

    Args:
        eq_id (int): The equipment ID.

    Returns:
        str: Rendered equipment/form.html in edit mode.
    """
    item = db.get_equipment_by_id(eq_id)
    if not item:
        abort(404)

    categories = db.get_equipment_categories()
    return render_template(
        "equipment/form.html",
        equipment=item,
        errors={},
        categories=categories,
        form_data={},
    )


@equipment_bp.route("/equipment/<int:eq_id>/edit", methods=["POST"])
def equipment_edit_submit(eq_id: int) -> str | Response:
    """
    Handle equipment edit form submission.

    Args:
        eq_id (int): The equipment ID.

    Returns:
        str: Redirect on success, re-render on error.
    """
    item = db.get_equipment_by_id(eq_id)
    if not item:
        abort(404)

    cleaned, errors = validate_equipment_form(request.form)

    if errors:
        categories = db.get_equipment_categories()
        return render_template(
            "equipment/form.html",
            equipment=item,
            errors=errors,
            categories=categories,
            form_data=cleaned,
        )

    db.update_equipment(eq_id, cleaned)
    flash("Equipment updated successfully!", "success")
    return redirect(url_for("equipment.equipment_detail", eq_id=eq_id))


@equipment_bp.route("/equipment/<int:eq_id>/delete", methods=["POST"])
def equipment_delete(eq_id: int) -> Response:
    """
    Delete an equipment item.

    Args:
        eq_id (int): The equipment ID.

    Returns:
        str: Redirect to equipment list.
    """
    # Check for active rentals before deleting
    active = [
        rental
        for rental in db.get_rentals_for_equipment(eq_id)
        if rental["status"] == "active"
    ]
    if active:
        flash(
            "Cannot delete equipment with active rentals.",
            "danger",
        )
    elif db.delete_equipment(eq_id):
        flash("Equipment deleted successfully!", "success")
    else:
        flash("Equipment not found.", "danger")
    return redirect(url_for("equipment.equipment_list"))
