
# db.py - In-memory database with seed data and CRUD functions
# TechRent Pro - Equipment Rental Platform

from datetime import datetime


# --- Seed Data ---

equipment_db = [
    {
        "id": 1,
        "name": "DJI Drone 4K Pro",
        "category": "Drone",
        "daily_rate": 85.00,
        "quantity": 3,
        "description": "Professional 4K drone for aerial photography.",
        "available": True,
    },
    {
        "id": 2,
        "name": "Canon EOS R5",
        "category": "Camera",
        "daily_rate": 120.00,
        "quantity": 2,
        "description": "Full-frame mirrorless camera with 8K video.",
        "available": True,
    },
    {
        "id": 3,
        "name": "MacBook Pro M3",
        "category": "Laptop",
        "daily_rate": 65.00,
        "quantity": 5,
        "description": "16-inch laptop for video editing and dev.",
        "available": True,
    },
    {
        "id": 4,
        "name": "Meta Quest 3",
        "category": "VR Headset",
        "daily_rate": 45.00,
        "quantity": 4,
        "description": "Mixed reality headset for VR experiences.",
        "available": True,
    },
    {
        "id": 5,
        "name": "Rode NT1 Kit",
        "category": "Audio",
        "daily_rate": 30.00,
        "quantity": 6,
        "description": "Studio condenser microphone with shock mount.",
        "available": True,
    },
    {
        "id": 6,
        "name": "Aputure 300d II",
        "category": "Lighting",
        "daily_rate": 55.00,
        "quantity": 3,
        "description": "Professional LED light for film production.",
        "available": True,
    },
]

customers_db = [
    {
        "id": 1,
        "name": "Alice Torres",
        "email": "alice@example.com",
        "phone": "555-1001",
        "created_at": "2025-01-15",
    },
    {
        "id": 2,
        "name": "Bob Lee",
        "email": "bob@example.com",
        "phone": "555-1002",
        "created_at": "2025-02-10",
    },
    {
        "id": 3,
        "name": "Carol Mejia",
        "email": "carol@example.com",
        "phone": "555-1003",
        "created_at": "2025-03-01",
    },
    {
        "id": 4,
        "name": "David Kim",
        "email": "david@example.com",
        "phone": "555-1004",
        "created_at": "2025-03-05",
    },
]

# Rental 1: active (6 days, 85*6=510)
# Rental 2: returned (5 days, 120*5=600)
# Rental 3: overdue (3 days, 65*3=195)
rentals_db = [
    {
        "id": 1,
        "equipment_id": 1,
        "customer_id": 1,
        "start_date": "2025-04-01",
        "end_date": "2025-04-07",
        "status": "active",
        "total_cost": 510.00,
    },
    {
        "id": 2,
        "equipment_id": 2,
        "customer_id": 2,
        "start_date": "2025-03-10",
        "end_date": "2025-03-15",
        "status": "returned",
        "total_cost": 600.00,
    },
    {
        "id": 3,
        "equipment_id": 3,
        "customer_id": 3,
        "start_date": "2025-03-20",
        "end_date": "2025-03-23",
        "status": "overdue",
        "total_cost": 195.00,
    },
]

_next_equipment_id = 7
_next_customer_id = 5
_next_rental_id = 4



def get_dashboard_stats() -> dict:
    """
    Get summary statistics for the dashboard.

    Returns:
        dict: Keys - total_equipment, available_equipment,
              active_rentals, total_customers.
    """
    total_eq = len(equipment_db)
    available_eq = sum(1 for item in equipment_db if item["available"])
    active = sum(1 for rental in rentals_db if rental["status"] == "active")
    total_cust = len(customers_db)
    return {
        "total_equipment": total_eq,
        "available_equipment": available_eq,
        "active_rentals": active,
        "total_customers": total_cust,
    }

# ===================== Rental Functions =====================

