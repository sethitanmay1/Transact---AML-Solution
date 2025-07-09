# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 16:38:21 2025

@author: ernest
"""

# -*- coding: utf-8 -*-
"""
Script Name: Generate_Customer_Reports.py
Description: Generates reports for all unique customers and saves them to a CSV file.
Author: Ernest
Date: Jan 2025
Version: 1.0
"""

import sqlite3
import pandas as pd
from Script4_Customer_Report import generate_customer_report  # Assuming the function is in this file


def create_customer_reports(db_path):
    """
    Generates reports for all unique customers and saves the results to a CSV file.

    Args:
        db_path (str): Path to the SQLite database file.
        output_csv_path (str): Path to the output CSV file.
    """
    # Connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Get all unique customer IDs from the kyc table
    customer_ids_query = "SELECT DISTINCT customer_id FROM kyc;"
    customer_ids = [row[0] for row in cursor.execute(customer_ids_query).fetchall()]

    # Close the connection (we'll reopen it in the function calls)
    conn.close()

    # Generate reports and collect them into a list
    reports = []
    print("Total number of customers:", len(customer_ids))
    for i, customer_id in enumerate(customer_ids, start=1):
        report = generate_customer_report(db_path, customer_id)
        if "error" not in report:  # Skip errors
            reports.append(report)
        if i % 100 == 0:
            print(f"Processed {i} customers...")

    # Convert the list of dictionaries to a Pandas DataFrame
    df = pd.DataFrame(reports)
    return df




# Example Usage
if __name__ == "__main__":
    db_path = "../Data/Scotiabank.db"
    output_csv_path = "../Data/customer_reports.csv"
    df=create_customer_reports(db_path)
    # Save to CSV
    df.to_csv(output_csv_path, index=False)
    print(f"Customer reports saved to {output_csv_path}")
