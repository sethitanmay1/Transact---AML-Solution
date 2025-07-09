# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 11:48:55 2025

@author: ernest
"""

import sqlite3
import pandas as pd


# Connect to the SQLite database
db_path = "../Data/Scotiabank.db"
conn = sqlite3.connect(db_path)

# Helper function to fetch table names
def get_table_names(connection):
    query = "SELECT name FROM sqlite_master WHERE type='table';"
    return [row[0] for row in connection.execute(query).fetchall()]

# Fetch table names
table_names = get_table_names(conn)
print("Tables in the database:")
print(table_names)

# Initialize a report dictionary
report = {}

# Analyze each table
for table in table_names:
    print(f"\nExploring table: {table}")
    
    # Load table into a DataFrame
    df = pd.read_sql_query(f"SELECT * FROM {table}", conn)
    report[table] = {}
    
    # General information
    num_rows, num_columns = df.shape
    print(f"Number of rows: {num_rows}, Number of columns: {num_columns}")
    report[table]['num_rows'] = num_rows
    report[table]['num_columns'] = num_columns
    
    # Column types
    column_types = df.dtypes
    print("Column types:")
    print(column_types)
    report[table]['column_types'] = column_types.to_dict()

    # Missing values
    missing_values = df.isnull().sum()
    print("Missing values:")
    print(missing_values)
    report[table]['missing_values'] = missing_values.to_dict()

    # Unique values
    unique_values = {col: df[col].unique().tolist()[:10] for col in df.columns}  # Limiting to 10 unique values
    print("Sample of unique values per column:")
    print(unique_values)
    report[table]['unique_values'] = unique_values


