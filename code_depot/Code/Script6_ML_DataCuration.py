#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 18:01:18 2025

@author: ernest
"""


import pandas as pd
import numpy as np
from sklearn.preprocessing import LabelEncoder


# Load the CSV file
def load_data(file_path):
    """
    Load customer_reports.csv into a DataFrame.
    
    Args:
        file_path (str): Path to the CSV file.
    
    Returns:
        pd.DataFrame: Loaded DataFrame.
    """
    df = pd.read_csv(file_path)
    return df


# Process date columns
def process_dates(df, date_columns):
    """
    Process date columns to extract features and handle missing values.
    
    Args:
        df (pd.DataFrame): DataFrame containing date columns.
        date_columns (list): List of column names with date information.
    
    Returns:
        pd.DataFrame: DataFrame with processed date features.
    """
    for col in date_columns:
        # Convert to datetime
        df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # Extract basic features
        df[f'{col}_year'] = df[col].dt.year
        df[f'{col}_month'] = df[col].dt.month
        df[f'{col}_day'] = df[col].dt.day
        df[f'{col}_day_of_week'] = df[col].dt.dayofweek
        df[f'{col}_day_of_year'] = df[col].dt.dayofyear
        
        # Add cyclic encoding
        df[f'{col}_month_sin'] = np.sin(2 * np.pi * df[f'{col}_month'] / 12)
        df[f'{col}_month_cos'] = np.cos(2 * np.pi * df[f'{col}_month'] / 12)
        df[f'{col}_day_of_week_sin'] = np.sin(2 * np.pi * df[f'{col}_day_of_week'] / 7)
        df[f'{col}_day_of_week_cos'] = np.cos(2 * np.pi * df[f'{col}_day_of_week'] / 7)
        
        # Calculate time since date
        df[f'days_since_{col}'] = (pd.Timestamp.now() - df[col]).dt.days
        
        # Handle missing dates
        df[f'{col}_missing'] = df[col].isna().astype(int)
        df[col].fillna(pd.Timestamp("1900-01-01"), inplace=True)
        
        # Convert to timestamp
        df[f'{col}_timestamp'] = df[col].astype('int64') // 10**9
    
    # Drop original date columns
    df.drop(columns=date_columns, inplace=True)
    return df


def label_encode_columns(df, columns):
    """
    Apply Label Encoding to specified columns in the DataFrame.

    Args:
        df (pd.DataFrame): The input DataFrame.
        columns (list): List of column names to encode.

    Returns:
        pd.DataFrame: DataFrame with encoded columns.
        dict: Dictionary containing LabelEncoders for each column.
    """
    encoders = {}
    for col in columns:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col].astype(str))  # Convert to string for compatibility
        encoders[col] = le  # Save the encoder for future use if needed
    return df, encoders



import numpy as np

def process_transaction_columns_dynamic(df, columns):
    """
    Dynamically process transaction-related columns to create binary features for unique values.

    Args:
        df (pd.DataFrame): The input DataFrame.
        columns (list): List of columns to process.

    Returns:
        pd.DataFrame: DataFrame with new binary features added.
    """
    for col in columns:
        # Replace empty lists with NaN
        df[col] = df[col].apply(lambda x: np.nan if x == '[]' else x)
        
        # Convert string representation of lists to actual lists
        df[col] = df[col].apply(lambda x: eval(x) if isinstance(x, str) else x)
        
        # Flatten lists to extract all unique values
        unique_values = set(
            value for row in df[col].dropna() if isinstance(row, list) for value in row
        )
        
        # Create binary features for each unique value
        for unique in unique_values:
            df[f'{col}_contains_{unique}'] = df[col].apply(
                lambda x: 1 if isinstance(x, list) and unique in x else 0
            )
        
        # Create a feature for the number of items in the list
        df[f'{col}_count'] = df[col].apply(lambda x: len(x) if isinstance(x, list) else 0)
    # Drop the original columns after processing
    df.drop(columns=columns, inplace=True)
    return df


# Main function
if __name__ == "__main__":
    # File paths
    input_file = "../Data/customer_reports.csv"
    output_file = "../Data/customer_reports_preprocessed.csv"
    
    # Load the data
    print("Loading data...")
    df = load_data(input_file)
    print("Data loaded successfully!")
    
    # Define date columns to process
    date_columns = ['established_date', 'onboard_date']
    
    # Process date columns
    print("Processing date columns...")
    df = process_dates(df, date_columns)
    print("Date columns processed successfully!")

    # Columns to label encode
    columns_to_encode = ['country', 'province', 'city']

    # Apply Label Encoding
    print("Applying Label Encoding...")
    df, encoders = label_encode_columns(df, columns_to_encode)
    print("Label Encoding applied successfully!")
    
    #drop industry
    df.drop(columns=['industry'], inplace=True)

    # Example columns to process
    transaction_columns = [
        'countries_of_abm_transactions',
        'provinces_of_abm_transactions',
        'cities_of_abm_transactions',
        'countries_of_card_transactions',
        'provinces_of_card_transactions',
        'cities_of_card_transactions',
    ]
    
    # Process transaction columns
    print("Processing transaction columns...")
    df = process_transaction_columns_dynamic(df, transaction_columns)
    print("Transaction columns processed successfully!")
    
    #fill nans
    fill_value = -999
    df.fillna(fill_value, inplace=True)
    
    non_numerical_columns = [
    col for col in df.columns if col != "customer_id" and not np.issubdtype(df[col].dtype, np.number)
    ]
    if non_numerical_columns:
        raise ValueError(f"The following columns are not numerical: {non_numerical_columns}")

    # Save the processed DataFrame
    output_file = "../Data/customer_features.csv"
    df.to_csv(output_file, index=False)
    print(f"Processed data saved to {output_file}")