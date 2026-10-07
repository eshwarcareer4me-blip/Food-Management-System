"""Smart Food Management System.

Run with:
    streamlit run app.py
"""

from datetime import datetime

import streamlit as st

st.set_page_config(page_title="Smart Food Management System", layout="centered")

if "inventory" not in st.session_state:
    st.session_state.inventory = [
        {
            "id": "FD001",
            "name": "Milk",
            "category": "Dairy",
            "quantity": 10,
            "unit": "litres",
            "purchase_date": "2026-10-01",
            "expiry_date": "2026-10-03",
        },
        {
            "id": "FD002",
            "name": "Rice",
            "category": "Grains",
            "quantity": 25,
            "unit": "kg",
            "purchase_date": "2026-09-15",
            "expiry_date": "2027-09-15",
        },
    ]

if "role" not in st.session_state:
    st.session_state.role = None


def compute_expiry_status(item):
    today = datetime.now()
    expiry_date = datetime.strptime(item["expiry_date"], "%Y-%m-%d")
    delta_days = (expiry_date - today).days

    if delta_days < 0:
        return "EXPIRED", delta_days
    if 0 <= delta_days <= 3:
        return "EXPIRING SOON", delta_days
    return "AVAILABLE", delta_days


if st.session_state.role is None:
    st.title("Smart Food Management System")
    st.subheader("Login")
    username = st.text_input("Username", key="login_username")
    password = st.text_input("Password", type="password", key="login_password")

    if st.button("Login"):
        if username == "admin" and password == "admin123":
            st.session_state.role = "ADMIN"
            st.rerun()
        elif username == "employee" and password == "employee123":
            st.session_state.role = "EMPLOYEE"
            st.rerun()
        else:
            st.error("Invalid credentials")

else:
    st.title("Smart Food Management System")
    st.sidebar.write(f"Logged in as: **{st.session_state.role}**")

    if st.sidebar.button("Logout"):
        st.session_state.role = None
        st.rerun()

    menu_options = ["View Inventory", "Search Food", "Update Quantity", "Expiry Monitor"]
    if st.session_state.role == "ADMIN":
        menu_options.insert(0, "Add Food")
        menu_options.append("Remove Food")
        menu_options.append("Summary")

    choice = st.sidebar.selectbox("Navigation", menu_options)

    if choice == "View Inventory":
        st.header("Current Inventory")
        if not st.session_state.inventory:
            st.info("No items in inventory.")
        else:
            st.dataframe(st.session_state.inventory)

    elif choice == "Add Food":
        st.header("Add New Food Item")
        with st.form("add_food_form"):
            food_id = st.text_input("Food ID (e.g. FD003)", key="food_id").strip().upper()
            name = st.text_input("Food Name", key="food_name").strip().title()
            category = st.text_input("Category", key="food_category").strip().title()
            quantity = st.number_input("Quantity", min_value=1, step=1, key="food_quantity")
            unit = st.text_input("Unit (e.g. kg, litres, pcs)", key="food_unit").strip()
            purchase_date = st.date_input("Purchase Date", key="purchase_date")
            expiry_date = st.date_input("Expiry Date", key="expiry_date")
            submitted = st.form_submit_button("Add Item")

            if submitted:
                if not food_id or not name or not category or not unit:
                    st.error("Please fill in all fields before adding an item.")
                elif any(item["id"] == food_id for item in st.session_state.inventory):
                    st.error(f"Error: Food ID '{food_id}' already exists.")
                elif expiry_date < purchase_date:
                    st.error("Error: Expiry date cannot be before purchase date.")
                else:
                    st.session_state.inventory.append(
                        {
                            "id": food_id,
                            "name": name,
                            "category": category,
                            "quantity": int(quantity),
                            "unit": unit,
                            "purchase_date": str(purchase_date),
                            "expiry_date": str(expiry_date),
                        }
                    )
                    st.success(f"{name} added to inventory!")

    elif choice == "Search Food":
        st.header("Search Food")
        query = st.text_input("Enter Food Name or Category", key="search_query").strip().lower()
        if query:
            results = [
                item
                for item in st.session_state.inventory
                if query in item["name"].lower() or query in item["category"].lower()
            ]
            if results:
                st.dataframe(results)
            else:
                st.warning(f"No items found matching '{query}'.")

    elif choice == "Update Quantity":
        st.header("Update Quantity")
        item_ids = [item["id"] for item in st.session_state.inventory]
        if not item_ids:
            st.info("Inventory is empty.")
        else:
            selected_id = st.selectbox("Select Food ID to Update", item_ids, key="update_food_id")
            target_item = next(item for item in st.session_state.inventory if item["id"] == selected_id)
            st.write(f"**Current Quantity:** {target_item['quantity']} {target_item['unit']}")
            new_qty = st.number_input(
                "New Quantity",
                min_value=0,
                step=1,
                value=target_item["quantity"],
                key="update_quantity_value",
            )
            if st.button("Update"):
                target_item["quantity"] = int(new_qty)
                st.success(
                    f"Updated quantity for {target_item['name']} to {new_qty} {target_item['unit']}."
                )

    elif choice == "Remove Food":
        st.header("Remove Food Item")
        item_ids = [item["id"] for item in st.session_state.inventory]
        if not item_ids:
            st.info("Inventory is empty.")
        else:
            selected_id = st.selectbox("Select Food ID to Remove", item_ids, key="remove_food_id")
            if st.button("Delete Item"):
                st.session_state.inventory = [
                    item for item in st.session_state.inventory if item["id"] != selected_id
                ]
                st.success(f"Item {selected_id} removed.")
                st.rerun()

    elif choice == "Expiry Monitor":
        st.header("Expiry Status Monitor")
        monitored_list = []
        for item in st.session_state.inventory:
            status, delta = compute_expiry_status(item)
            monitored_list.append(
                {
                    "ID": item["id"],
                    "Name": item["name"],
                    "Days to Expiry": delta,
                    "Status": status,
                }
            )
        st.table(monitored_list)

    elif choice == "Summary":
        st.header("Inventory Summary Report")
        total_items = len(st.session_state.inventory)
        total_qty = sum(item["quantity"] for item in st.session_state.inventory)

        expired = 0
        expiring_soon = 0
        available = 0

        for item in st.session_state.inventory:
            status, delta = compute_expiry_status(item)
            if status == "EXPIRED":
                expired += 1
            elif status == "EXPIRING SOON":
                expiring_soon += 1
            else:
                available += 1

        col1, col2 = st.columns(2)
        col1.metric("Total Unique Items", total_items)
        col2.metric("Total Quantity", total_qty)

        st.write("---")
        st.write(f"- **Expired Items:** {expired}")
        st.write(f"- **Expiring Soon (0–3 days):** {expiring_soon}")
        st.write(f"- **Available Items:** {available}")
#

