import mysql.connector
import pandas as pd
from Script1_Load_CSV_Files import data_load

# MySQL Database Configuration
DB_CONFIG = {
    "host": "localhost",  # Change if needed
    "user": "timothy",
    "password": "CanyouFindThisPassword!",
    "database": "Scotiabank"
}

data_path = "Data"
files = [
    "abm.csv", "card.csv", "cheque.csv", "eft.csv", "emt.csv",
    "kyc.csv", "kyc_industry_codes.csv", "wire.csv"
]

dataframes = data_load(data_path, files)

# Connect to MySQL and create database
conn = mysql.connector.connect(host=DB_CONFIG["host"], user=DB_CONFIG["user"], password=DB_CONFIG["password"])
cursor = conn.cursor()
cursor.execute("CREATE DATABASE IF NOT EXISTS Scotiabank")
cursor.execute("USE Scotiabank")

# Schema Definition
schema = {
    "kyc": """
        CREATE TABLE IF NOT EXISTS kyc (
            customer_id VARCHAR(255) PRIMARY KEY,
            country VARCHAR(255),
            province VARCHAR(255),
            city VARCHAR(255),
            industry_code INT,
            employee_count INT,
            sales DECIMAL(18,2),
            established_date DATE,
            onboard_date DATE,
            FOREIGN KEY (industry_code) REFERENCES kyc_industry_codes(industry_code)
        ) ENGINE=InnoDB;
    """,
    "kyc_industry_codes": """
        CREATE TABLE IF NOT EXISTS kyc_industry_codes (
            industry_code INT PRIMARY KEY,
            industry VARCHAR(255)
        ) ENGINE=InnoDB;
    """,
    "abm": """
        CREATE TABLE IF NOT EXISTS abm (
            abm_id VARCHAR(255) PRIMARY KEY,
            customer_id VARCHAR(255),
            amount_cad DECIMAL(18,2),
            debit_credit INT,
            cash_indicator INT,
            country VARCHAR(255),
            province VARCHAR(255),
            city VARCHAR(255),
            transaction_date DATE,
            transaction_time TIME,
            FOREIGN KEY (customer_id) REFERENCES kyc(customer_id)
        ) ENGINE=InnoDB;
    """,
    "card": """
        CREATE TABLE IF NOT EXISTS card (
            card_trxn_id VARCHAR(255) PRIMARY KEY,
            customer_id VARCHAR(255),
            amount_cad DECIMAL(18,2),
            debit_credit INT,
            merchant_category INT,
            ecommerce_ind INT,
            country VARCHAR(255),
            province VARCHAR(255),
            city VARCHAR(255),
            transaction_date DATE,
            transaction_time TIME,
            FOREIGN KEY (customer_id) REFERENCES kyc(customer_id)
        ) ENGINE=InnoDB;
    """,
    "cheque": """
        CREATE TABLE IF NOT EXISTS cheque (
            cheque_id VARCHAR(255) PRIMARY KEY,
            customer_id VARCHAR(255),
            amount_cad DECIMAL(18,2),
            debit_credit INT,
            transaction_date DATE,
            FOREIGN KEY (customer_id) REFERENCES kyc(customer_id)
        ) ENGINE=InnoDB;
    """,
    "eft": """
        CREATE TABLE IF NOT EXISTS eft (
            eft_id VARCHAR(255) PRIMARY KEY,
            customer_id VARCHAR(255),
            amount_cad DECIMAL(18,2),
            debit_credit INT,
            transaction_date DATE,
            transaction_time TIME,
            FOREIGN KEY (customer_id) REFERENCES kyc(customer_id)
        ) ENGINE=InnoDB;
    """,
    "emt": """
        CREATE TABLE IF NOT EXISTS emt (
            emt_id VARCHAR(255) PRIMARY KEY,
            customer_id VARCHAR(255),
            amount_cad DECIMAL(18,2),
            debit_credit INT,
            transaction_date DATE,
            transaction_time TIME,
            FOREIGN KEY (customer_id) REFERENCES kyc(customer_id)
        ) ENGINE=InnoDB;
    """,
    "wire": """
        CREATE TABLE IF NOT EXISTS wire (
            wire_id VARCHAR(255) PRIMARY KEY,
            customer_id VARCHAR(255),
            amount_cad DECIMAL(18,2),
            debit_credit INT,
            transaction_date DATE,
            transaction_time TIME,
            FOREIGN KEY (customer_id) REFERENCES kyc(customer_id)
        ) ENGINE=InnoDB;
    """
}

table_order = ["kyc_industry_codes", "kyc", "abm", "card", "cheque", "eft", "emt", "wire"]
# Disable foreign key checks
cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
conn.commit()
# Execute table creation in the correct order
for table_name in table_order:
    cursor.execute(schema[table_name])

# Insert Data into MySQL
for table_name, df in dataframes.items():
    if not df.empty:
        df = df.astype(object).where(pd.notna(df), None)
        cols = ", ".join(df.columns)
        placeholders = ", ".join(["%s"] * len(df.columns))
        insert_sql = f"INSERT INTO {table_name} ({cols}) VALUES ({placeholders})"
        # Convert NAType (pandas NA values) to None (MySQL NULL)
        # df = df.where(pd.notna(df), None)
        cursor.executemany(insert_sql, df.values.tolist())

# Commit and Close Connection
conn.commit()

# Re-enable foreign key checks
cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
conn.commit()
cursor.close()
conn.close()



print("Database 'Scotiabank' created and data inserted successfully!")