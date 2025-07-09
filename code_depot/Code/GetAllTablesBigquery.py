import pandas as pd
from google.cloud import bigquery
from google.oauth2 import service_account

#replace credential location with json location
credentials = service_account.Credentials.from_service_account_file(
    "/content/imi-datathon-3bac336d0513 (1).json",
    scopes=["https://www.googleapis.com/auth/bigquery"]
)

client = bigquery.Client(
        project="imi-datathon",
        credentials=credentials,
    )

# Define project ID
project_id = "your_project_id"  # Replace with your GCP project ID

# Retrieve all datasets in the project
datasets = list(client.list_datasets(project=project_id))

# Dictionary to store DataFrames for each table
table_dataframes = {}

# Loop through each dataset
for dataset in datasets:
    dataset_id = dataset.dataset_id
    tables = list(client.list_tables(dataset_id))

    # Loop through each table in the dataset
    for table in tables:
        table_id = table.table_id
        full_table_id = f"{project_id}.{dataset_id}.{table_id}"

        print(f"Fetching data from {full_table_id}...")

        # Run a query to fetch all data from the table
        query = f"SELECT * FROM `{full_table_id}`"
        df = client.query(query).to_dataframe()

        # Store the DataFrame in a dictionary
        table_dataframes[full_table_id] = df

        # Display the DataFrame for the user
        import ace_tools as tools
        tools.display_dataframe_to_user(name=f"Table: {full_table_id}", dataframe=df)

print("Data retrieval complete. All tables are stored in the `table_dataframes` dictionary.")
