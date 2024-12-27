import json
import matplotlib.pyplot as plt
import datetime
from tabulate import tabulate
from fpdf import FPDF

months_list = ["January", "February", "March", "April", "May", "June",
               "July", "August", "September", "October", "November", "December"]

def initialize_file():
    try:
        with open('income_cost.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        with open('income_cost.json', 'w') as file:
            json.dump([], file)

def add_record(year=None, month=None, income=0, cost=0):
    current_date = datetime.datetime.now()
    
    # if year & date not defined by user
    if not year or not month:
        year = current_date.year
        month = months_list[current_date.month - 1]

    # Prevent future dates
    if year > current_date.year or (year == current_date.year and months_list.index(month) + 1 > current_date.month):
        print("Error: Cannot enter future date.")
        return

    with open('income_cost.json', 'r') as file:
        data = json.load(file)

    # Merge records if the same year and month exist
    for entry in data:
        if entry['year'] == year and entry['month'] == month:
            entry['income'] += income
            entry['cost'] += cost
            break
    else:
        data.append({"year": year, "month": month, "income": income, "cost": cost})

    with open('income_cost.json', 'w') as file:
        json.dump(data, file, indent=4)


def view_records():
    try:
        with open('income_cost.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print("No records file found.")
        return []

    if not data:
        print("No records found.")
        return []

    # Prepare data for tabulation
    table = [[entry['year'], entry['month'], entry['income'], entry['cost']] for entry in data]
    headers = ["Year", "Month", "Income", "Cost"]

    # Display as a table
    print("\n--- Recorded Data ---")
    print(tabulate(table, headers=headers, tablefmt="grid"))

    return data


def visualize_data():
    with open('income_cost.json', 'r') as file:
        data = json.load(file)

    if not data:
        print("No data available to visualize.")
        return

    years_months = [f"{entry['month']} {entry['year']}" for entry in data]
    incomes = [entry['income'] for entry in data]
    costs = [entry['cost'] for entry in data]

    plt.figure(figsize=(10, 6))
    plt.plot(years_months, incomes, label='Income', marker='o')
    plt.plot(years_months, costs, label='Cost', marker='o')
    plt.xlabel('Month & Year')
    plt.ylabel('Amount')
    plt.title('Income vs Cost')
    plt.legend()
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def analyze_data():
    with open('income_cost.json', 'r') as file:
        data = json.load(file)

    if not data:
        print("No data available for analysis.")
        return

    # the month with the highest income
    max_income_entry = max(data, key=lambda x: x['income'])
    print(f"Month with the highest income: {max_income_entry['month']} {max_income_entry['year']} (Income: {max_income_entry['income']})")

    # the year with the highest cost
    yearly_cost = {}
    yearly_income = {}
    for entry in data:
        yearly_cost[entry['year']] = yearly_cost.get(entry['year'], 0) + entry['cost']
        yearly_income[entry['year']] = yearly_income.get(entry['year'], 0) + entry['income']

    max_cost_year = max(yearly_cost, key=yearly_cost.get)
    print(f"Year with the highest cost: {max_cost_year} (Total Cost: {yearly_cost[max_cost_year]})")

    # Calculate total income and cost
    total_income = sum(entry['income'] for entry in data)
    total_cost = sum(entry['cost'] for entry in data)
    print(f"Total Income: {total_income}")
    print(f"Total Cost: {total_cost}")

    # the year with the highest income
    max_income_year = max(yearly_income, key=yearly_income.get)
    print(f"Year with the highest income: {max_income_year} (Total Income: {yearly_income[max_income_year]})")

    # net balance for each year
    net_balance = {year: yearly_income[year] - yearly_cost.get(year, 0) for year in yearly_income}
    for year, balance in net_balance.items():
        print(f"Net balance for {year}: {balance}")

def query_balance_option():
    with open('income_cost.json', 'r') as file:
        data = json.load(file)

    if not data:
        print("No data available for balance query.")
        return

    print("\n--- Balance Query ---")
    print("1. Current Balance (from past to today's date)")
    print("2. Specific Year & Month")
    choice = input("Enter your choice: ")

    if choice == '1':
        current_date = datetime.datetime.now()
        total_income = 0
        total_cost = 0

        for entry in data:
            entry_date = datetime.datetime(entry['year'], months_list.index(entry['month']) + 1, 1)
            if entry_date <= current_date:
                total_income += entry['income']
                total_cost += entry['cost']

        balance = total_income - total_cost
        print(f"Current balance (from past to today's date): {balance}")

    elif choice == '2':
        year = int(input("Enter year for balance query: "))
        print("Select month:")
        for i, month in enumerate(months_list, 1):
            print(f"{i}. {month}")

        month_choice = int(input("Enter month number: "))
        if 1 <= month_choice <= 12:
            month_name = months_list[month_choice - 1]
            total_income = 0
            total_cost = 0

            for entry in data:
                entry_date = datetime.datetime(entry['year'], months_list.index(entry['month']) + 1, 1)
                target_date = datetime.datetime(year, month_choice, 1)

                if entry_date <= target_date:
                    total_income += entry['income']
                    total_cost += entry['cost']

            balance = total_income - total_cost
            print(f"Balance up to {month_name} {year}: {balance}")
        else:
            print("Invalid month selection.")

    else:
        print("Invalid choice. Please try again.")

def export_to_pdf():
    try:
        with open('income_cost.json', 'r') as file:
            data = json.load(file)
    except FileNotFoundError:
        print("No records file found.")
        return

    if not data:
        print("No records to export.")
        return

    # Calculate Summary
    total_income = sum(entry['income'] for entry in data)
    total_cost = sum(entry['cost'] for entry in data)
    net_balance = total_income - total_cost

    class PDF(FPDF):
        def header(self):
            self.set_font("Arial", "B", 14)
            self.cell(0, 10, "Income & Cost Records", border=False, ln=True, align="C")
            self.ln(10)

        def footer(self):
            self.set_y(-15)
            self.set_font("Arial", "I", 10)
            self.cell(0, 10, f"Page {self.page_no()}", align="C")

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Table Headers
    pdf.set_fill_color(200, 220, 255)
    pdf.set_text_color(0)
    pdf.set_draw_color(50, 50, 100)
    pdf.set_line_width(0.3)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(40, 10, "Year", 1, 0, "C", fill=True)
    pdf.cell(60, 10, "Month", 1, 0, "C", fill=True)
    pdf.cell(40, 10, "Income", 1, 0, "C", fill=True)
    pdf.cell(40, 10, "Cost", 1, 1, "C", fill=True)

    # Table Data
    pdf.set_font("Arial", "", 12)
    for entry in data:
        pdf.cell(40, 10, str(entry['year']), 1, 0, "C")
        pdf.cell(60, 10, entry['month'], 1, 0, "C")
        pdf.cell(40, 10, f"{entry['income']:.2f}", 1, 0, "R")
        pdf.cell(40, 10, f"{entry['cost']:.2f}", 1, 1, "R")

    # Add Summary Section
    pdf.ln(10)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Summary", ln=True, align="L")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 10, f"Total Income: {total_income:.2f}", ln=True, align="L")
    pdf.cell(0, 10, f"Total Cost: {total_cost:.2f}", ln=True, align="L")
    pdf.cell(0, 10, f"Net Balance: {net_balance:.2f}", ln=True, align="L")

    pdf.output("income_cost_records.pdf")
    print("Records have been exported to 'income_cost_records.pdf' with a summary.")

def main():
    initialize_file()
    current_date = datetime.datetime.now()
    current_year = current_date.year
    current_month = current_date.month

    while True:
        print("\n--- Income & Cost Tracker ---")
        print("1. Add Record")
        print("2. View Records")
        print("3. Export Record in PDF")
        print("4. Visualize Data")
        print("5. Analyze Data")
        print("6. Query Balance")
        print("7. Exit")
        
        choice = input("Enter your choice: ")
        
        if choice == '1':
            # Year input validation
            while True:
                try:
                    year = int(input(f"Enter year: "))
                    if year > current_year:
                        print("Error: Cannot enter future year.")
                    else:
                        break
                except ValueError:
                    print("Invalid input. Please enter a valid year (e.g., 2024).")

            # Month input validation
            while True:
                print("Select month:")
                for i, month in enumerate(months_list, 1):
                    print(f"{i}. {month}")
                print(f"Current month: ({months_list[current_month - 1]}) - Cannot enter future month.")
                
                try:
                    month_choice = int(input("Enter month number: "))
                    if 1 <= month_choice <= 12:
                        if year == current_year and month_choice > current_month:
                            print("Error: Cannot enter future month.")
                        else:
                            month = months_list[month_choice - 1]
                            break
                    else:
                        print("Invalid month number. Please select a valid month between 1 and 12.")
                except ValueError:
                    print("Invalid input. Please enter a valid number for the month.")

            # Income and cost inputs
            income = float(input("Enter income: "))
            cost = float(input("Enter cost: "))
            add_record(year, month, income, cost)
            print("Record added successfully.")
            
        elif choice == '2':
            records = view_records()
            if not records:
                print("No records to display.")

        elif choice == '3':
            export_to_pdf()
        elif choice == '4':
            visualize_data()
        elif choice == '5':
            analyze_data()
        elif choice == '6':
            query_balance_option()
        elif choice == '7':
            print("Exiting program.")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