def get_recent_rentals(limit: int = 5) -> list[dict]:
    """
    Get the most recent rentals with names resolved.

    Args:
        limit (int): Max number of rentals to return.

    Returns:
        list[dict]: Rentals sorted by ID desc, with
                    customer_name and equipment_name.
    """
    sorted_rentals = sorted(
        rentals_db,
        key=lambda rental: rental["id"],
        reverse=True,
    )
    results = []
    for rental in sorted_rentals[:limit]:
        entry = dict(rental)
        cust = get_customer_by_id(rental["customer_id"])
        eq = get_equipment_by_id(rental["equipment_id"])
        entry["customer_name"] = cust["name"] if cust else "Unknown"
        entry["equipment_name"] = eq["name"] if eq else "Unknown"
        results.append(entry)
    return results

def get_all_rentals() -> list[dict]:
    """
    Return all rentals.

    Returns:
        list[dict]: List of all rental dicts.
    """
    return list(rentals_db)


def get_rental_by_id(rental_id: int) -> dict | None:
    """
    Find a single rental by ID.

    Args:
        rental_id (int): The rental ID.

    Returns:
        dict or None: The rental dict, or None.
    """
    for rental in rentals_db:
        if rental["id"] == rental_id:
            return dict(rental)
    return None


def create_rental(data: dict) -> dict:
    """
    Create a new rental.

    Args:
        data (dict): Must contain equipment_id, customer_id,
                     start_date, end_date, total_cost.

    Returns:
        dict: The newly created rental dict.
    """
    global _next_rental_id
    new_rental = {
        "id": _next_rental_id,
        "equipment_id": int(data["equipment_id"]),
        "customer_id": int(data["customer_id"]),
        "start_date": data["start_date"],
        "end_date": data["end_date"],
        "status": "active",
        "total_cost": float(data["total_cost"]),
    }
    _next_rental_id += 1
    rentals_db.append(new_rental)
    return dict(new_rental)


def mark_rental_returned(rental_id: int) -> dict | None:
    """
    Mark a rental as returned.

    Args:
        rental_id (int): The rental ID.

    Returns:
        dict or None: Updated rental, or None if not found
                      or already returned.
    """
    for rental in rentals_db:
        if rental["id"] == rental_id:
            if rental["status"] == "returned":
                return None
            rental["status"] = "returned"
            return dict(rental)
    return None


def get_rentals_for_equipment(eq_id: int) -> list[dict]:
    """
    Get all rentals for a specific equipment item.

    Args:
        eq_id (int): The equipment ID.

    Returns:
        list[dict]: Rentals with customer_name added.
    """
    results = []
    for rental in rentals_db:
        if rental["equipment_id"] == eq_id:
            entry = dict(rental)
            customer = get_customer_by_id(int(rental["customer_id"]))
            entry["customer_name"] = (
                customer["name"] if customer else "Unknown"
            )
            results.append(entry)
    return results


def get_rentals_for_customer(cust_id: int) -> list[dict]:
    """
    Get all rentals for a specific customer.

    Args:
        cust_id (int): The customer ID.

    Returns:
        list[dict]: Rentals with equipment_name added.
    """
    results = []
    for rental in rentals_db:
        if rental["customer_id"] == cust_id:
            entry = dict(rental)
            equipment = get_equipment_by_id(int(rental["equipment_id"]))
            entry["equipment_name"] = (
                equipment["name"] if equipment else "Unknown"
            )
            results.append(entry)
    return results


def has_active_rentals(customer_id: int) -> bool:
    """
    Check if a customer has any active rentals.

    Args:
        customer_id (int): The customer ID.

    Returns:
        bool: True if the customer has active rentals.
    """
    for rental in rentals_db:
        if (
            rental["customer_id"] == customer_id
            and rental["status"] == "active"
        ):
            return True
    return False


def check_overlap(equipment_id: int, start_date: str, end_date: str) -> bool:
    """
    Check if a date range overlaps with any active rental
    for the given equipment. Accounts for equipment quantity
    so multi-unit items can be rented concurrently.

    Args:
        equipment_id (int): The equipment ID.
        start_date (str): ISO start date.
        end_date (str): ISO end date.

    Returns:
        bool: True if all units are booked (no availability).
    """
    eq = get_equipment_by_id(equipment_id)
    if not eq:
        return True
    overlap_count = sum(
        1
        for rental in rentals_db
        if rental["equipment_id"] == equipment_id
        and rental["status"] == "active"
        and start_date < str(rental["end_date"])
        and end_date > str(rental["start_date"])
    )
    return overlap_count >= int(eq["quantity"])



