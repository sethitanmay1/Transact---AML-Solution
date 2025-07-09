#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script Name: 1-Load_CSV_Files.py
Description: Loads the CSV files into Pandas DataFrames.
Author: Ernest
Date: Jan 2025
Version: 1.2
"""

import pandas as pd
import os
import numpy as np

def enforce_column_types(df, column_types):
    """
    Enforces the specified column types on the DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame to transform.
        column_types (dict): A dictionary specifying column types.

    Returns:
        pd.DataFrame: The transformed DataFrame.
    """
    for column, dtype in column_types.items():
        if dtype == 'text':
            df[column] = df[column].astype('string')
        elif dtype == 'float':
            df[column] = pd.to_numeric(df[column], errors='coerce')
        elif dtype == 'int':
            if column == 'industry_code':
                # Map 'other' to -1, leave empty values untouched
                df[column] = df[column].apply(lambda x: -1 if str(x).strip().lower() == 'other' else x)
                df[column] = pd.to_numeric(df[column], errors='coerce')
            else:
                df[column] = pd.to_numeric(df[column], errors='coerce').astype('Int64')
        elif dtype == 'binary':
            if column == 'debit_credit':  # Map both full and abbreviated values for debit/credit
                df[column] = df[column].str.upper().map({'CREDIT': 1, 'DEBIT': 0, 'C': 1, 'D': 0})
            else:
                df[column] = df[column].apply(lambda x: 1 if x == 1 else 0 if x == 0 else np.nan)
        elif dtype == 'date':
            df[column] = pd.to_datetime(df[column], format='%Y-%m-%d', errors='coerce').dt.date
        elif dtype == 'time':
            df[column] = pd.to_datetime(df[column], format='%H:%M:%S', errors='coerce').dt.time

    return df

def data_load(data_path, file_list):
    # Load files into a dictionary of DataFrames
    dataframes = {
        file.split('.')[0]: pd.read_csv(os.path.join(data_path, file))
        for file in file_list
    }

    # Define column types for each table
    column_types = {
        "abm": {
            'abm_id': 'text',
            'customer_id': 'text',
            'amount_cad': 'float',
            'debit_credit': 'binary',
            'cash_indicator': 'binary',
            'country': 'text',
            'province': 'text',
            'city': 'text',
            'transaction_date': 'date',
            'transaction_time': 'time'
        },
        "card": {
            'card_trxn_id': 'text',
            'customer_id': 'text',
            'amount_cad': 'float',
            'debit_credit': 'binary',
            'merchant_category': 'int',
            'ecommerce_ind': 'binary',
            'country': 'text',
            'province': 'text',
            'city': 'text',
            'transaction_date': 'date',
            'transaction_time': 'time'
        },
        "cheque": {
            'cheque_id': 'text',
            'customer_id': 'text',
            'amount_cad': 'float',
            'debit_credit': 'binary',
            'transaction_date': 'date'
        },
        "eft": {
            'eft_id': 'text',
            'customer_id': 'text',
            'amount_cad': 'float',
            'debit_credit': 'binary',
            'transaction_date': 'date',
            'transaction_time': 'time'
        },
        "emt": {
            'emt_id': 'text',
            'customer_id': 'text',
            'amount_cad': 'float',
            'debit_credit': 'binary',
            'transaction_date': 'date',
            'transaction_time': 'time'
        },
        "kyc": {
            'customer_id': 'text',
            'country': 'text',
            'province': 'text',
            'city': 'text',
            'industry_code': 'int',
            'employee_count': 'int',
            'sales': 'float',
            'established_date': 'date',
            'onboard_date': 'date'
        },
        "kyc_industry_codes": {
            'industry_code': 'int',
            'industry': 'text'
        },
        "wire": {
            'wire_id': 'text',
            'customer_id': 'text',
            'amount_cad': 'float',
            'debit_credit': 'binary',
            'transaction_date': 'date',
            'transaction_time': 'time'
        }
    }

    # Enforce column types for each DataFrame
    for table, df in dataframes.items():
        if table in column_types:
            dataframes[table] = enforce_column_types(df, column_types[table])



    return dataframes

if __name__ == "__main__":
    # Data path and file names
    data_path = "Data"
    files = [
        "abm.csv",
        "card.csv",
        "cheque.csv",
        "eft.csv",
        "emt.csv",
        "kyc.csv",
        "kyc_industry_codes.csv",
        "wire.csv"
    ]

    dataframes = data_load(data_path, files)

    # Print column names and their data types for each DataFrame
    for name, df in dataframes.items():
        print(f"Columns in {name}.csv:")
        for col in df.columns:
            print(f"  {col}: {df[col].dtype}")
        print()

