# -*- coding: utf-8 -*-
"""
Script Name: Generate_Customer_Reports.py
Description: Generates reports for all unique customers and saves them to a CSV file using parallel processing.
Author: Ernest
Date: Jan 2025
Version: 2.0
"""

from multiprocessing import Pool, cpu_count
import sqlite3
import pandas as pd
from tqdm import tqdm
from Script4_Customer_Report import generate_customer_report


def get_customer_ids(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    customer_ids_query = "SELECT DISTINCT customer_id FROM kyc;"
    customer_ids = [row[0] for row in cursor.execute(customer_ids_query).fetchall()]
    conn.close()
    return customer_ids


def process_customer(args):
    db_path, customer_id = args
    try:
        return generate_customer_report(db_path, customer_id)
    except Exception as e:
        print(f"Error processing customer {customer_id}: {e}")
        return None


def create_customer_reports(db_path, num_workers=None):
    if num_workers is None:
        num_workers = cpu_count()

    customer_ids = get_customer_ids(db_path)
    print("Total number of customers:", len(customer_ids))

    # Use multiprocessing Pool for parallel processing with tqdm progress bar
    with Pool(processes=num_workers) as pool:
        results = []
        for result in tqdm(pool.imap(process_customer, [(db_path, cid) for cid in customer_ids]), total=len(customer_ids)):
            results.append(result)

    # Filter out None results (errors)
    valid_reports = [report for report in results if report and "error" not in report]

    # Convert to DataFrame
    return pd.DataFrame(valid_reports)


if __name__ == "__main__":
    db_path = "../Data/Scotiabank.db"
    output_csv_path = "../Data/customer_reports.csv"
    df = create_customer_reports(db_path, num_workers=64)  # Adjust workers based on system
    df.to_csv(output_csv_path, index=False)
    print(f"Customer reports saved to {output_csv_path}")
