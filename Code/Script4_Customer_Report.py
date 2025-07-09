# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 13:55:49 2025

@author: ernest
"""

import sqlite3
import json

def analyze_transactions(cursor, table, columns, customer_id):
    """
    Analyze transactions for a given table, dynamically handling available columns.

    Args:
        cursor: SQLite cursor object.
        table (str): Table name to query.
        columns (list): List of column names available in the table.
        customer_id (str): Customer ID for which to analyze data.

    Returns:
        dict: Aggregated transaction stats.
    """
    select_fields = [
        "COALESCE(SUM(CASE WHEN debit_credit = 1 THEN amount_cad ELSE 0 END), 0) AS total_credit",
        "COALESCE(SUM(CASE WHEN debit_credit = 0 THEN amount_cad ELSE 0 END), 0) AS total_debit",
        "COUNT(*) AS transaction_count"
    ]
    if "country" in columns:
        select_fields.append("GROUP_CONCAT(DISTINCT country) AS countries")
    else:
        select_fields.append("NULL AS countries")
    if "province" in columns:
        select_fields.append("GROUP_CONCAT(DISTINCT province) AS provinces")
    else:
        select_fields.append("NULL AS provinces")
    if "city" in columns:
        select_fields.append("GROUP_CONCAT(DISTINCT city) AS cities")
    else:
        select_fields.append("NULL AS cities")

    query = f"""
    SELECT {', '.join(select_fields)}
    FROM {table}
    WHERE customer_id = ?;
    """
    stats = cursor.execute(query, (customer_id,)).fetchone()
    return {
        "total_credit": stats[0],
        "total_debit": stats[1],
        "transaction_count": stats[2],
        "countries": sorted(stats[3].split(',')) if stats[3] else [],
        "provinces": sorted(stats[4].split(',')) if stats[4] else [],
        "cities": sorted(stats[5].split(',')) if stats[5] else []
    }


def generate_customer_report(db_path, customer_id):
    """
    Generate a structured report for a specific customer by analyzing multiple tables.

    Args:
        db_path (str): Path to the SQLite database file.
        customer_id (str): The customer ID for which to generate the report.

    Returns:
        dict: The structured customer report.
    """
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    def get_columns(table):
        return [col[1] for col in cursor.execute(f"PRAGMA table_info({table});").fetchall()]

    # Fetch customer details from kyc
    kyc_query = """
    SELECT kyc.customer_id, kyc.country, kyc.province, kyc.city,
           kyc_industry_codes.industry_code, kyc_industry_codes.industry, 
           kyc.employee_count, kyc.sales, kyc.established_date, kyc.onboard_date
    FROM kyc
    LEFT JOIN kyc_industry_codes ON kyc.industry_code = kyc_industry_codes.industry_code
    WHERE kyc.customer_id = ?;
    """
    kyc_details = cursor.execute(kyc_query, (customer_id,)).fetchone()

    if not kyc_details:
        conn.close()
        return {"error": f"No data found for customer ID: {customer_id}"}

    (customer_id, country, province, city, industry_id, industry, employee_count, sales,
     established_date, onboard_date) = kyc_details

    # Analyze transactions for each table
    abm_stats = analyze_transactions(cursor, "abm", get_columns("abm"), customer_id)
    card_stats = analyze_transactions(cursor, "card", get_columns("card"), customer_id)
    cheque_stats = analyze_transactions(cursor, "cheque", get_columns("cheque"), customer_id)
    eft_stats = analyze_transactions(cursor, "eft", get_columns("eft"), customer_id)
    emt_stats = analyze_transactions(cursor, "emt", get_columns("emt"), customer_id)
    wire_stats = analyze_transactions(cursor, "wire", get_columns("wire"), customer_id)

    # Generate the report as a dictionary
    report = {
        "customer_id": customer_id,
        "country": country,
        "province": province,
        "city": city,
        "industry_id": industry_id,
        "industry": industry,
        "employee_count": employee_count,
        "sales": sales,
        "established_date": established_date,
        "onboard_date": onboard_date,
        "total_abm_credit": abm_stats["total_credit"],
        "total_abm_debit": abm_stats["total_debit"],
        "number_of_abm_transactions": abm_stats["transaction_count"],
        "countries_of_abm_transactions": abm_stats["countries"],
        "provinces_of_abm_transactions": abm_stats["provinces"],
        "cities_of_abm_transactions": abm_stats["cities"],
        "total_card_credit": card_stats["total_credit"],
        "total_card_debit": card_stats["total_debit"],
        "number_of_card_transactions": card_stats["transaction_count"],
        "countries_of_card_transactions": card_stats["countries"],
        "provinces_of_card_transactions": card_stats["provinces"],
        "cities_of_card_transactions": card_stats["cities"],
        "total_cheque_credit": cheque_stats["total_credit"],
        "total_cheque_debit": cheque_stats["total_debit"],
        "number_of_cheque_transactions": cheque_stats["transaction_count"],
        "total_eft_credit": eft_stats["total_credit"],
        "total_eft_debit": eft_stats["total_debit"],
        "number_of_eft_transactions": eft_stats["transaction_count"],
        "total_emt_credit": emt_stats["total_credit"],
        "total_emt_debit": emt_stats["total_debit"],
        "number_of_emt_transactions": emt_stats["transaction_count"],
        "total_wire_credit": wire_stats["total_credit"],
        "total_wire_debit": wire_stats["total_debit"],
        "number_of_wire_transactions": wire_stats["transaction_count"],
    }

    conn.close()
    return report


# Example Usage
if __name__ == "__main__":
    db_path = "../Data/Scotiabank.db"
    customer_id = "SYNCID0000000034"  # Replace with the actual customer ID
    report = generate_customer_report(db_path, customer_id)
    print(json.dumps(report, indent=4))