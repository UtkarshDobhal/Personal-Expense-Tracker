import streamlit as st
import requests
from datetime import date

# Define the types of expenses
permanent_expenses_default = ["Rent", "Utilities", "Healthcare", "EMI", "Mortgage"]
variable_expenses_default = ["Shopping", "Travel", "Personal", "Petrol"]

# Session state to track user login and name
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'user_data' not in st.session_state:
    st.session_state['user_data'] = {}

# Function to send user data and create expense CSV files
def create_expense_files(user_data):
    response = requests.post('http://127.0.0.1:5000/create_expense_files', json=user_data)
    return response.status_code == 200

# Login Page
if not st.session_state['logged_in']:
    st.title("Login")
    name = st.text_input("Enter your name")
    dob = st.date_input("Enter your date of birth", format="DD/MM/YYYY")
    gender = st.text_input("Enter your gender")
    income = st.number_input("Enter your income")

    # Convert the date to string in the format "YYYY-MM-DD"
    dob_str = dob.strftime("%Y-%m-%d")

    user_data = {"name": name, "dob": dob_str, "gender": gender, "income": income}

    if st.button("Submit"):
        if name:
            # Send the user data (name, dob, gender, income) to Flask backend
            if create_expense_files(user_data):
                st.success("Files created, proceeding to the expense page...")
                st.session_state['logged_in'] = True
                st.session_state['user_data'] = user_data
            else:
                st.error("Failed to create files. Try again.")
else:
    st.title(f"Welcome, {st.session_state['user_data']['name']}")
    st.header("Add Type of Expense")

    # Checkbox menu for permanent expenses
    st.subheader("Permanent Expenses")
    selected_permanent_expenses = st.multiselect(
        "Select permanent expenses:", permanent_expenses_default
    )

    # Option to add custom permanent expense
    custom_permanent = st.text_input("Add a custom permanent expense (if any):")
    if custom_permanent:
        selected_permanent_expenses.append(custom_permanent)

    # Checkbox menu for variable expenses
    st.subheader("Variable Expenses")
    selected_variable_expenses = st.multiselect(
        "Select variable expenses:", variable_expenses_default
    )

    # Option to add custom variable expense
    custom_variable = st.text_input("Add a custom variable expense (if any):")
    if custom_variable:
        selected_variable_expenses.append(custom_variable)

    # Button to submit the data to Flask backend
    if st.button("Submit Expenses"):
        # Prepare the data to send to the backend
        data = {
            "name": st.session_state['user_data']['name'],
            "dob": st.session_state['user_data']['dob'],
            "gender": st.session_state['user_data']['gender'],
            "income": st.session_state['user_data']['income'],
            "permanent_expenses": selected_permanent_expenses,
            "variable_expenses": selected_variable_expenses
        }

        # Send the data to the Flask backend using a POST request
        response = requests.post('http://127.0.0.1:5000/add_expenses', json=data)

        # Check the response from Flask
        if response.status_code == 200:
            st.success("Expenses successfully submitted and saved!")
        else:
            st.error("Failed to submit expenses.")