def get_available_equipment_for_rental() -> list[dict]:
    """
    Get equipment that is available for new rentals.
    Only returns items where available=True AND
    active rental count < quantity.

    Returns:
        list[dict]: Available equipment items.
    """
    # Count active rentals per equipment
    active_counts: dict[int, int] = {}
    for rental in rentals_db:
        if rental["status"] == "active":
            eq_id = int(rental["equipment_id"])
            active_counts[eq_id] = active_counts.get(eq_id, 0) + 1

    results = []
    for eq in equipment_db:
        if eq["available"]:
            active = active_counts.get(int(eq["id"]), 0)
            if active < int(eq["quantity"]):
                results.append(dict(eq))
    return results


# ===================== Equipment Functions =====================

def get_all_equipment() -> list[dict]:
    """
    Return all equipment items.

    Returns:
        list[dict]: List of all equipment dicts.
    """
    return list(equipment_db)


def get_equipment_by_id(eq_id: int) -> dict | None:
    """
    Find a single equipment item by its ID.

    Args:
        eq_id (int): The equipment ID to look up.

    Returns:
        dict or None: The equipment dict, or None if not found.
    """
    for item in equipment_db:
        if item["id"] == eq_id:
            return dict(item)
    return None

def get_equipment_categories() -> list[str]:
    """
    Get a sorted list of unique equipment categories.

    Returns:
        list[str]: Sorted unique category names.
    """
    cats: set[str] = {str(item["category"]) for item in equipment_db}
    return sorted(cats)


def create_equipment(data: dict) -> dict:
    """
    Create a new equipment item and add it to the database.

    Args:
        data (dict): Must contain name, category, daily_rate,
                     quantity, description, available.

    Returns:
        dict: The newly created equipment dict with auto ID.
    """
    global _next_equipment_id
    new_item = {
        "id": _next_equipment_id,
        "name": data["name"],
        "category": data["category"],
        "daily_rate": float(data["daily_rate"]),
        "quantity": int(data["quantity"]),
        "description": data.get("description", ""),
        "available": bool(data.get("available", True)),
    }
    _next_equipment_id += 1
    equipment_db.append(new_item)
    return dict(new_item)


def update_equipment(eq_id: int, data: dict) -> dict | None:
    """
    Update an existing equipment item.

    Args:
        eq_id (int): The ID of the item to update.
        data (dict): Fields to update.

    Returns:
        dict or None: Updated equipment dict, or None if not found.
    """
    for item in equipment_db:
        if item["id"] == eq_id:
            item["name"] = data.get("name", item["name"])
            item["category"] = data.get("category", item["category"])
            item["daily_rate"] = float(
                data.get("daily_rate", item["daily_rate"])
            )
            item["quantity"] = int(data.get("quantity", item["quantity"]))
            item["description"] = data.get(
                "description", item["description"]
            )
            if "available" in data:
                item["available"] = bool(data["available"])
            return dict(item)
    return None


def delete_equipment(eq_id: int) -> bool:
    """
    Delete an equipment item by ID.

    Args:
        eq_id (int): The ID of the item to delete.

    Returns:
        bool: True if deleted, False if not found.
    """
    for i, item in enumerate(equipment_db):
        if item["id"] == eq_id:
            equipment_db.pop(i)
            return True
    return False

# ===================== Customer Functions =====================

def get_all_customers() -> list[dict]:
    """
    Return all customers sorted by name.

    Returns:
        list[dict]: List of all customer dicts.
    """
    return sorted(customers_db, key=lambda c: c["name"])


def get_customer_by_id(cust_id: int) -> dict | None:
    """
    Find a single customer by ID.

    Args:
        cust_id (int): The customer ID.

    Returns:
        dict or None: The customer dict, or None if not found.
    """
    for cust in customers_db:
        if cust["id"] == cust_id:
            return dict(cust)
    return None


