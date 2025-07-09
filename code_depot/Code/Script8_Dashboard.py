# -*- coding: utf-8 -*-
"""
Script Name: simple_anomaly_dashboard.py
Description: Robust web app to compare anomaly scores and fetch profiles from customer_reports.csv.
"""

import dash
from dash import dcc, html, Input, Output
import pandas as pd
import numpy as np
import plotly.express as px
import json
from sklearn.preprocessing import MinMaxScaler

# File paths
isolation_file = "../Data/customer_features_with_isolation_forest_scores.csv"
vae_file = "../Data/customer_features_with_vae_scores.csv"
reports_file = "../Data/customer_reports.csv"

# Load data
try:
    isolation_df = pd.read_csv(isolation_file)
    vae_df = pd.read_csv(vae_file)
    customer_reports_df = pd.read_csv(reports_file)
    print("Data loaded successfully!")
except FileNotFoundError as e:
    print(f"Error loading files: {e}")
    exit()

# Ensure column names are consistent
isolation_df.rename(columns={'outlier_score': 'anomaly_score_isolation'}, inplace=True)
vae_df.rename(columns={'outlier_score': 'anomaly_score_vae'}, inplace=True)

# Min-Max scale the anomaly scores separately
scaler_isolation = MinMaxScaler()
isolation_df['anomaly_score_isolation'] = scaler_isolation.fit_transform(
    isolation_df[['anomaly_score_isolation']]
)

scaler_vae = MinMaxScaler()
vae_df['anomaly_score_vae'] = scaler_vae.fit_transform(
    vae_df[['anomaly_score_vae']]
)

# Merge the two dataframes on customer_id
try:
    merged_df = pd.merge(
        isolation_df[['customer_id', 'anomaly_score_isolation']],
        vae_df[['customer_id', 'anomaly_score_vae']],
        on='customer_id'
    )
    print("Data merged successfully!")
except KeyError as e:
    print(f"Error merging data: {e}")
    exit()

# Initialize Dash app
app = dash.Dash(__name__)

# Layout
app.layout = html.Div([
    html.H1("Anomaly Dashboard", style={'textAlign': 'center'}),
    dcc.Graph(id='scatter-plot', style={'height': '70vh'}),
    html.Div(id='customer-profile', style={'padding': '20px', 'border': '1px solid black'})
])

# Helper function to fetch customer profile from customer_reports.csv
def fetch_customer_profile(customer_id):
    profile = customer_reports_df[customer_reports_df['customer_id'] == customer_id]
    return profile

# Callbacks
@app.callback(
    [Output('scatter-plot', 'figure'),
     Output('customer-profile', 'children')],
    [Input('scatter-plot', 'clickData')]
)
def update_graph(click_data):
    # Create scatter plot
    fig = px.scatter(
        merged_df,
        x='anomaly_score_isolation',
        y='anomaly_score_vae',
        color=np.sqrt(merged_df['anomaly_score_isolation']**2 + merged_df['anomaly_score_vae']**2),
        color_continuous_scale='RdBu_r',
        hover_data={'customer_id': True, 'anomaly_score_isolation': True, 'anomaly_score_vae': True},
        title="Anomaly Scores"
    )
    fig.update_traces(marker=dict(size=12))

    profile_text = "Click a point to view the customer profile."

    if click_data:
        customer_id = click_data['points'][0]['customdata'][0]
        profile = fetch_customer_profile(customer_id)
        if not profile.empty:
            profile_dict = profile.iloc[0].to_dict()
            profile_json = json.dumps(profile_dict, indent=4)
            profile_text = html.Pre(
                profile_json,
                style={'whiteSpace': 'pre-wrap', 'fontSize': '16px'}
            )

    return fig, profile_text

# Run the app
if __name__ == "__main__":
    app.run_server(debug=True, port=8051)
