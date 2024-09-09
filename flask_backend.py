from flask import Flask, request, jsonify
import csv
import os
import pandas as pd

app = Flask(__name__)

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
            existing_headers = reader.fieldnames or []
            rows = list(reader)
    except FileNotFoundError:
        existing_headers = []
        rows = []

    # Combine existing headers with new headers, only adding new ones
    updated_headers = list(set(existing_headers + list(new_headers)))

    # If there are new headers to add, rewrite the file with new headers and old rows
    if updated_headers != existing_headers:
        with open(file_path, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=updated_headers)
            writer.writeheader()
            writer.writerows(rows)

    return updated_headers

# Route to create CSV files for personal and expense data
@app.route('/create_expense_files', methods=['POST'])
def create_expense_files_route():
    data = request.json
    name = data.get('name')
    
    # Create the expense CSV files for the user
    create_expense_files(name)
    
    # Add the user's personal data to the personal_data.csv
    add_personal_data(data)
    
    return jsonify({"status": "success", "message": "Personal data and CSV files created"})

# Route to add expenses to the CSV files
@app.route('/add_expenses', methods=['POST'])
def add_expenses():
    data = request.json
    name = data.get('name')
    permanent_expenses = data.get('permanent_expenses', [])
    variable_expenses = data.get('variable_expenses', [])
    
    # Include day, month, and year for expense tracking
    day = data.get('day', None)
    month = data.get('month', None)
    year = data.get('year', None)

    permanent_file = os.path.join(CSV_DIR, f"{name}_Expenses_permanent.csv")
    variable_file = os.path.join(CSV_DIR, f"{name}_Expenses_variable.csv")

    # Create base rows with date information
    permanent_row = {"year": year, "month": month, "day": day}
    variable_row = {"year": year, "month": month, "day": day}

    # Add expenses to their respective rows
    for expense in permanent_expenses:
        permanent_row[expense] = expense
    for expense in variable_expenses:
        variable_row[expense] = expense
    
    print(permanent_row.keys())    

    # Update headers only if there are new expenses
    update_csv_headers(permanent_file, permanent_row.keys())
    update_csv_headers(variable_file, variable_row.keys())

    # Append the permanent and variable expenses to CSV
    # with open(permanent_file, 'a', newline='') as f:
    #     writer = csv.DictWriter(f, fieldnames=permanent_row.keys())
    #     writer.writerow(permanent_row)
    
    # with open(variable_file, 'a', newline='') as f:
    #     writer = csv.DictWriter(f, fieldnames=variable_row.keys())
    #     writer.writerow(variable_row)

    return jsonify({"status": "success", "message": "Expenses added to CSV files"})

if __name__ == '__main__':
    app.run(debug=True)
