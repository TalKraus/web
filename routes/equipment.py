# equipment.py - Equipment blueprint with CRUD routes
# TechRent Pro - Equipment Rental Platform

from flask import (
    Blueprint,
    render_template,
    request,
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
