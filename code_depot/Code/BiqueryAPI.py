from google.cloud import bigquery
from google.oauth2 import service_account

def initialize_client():
    """
    Initialize the BigQuery client.
    Replace credentials.json with the path to your service account key file.

    Returns:
        bigquery.Client: The BigQuery client object.
    """

    credentials = service_account.Credentials.from_service_account_file(
    "/content/imi-datathon-3bac336d0513 (1).json",
    scopes=["https://www.googleapis.com/auth/bigquery"]
)

    client = bigquery.Client(
        project="imi-datathon",
        credentials=credentials,
        # location="australia-southeast1"
    )
    return client

def run_query(client, query):
    """
    Run a query on BigQuery and return the results.

    Args:
        client (bigquery.Client): The BigQuery client object.
        query (str): The SQL query to execute.

    Returns:
        list: The query results as a list of dictionaries.
    """
    query_job = client.query(query)  # Make an API request
    results = query_job.result()  # Wait for the job to complete
    # Convert results to a DataFrame
    df = results.to_dataframe()
    return df

# def insert_data(client, dataset_id, table_id, rows_to_insert):
#     """
#     Insert data into a BigQuery table.

#     Args:
#         client (bigquery.Client): The BigQuery client object.
#         dataset_id (str): The dataset ID.
#         table_id (str): The table ID.
#         rows_to_insert (list): List of rows (as dictionaries) to insert.

#     Returns:
#         None
#     """
#     table_ref = client.dataset(dataset_id).table(table_id)
#     table = client.get_table(table_ref)  # Fetch the table

#     errors = client.insert_rows_json(table, rows_to_insert)  # Insert rows
#     if errors:
#         print("Errors occurred while inserting data:", errors)
#     else:
#         print("Data inserted successfully.")

def main():
    # Initialize BigQuery client
    client = initialize_client()

    # Example: Running a query
    query = """
        SELECT * FROM `imi-datathon.IMI_Dataset.abm` LIMIT 1000
    """
    df = run_query(client, query)
    print(df)

    # # Example: Inserting data into a table
    # dataset_id = "your_dataset_id"
    # table_id = "your_table_id"
    # rows_to_insert = [
    #     {"column1": "value1", "column2": "value2"},
    #     {"column1": "value3", "column2": "value4"},
    # ]
    # insert_data(client, dataset_id, table_id, rows_to_insert)

if __name__ == "__main__":
    main()
