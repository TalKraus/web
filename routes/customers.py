# customers.py - Customer blueprint with CRUD routes
# TechRent Pro - Equipment Rental Platform

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    url_for,
)
from werkzeug.wrappers import Response

import db

customers_bp = Blueprint("customers", __name__)


def validate_customer_form(
    form_data: dict, exclude_id: int | None = None
) -> tuple[dict, dict]:
    """
    Validate customer form data server-side.

    Args:
        form_data: Flask request.form dict.
        exclude_id (int or None): Customer ID to exclude
                                  from email uniqueness check.

    Returns:
        tuple[dict, dict]: (cleaned_data, errors).
    """
    errors = {}
    cleaned = {}

    name = form_data.get("name", "").strip()
    if not name:
        errors["name"] = "Name is required"
    cleaned["name"] = name

    email = form_data.get("email", "").strip()
    if not email:
        errors["email"] = "Email is required"
    elif "@" not in email or "." not in email:
        errors["email"] = "Please enter a valid email address"
    elif not db.is_email_unique(email, exclude_id=exclude_id):
        errors["email"] = "This email is already registered"
    cleaned["email"] = email

    phone = form_data.get("phone", "").strip()
    if not phone:
        errors["phone"] = "Phone is required"
    cleaned["phone"] = phone

    return cleaned, errors


@customers_bp.route("/customers")
def customer_list() -> str:
    """
    List all customers with optional search.

    Returns:
        str: Rendered customers/list.html.
    """
    search = request.args.get("search", "").strip()
    customers = db.get_all_customers()

    if search:
        customers = [
            customer
            for customer in customers
            if search.lower() in customer["name"].lower()
            or search.lower() in customer["email"].lower()
        ]

    return render_template(
        "customers/list.html",
        customers=customers,
        search_query=search,
    )


@customers_bp.route("/customers/new")
def customer_new_form() -> str:
    """
    Show empty form for registering a new customer.

    Returns:
        str: Rendered customers/form.html in create mode.
    """
    return render_template(
        "customers/form.html",
        customer=None,
        errors={},
        form_data={},
    )


@customers_bp.route("/customers/new", methods=["POST"])
def customer_new_submit() -> str | Response:
    """
    Handle new customer form submission.

    Returns:
        str: Redirect on success, re-render on error.
    """
    cleaned, errors = validate_customer_form(request.form)

    if errors:
        return render_template(
            "customers/form.html",
            customer=None,
            errors=errors,
            form_data=cleaned,
        )

    db.create_customer(cleaned)
    flash("Customer registered successfully!", "success")
    return redirect(url_for("customers.customer_list"))


@customers_bp.route("/customers/<int:cust_id>/edit")
def customer_edit_form(cust_id: int) -> str:
    """
    Show pre-filled form for editing a customer.

    Args:
        cust_id (int): The customer ID.

    Returns:
        str: Rendered customers/form.html in edit mode.
    """
    customer = db.get_customer_by_id(cust_id)
    if not customer:
        abort(404)

    return render_template(
        "customers/form.html",
        customer=customer,
        errors={},
        form_data={},
    )


@customers_bp.route("/customers/<int:cust_id>/edit", methods=["POST"])
def customer_edit_submit(cust_id: int) -> str | Response:
    """
    Handle customer edit form submission.

    Args:
        cust_id (int): The customer ID.

    Returns:
        str: Redirect on success, re-render on error.
    """
    customer = db.get_customer_by_id(cust_id)
    if not customer:
        abort(404)

    cleaned, errors = validate_customer_form(request.form, exclude_id=cust_id)

    if errors:
        return render_template(
            "customers/form.html",
            customer=customer,
            errors=errors,
            form_data=cleaned,
        )

    db.update_customer(cust_id, cleaned)
    flash("Customer updated successfully!", "success")
    return redirect(url_for("customers.customer_list"))


@customers_bp.route("/customers/<int:cust_id>/delete", methods=["POST"])
def customer_delete(cust_id: int) -> Response:
    """
    Delete a customer.

    Args:
        cust_id (int): The customer ID.

    Returns:
        str: Redirect to customer list.
    """
    if db.has_active_rentals(cust_id):
        flash(
            "Cannot delete customer with active rentals.",
            "danger",
        )
    elif db.delete_customer(cust_id):
        flash("Customer deleted successfully!", "success")
    else:
        flash("Customer not found.", "danger")
    return redirect(url_for("customers.customer_list"))
