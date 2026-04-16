# equipment.py - Equipment blueprint with CRUD routes
# TechRent Pro - Equipment Rental Platform

from flask import (
    Blueprint,
    render_template,
    request,
    abort,
)

import db

equipment_bp = Blueprint("equipment", __name__)


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