def create_customer(data: dict) -> dict:
    """
    Create a new customer.

    Args:
        data (dict): Must contain name, email, phone.

    Returns:
        dict: The newly created customer dict.
    """
    global _next_customer_id
    new_cust = {
        "id": _next_customer_id,
        "name": data["name"],
        "email": data["email"],
        "phone": data["phone"],
        "created_at": datetime.now().strftime("%Y-%m-%d"),
    }
    _next_customer_id += 1
    customers_db.append(new_cust)
    return dict(new_cust)


def update_customer(cust_id: int, data: dict) -> dict | None:
    """
    Update an existing customer.

    Args:
        cust_id (int): The customer ID.
        data (dict): Fields to update (name, email, phone).

    Returns:
        dict or None: Updated customer dict, or None.
    """
    for cust in customers_db:
        if cust["id"] == cust_id:
            cust["name"] = data.get("name", cust["name"])
            cust["email"] = data.get("email", cust["email"])
            cust["phone"] = data.get("phone", cust["phone"])
            return dict(cust)
    return None


def delete_customer(cust_id: int) -> bool:
    """
    Delete a customer by ID. Refuses if active rentals exist.

    Args:
        cust_id (int): The customer ID.

    Returns:
        bool: True if deleted, False if not found or has rentals.
    """
    if has_active_rentals(cust_id):
        return False
    for i, cust in enumerate(customers_db):
        if cust["id"] == cust_id:
            customers_db.pop(i)
            return True
    return False


def is_email_unique(email: str, exclude_id: int | None = None) -> bool:
    """
    Check if an email address is unique among customers.

    Args:
        email (str): The email to check.
        exclude_id (int or None): Customer ID to exclude (for edits).

    Returns:
        bool: True if the email is unique.
    """
    for cust in customers_db:
        cust_email = str(cust["email"])
        if cust_email.lower() == email.lower():
            if exclude_id is not None and cust["id"] == exclude_id:
                continue
            return False
    return True

# ===================== Report Functions =====================

def get_report_data() -> dict:
    """
    Get aggregated report data for the reports page.

    Returns:
        dict: total_revenue, active_revenue, top_equipment,
              top_customers, status_counts, total_rentals.
    """
    total_revenue = sum(
        rental["total_cost"]
        for rental in rentals_db
        if rental["status"] == "returned"
    )
    active_revenue = sum(
        rental["total_cost"]
        for rental in rentals_db
        if rental["status"] == "active"
    )

    # Status counts
    status_counts = {"active": 0, "returned": 0, "overdue": 0}
    for rental in rentals_db:
        if rental["status"] in status_counts:
            status_counts[rental["status"]] += 1

    # Top equipment by rental count
    eq_counts: dict[int, int] = {}
    for rental in rentals_db:
        eq_id = int(rental["equipment_id"])
        eq_counts[eq_id] = eq_counts.get(eq_id, 0) + 1
    top_eq = sorted(
        eq_counts.items(),
        key=lambda pair: pair[1],
        reverse=True,
    )[:3]
    top_equipment = []
    for eq_id, count in top_eq:
        eq = get_equipment_by_id(eq_id)
        top_equipment.append(
            {
                "name": eq["name"] if eq else "Unknown",
                "rental_count": count,
            }
        )

    # Top customers by total spend
    cust_spend: dict[int, float] = {}
    for rental in rentals_db:
        cid = int(rental["customer_id"])
        cust_spend[cid] = cust_spend.get(cid, 0) + float(rental["total_cost"])
    top_cust = sorted(
        cust_spend.items(),
        key=lambda pair: pair[1],
        reverse=True,
    )[:3]
    top_customers = []
    for cust_id, spend in top_cust:
        cust = get_customer_by_id(cust_id)
        top_customers.append(
            {
                "name": cust["name"] if cust else "Unknown",
                "total_spend": spend,
            }
        )

    return {
        "total_revenue": total_revenue,
        "active_revenue": active_revenue,
        "top_equipment": top_equipment,
        "top_customers": top_customers,
        "status_counts": status_counts,
        "total_rentals": len(rentals_db),
    }
