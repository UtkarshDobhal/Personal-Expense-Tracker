from flask import Flask, request, jsonify, session
import os
import csv
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Set the secret key for session management
app.secret_key = 'qwerty12345'  # Replace with a secure, random key

# Directory to store the CSV files
CSV_DIR = './expenses_csv'

# Function to store personal data in the CSV file
def add_personal_data(data):
    # Open the CSV file in append mode
    personal_file = "Personal-Expense-Tracker/personal_data.csv"
    
    # Define the fieldnames for the personal data CSV
    fieldnames = ['ID', 'Name', 'DOB', 'Gender', 'Yearly Income']
    
    # Create the CSV directory if it doesn't exist
    os.makedirs(os.path.dirname(personal_file), exist_ok=True)
    
    # Automatically generate the next ID
    if os.path.exists(personal_file):
        last_id = pd.read_csv(personal_file)['ID'].max()
        new_id = last_id + 1 if not pd.isna(last_id) else 1
    else:
        new_id = 1
    
    # Open the personal data CSV in append mode
    with open(personal_file, 'a', newline='') as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        
        # If the file is new, write the headers
        if csv_file.tell() == 0:
            writer.writeheader()
        
        # Write the personal data to the CSV
        writer.writerow({
            'ID': new_id,
            'Name': data['name'],
            'DOB': data['dob'],
            'Gender': data['gender'],
            'Yearly Income': data['income']
        })

# Function to create empty CSV files for the user's expenses
def create_expense_files(name):
    permanent_file = os.path.join(CSV_DIR, f"{name}_Expenses_permanent.csv")
    variable_file = os.path.join(CSV_DIR, f"{name}_Expenses_variable.csv")
    
    # Ensure the directory exists
    os.makedirs(CSV_DIR, exist_ok=True)

    # Create the CSV files if they don't exist
    if not os.path.exists(permanent_file):
        with open(permanent_file, 'w', newline='') as f:
            pass
    if not os.path.exists(variable_file):
        with open(variable_file, 'w', newline='') as f:
            pass

# Function to update headers only if new columns are introduced
def update_csv_headers(file_path, new_headers):
    try:
        # Read existing headers and rows if the file exists
        with open(file_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            existing_headers = ["Year", "Month", "Date"]
            rows = list(reader)
    except FileNotFoundError:
        existing_headers = []
        rows = []

    # Combine existing headers with new headers, only adding new ones
    updated_headers = existing_headers + new_headers

    # If there are new headers to add, rewrite the file with new headers and old rows
    if updated_headers != existing_headers:
        with open(file_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=updated_headers)
            writer.writeheader()
            writer.writerows(rows)

    return updated_headers

def update_exp(data, name,type):
    # Get the current date
    current_date = datetime.now()
    year = current_date.year
    month = current_date.month
    day = current_date.day

    # Extract the dynamic expense category ('permanent_expenses' in this case)
    expense_category = list(data.keys())[1]  # Get the second key (assuming it's expenses)
    expenses = data[expense_category]  # Fetch the expenses dictionary dynamically

    with open(f"expenses_csv\\{name}_{type}.csv", 'a', newline='') as csv_file:
        # Define the fieldnames, starting with date-related fields
        fieldnames = ["Year", "Month", "Day"]
        
        # Dynamically add all keys from the expenses dictionary to the fieldnames
        fieldnames.extend(expenses.keys())

        # Create a DictWriter object
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)

        # Prepare a single dictionary to write the entire row
        row_data = {
            'Year': year,  # Insert current year
            'Month': month,  # Insert current month
            'Day': day  # Insert current day
        }

        # Dynamically update the row data with the fetched expenses
        row_data.update(expenses)

        # Write the header if it's a new file
        if csv_file.tell() == 0:  # Check if the file is empty
            writer.writeheader()

        # Write the entire row in one go
        writer.writerow(row_data)


# Route to create CSV files for personal and expense data
@app.route('/create_expense_files', methods=['POST'])
def create_expense_files_route():
    data = request.json
    name = data.get('name')
    
    # Create the expense CSV files for the user
    create_expense_files(name)
    
    # Add the user's personal data to the personal_data.csv
    add_personal_data(data)
    session['name'] = name
    
    return jsonify({"status": "success", "message": "Personal data and CSV files created"})

# Route to add expenses to the CSV files
@app.route('/add_expenses', methods=['POST'])
def add_expenses():
    data = request.json
    name = data.get('name')
    permanent_expenses = data.get('permanent_expenses', [])
    variable_expenses = data.get('variable_expenses', [])
    

    permanent_file = os.path.join(CSV_DIR, f"{name}_Expenses_permanent.csv")
    variable_file = os.path.join(CSV_DIR, f"{name}_Expenses_variable.csv")


    # Update headers only if there are new expenses
    update_csv_headers(permanent_file, permanent_expenses)
    update_csv_headers(variable_file, variable_expenses)
    


    return jsonify({"status": "success", "message": "Expenses added to CSV files"})

@app.route('/update_permanent_expenses', methods=['POST'])
def update_per_expenses():
    data = request.json
    print(data)
    name = data["name"]
    print(name)  
    if not name:
        return jsonify({"status": "error", "message": "User not logged in"})
    type = "Expenses_permanent"
    update_exp(data, name, type)
    return jsonify({"status": "success", "message": "Expenses updated successfully"})

@app.route('/update_variable_expenses', methods=['POST'])
def update_var_expenses():
    data = request.json
    name = data["name"]  
    if not name:
        return jsonify({"status": "error", "message": "User not logged in"})
    type = "Expenses_variable"
    update_exp(data, name, type)
    return jsonify({"status": "success", "message": "Expenses updated successfully"})





if __name__ == '__main__':
    app.run(debug=True)
