


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
