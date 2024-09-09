import streamlit as st
import requests
from datetime import date
import yaml
import hashlib
import os

USER_DATA_FILE = './users.yaml'

# Function to hash passwords using SHA-256
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# Function to load user data from the YAML file
def load_user_data():
    if os.path.exists(USER_DATA_FILE):
        with open(USER_DATA_FILE, 'r') as file:
            return yaml.safe_load(file) or {}
    return {}

# Function to save user data to the YAML file
def save_user_data(user_data):
    with open(USER_DATA_FILE, 'w') as file:
        yaml.dump(user_data, file)

# Function for user registration (Sign Up)
def sign_up(username, password):
    user_data = load_user_data()
    
    if username in user_data:
        return False, "Username already exists"
    
    # Hash the password before saving
    user_data[username] = {
        'password': hash_password(password)
    }
    
    save_user_data(user_data)
    return True, "User registered successfully"

# Function for user authentication (Login)
def login(username, password):
    user_data = load_user_data()
    
    if username not in user_data:
        return False, "Username does not exist"
    
    # Check if the hashed password matches
    if user_data[username]['password'] == hash_password(password):
        return True, "Login successful"
    else:
        return False, "Incorrect password"

# Streamlit app for login and sign-up
st.title("Personal Expense Tracker")

# Session state to track login status
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

if 'page' not in st.session_state:
    st.session_state['page'] = 'login'

# Function to display login or sign-up page
def show_login_page():
    st.subheader("Login / Sign Up")
    
    # Option to select between Login and Sign Up
    option = st.selectbox("Choose an option", ["Login", "Sign Up"])

    if option == "Sign Up":
        st.subheader("Sign Up")
        new_username = st.text_input("Enter a username")
        new_password = st.text_input("Enter a password", type="password")
        confirm_password = st.text_input("Confirm your password", type="password")
        
        if st.button("Sign Up"):
            if new_password != confirm_password:
                st.error("Passwords do not match!")
            else:
                success, message = sign_up(new_username, new_password)
                if success:
                    st.success(message)
                else:
                    st.error(message)
    
    elif option == "Login":
        st.subheader("Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        
        if st.button("Login"):
            success, message = login(username, password)
            if success:
                st.success(message)
                st.session_state['logged_in'] = True
                st.session_state['username'] = username
                st.session_state['page'] = 'personal_info'
            else:
                st.error(message)

def create_expense_files(user_data):
    response = requests.post('http://127.0.0.1:5000/create_expense_files', json=user_data)
    return response.status_code == 200
# Function to display personal information and expenses page
def show_personal_info_page():
    st.title(f"Welcome, {st.session_state['username']}")
    
    # Collect personal information and expenses
    st.header("Personal Information")
    name = st.text_input("Enter your name", st.session_state['username'])
    dob = st.date_input("Enter your date of birth")
    gender = st.text_input("Enter your gender")
    income = st.number_input("Enter your income")
    
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



    
    st.title("Add Type of Expense")

    # Define the types of expenses
    permanent_expenses_default = ["Rent", "Utilities", "Healthcare", "EMI", "Mortgage"]
    variable_expenses_default = ["Shopping", "Travel", "Personal", "Petrol"]

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
            "name": name,
            "dob": dob.strftime("%Y-%m-%d"),
            "gender": gender,
            "income": income,
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

    if st.button("Logout"):
        st.session_state['logged_in'] = False
        st.session_state['page'] = 'login'
        st.experimental_rerun()

# Routing based on login status and page selection
if not st.session_state['logged_in']:
    show_login_page()
else:
    if st.session_state['page'] == 'personal_info':
        show_personal_info_page()