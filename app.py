import streamlit as st
import pandas as pd
from datetime import datetime
import openpyxl

# Initialize data (mock data for menu and inventory)
menu = {
    "Americano": 5.00,
    "Cappuccino": 6.00,
    "Latte": 6.50,
    "Caramel Macchiato": 7.00
}

default_inventory = {
    "coffee_beans": 1000,  # grams
    "milk": 500,           # ml
    "sugar": 200,          # grams
    "cups": 100            # count
}

# Initialize session state for order history, inventory, and login status
if "order_history" not in st.session_state:
    st.session_state["order_history"] = []
if "inventory" not in st.session_state:
    st.session_state["inventory"] = default_inventory.copy()
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "is_customer" not in st.session_state:
    st.session_state["is_customer"] = False
if "is_admin" not in st.session_state:
    st.session_state["is_admin"] = False

# Function to save data to an Excel file
def save_data_to_excel():
    with pd.ExcelWriter("coffee_shop_data.xlsx", engine="openpyxl", mode="w") as writer:
        # Save order history
        if st.session_state["order_history"]:
            order_df = pd.DataFrame(st.session_state["order_history"])
            order_df.to_excel(writer, sheet_name="Order History", index=False)
        
        # Save inventory
        inventory_df = pd.DataFrame(st.session_state["inventory"].items(), columns=["Item", "Quantity"])
        inventory_df.to_excel(writer, sheet_name="Inventory", index=False)

        st.success("Data saved to 'coffee_shop_data.xlsx' successfully!")

# Role selection buttons
st.sidebar.write("Select your role:")
if st.sidebar.button("Customer"):
    st.session_state["is_customer"] = True
    st.session_state["is_admin"] = False
    st.session_state["logged_in"] = True
    st.session_state["user_role"] = "customer"
    st.sidebar.success("Customer Access Granted")

if st.sidebar.button("Admin"):
    st.session_state["is_admin"] = True
    st.session_state["is_customer"] = False

# Show admin login fields if "Admin" button was clicked
if st.session_state["is_admin"]:
    username = st.sidebar.text_input("Username", key="admin_username")
    password = st.sidebar.text_input("Password", type="password", key="admin_password")
    if st.sidebar.button("Login as Admin"):
        if username == "admin" and password == "admin123":
            st.session_state["logged_in"] = True
            st.session_state["user_role"] = "admin"
            st.sidebar.success("Admin Access Granted")
        else:
            st.sidebar.error("Invalid admin credentials.")
            st.session_state["is_admin"] = False  # Reset admin flag if login fails

# App title
st.title("Coffee Shop App")

# Customer Order Process
if st.session_state["logged_in"] and st.session_state["user_role"] == "customer":
    st.subheader("Place Your Order")

    coffee_type = st.selectbox("Select Coffee Type", list(menu.keys()))
    coffee_size = st.radio("Choose Size", ("Small", "Medium", "Large"))
    add_ons = st.multiselect("Add-ons", ["Extra sugar", "Milk"])

    if st.button("Place Order"):
        order = {
            "coffee_type": coffee_type,
            "size": coffee_size,
            "add_ons": add_ons,
            "price": menu[coffee_type],
            "order_time": datetime.now()
        }
        st.session_state["order_history"].append(order)
        st.success(f"Order placed! Your coffee will be ready shortly. Order: {coffee_type} ({coffee_size})")

        # Update Inventory based on order (basic example)
        st.session_state["inventory"]["coffee_beans"] -= 10  # Adjust amount as per recipe
        st.session_state["inventory"]["cups"] -= 1

# Inventory Management (Admin Only)
if st.session_state["logged_in"] and st.session_state["user_role"] == "admin":
    st.subheader("Inventory Management")

    # Display current inventory levels
    st.write("Inventory Levels")
    for item, qty in st.session_state["inventory"].items():
        st.write(f"{item.capitalize()}: {qty} units")

    # Low stock alert
    for item, qty in st.session_state["inventory"].items():
        if qty < 20:
            st.warning(f"Low stock alert: {item}")

    # Update inventory
    item_to_restock = st.selectbox("Item to Restock", list(st.session_state["inventory"].keys()))
    restock_amount = st.number_input("Restock Amount", min_value=1)
    if st.button("Restock Inventory"):
        st.session_state["inventory"][item_to_restock] += restock_amount
        st.success(f"{item_to_restock.capitalize()} restocked successfully.")

    # Button to save data to Excel
    if st.button("Save Data to Excel"):
        save_data_to_excel()

# Sales Reporting (Admin Only)
if st.session_state["logged_in"] and st.session_state["user_role"] == "admin":
    st.subheader("Sales Reporting")

    # Display total sales
    sales_df = pd.DataFrame(st.session_state["order_history"])
    st.write("Total Sales Data")
    st.dataframe(sales_df)

    # Sales Breakdown by Coffee Type
    if not sales_df.empty:
        sales_summary = sales_df["coffee_type"].value_counts()
        st.bar_chart(sales_summary)

        # Total Profit Calculation (mock example)
        total_sales = sum(order["price"] for order in st.session_state["order_history"])
        st.write(f"Total Revenue: ${total_sales}")

# Customer Feedback
if st.session_state["logged_in"] and st.session_state["user_role"] == "customer":
    st.subheader("Feedback")
    feedback = st.text_area("Rate your experience with us!")
    if st.button("Submit Feedback"):
        st.success("Thank you for your feedback!")
