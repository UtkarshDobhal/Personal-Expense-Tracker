from flask import Flask, request, jsonify
import csv
import os

app = Flask(__name__)

# Directory to store the CSV files
CSV_DIR = './expenses_csv'

# Function to create CSV files with an empty header initially
def create_expense_files(name):
    permanent_file = os.path.join(CSV_DIR, f"{name}_Expenses_permanent.csv")
    variable_file = os.path.join(CSV_DIR, f"{name}_Expenses_variable.csv")

    # Ensure the directory exists
    os.makedirs(CSV_DIR, exist_ok=True)

    # Create both permanent and variable expense CSV files with no headers
    with open(permanent_file, 'w', newline='') as f:
        pass

    with open(variable_file, 'w', newline='') as f:
        pass

# Route to create empty CSV files for a user
@app.route('/create_expense_files', methods=['POST'])
def create_expense_files_route():
    data = request.json
    name = data.get('name')

    create_expense_files(name)
    return jsonify({"status": "success", "message": "CSV files created"})

# Function to ensure the selected headers are present in the CSV
def update_csv_headers(file_path, new_headers):
    try:
        # Try to read the existing headers and rows if the file exists
        with open(file_path, 'r', newline='') as f:
            reader = csv.DictReader(f)
            existing_headers = reader.fieldnames or []
            rows = list(reader)
    except FileNotFoundError:
        # If file doesn't exist, initialize with empty headers and rows
        existing_headers = []
        rows = []

    # Combine existing headers with new headers
    updated_headers = list(set(existing_headers + list(new_headers)))

    # Rewrite the file with the updated headers and existing rows
    with open(file_path, 'w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=updated_headers)
        writer.writeheader()
        writer.writerows(rows)

    return updated_headers

# Route to add expenses to the CSV files
@app.route('/add_expenses', methods=['POST'])
def add_expenses():
    data = request.json
    name = data.get('name')
    permanent_expenses = data.get('permanent_expenses', [])
    variable_expenses = data.get('variable_expenses', [])
    month = data.get('month')
    year = data.get('year')
    day = data.get('day')

    permanent_file = os.path.join(CSV_DIR, f"{name}_Expenses_permanent.csv")
    variable_file = os.path.join(CSV_DIR, f"{name}_Expenses_variable.csv")

    # Create base rows with date information
    permanent_row = {"year": year, "month": month, "date": day}
    variable_row = {"year": year, "month": month, "date": day}

    # Add expenses to their respective rows
    for expense in permanent_expenses:
        permanent_row[expense] = expense
    for expense in variable_expenses:
        variable_row[expense] = expense

    # Update headers with the new expenses
    permanent_headers = update_csv_headers(permanent_file, permanent_row.keys())
    variable_headers = update_csv_headers(variable_file, variable_row.keys())

    # Write updated permanent expenses to the CSV file


    return jsonify({"status": "success", "message": "Expenses added to CSV files"})

if __name__ == '__main__':
    app.run(debug=True)
