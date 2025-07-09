# -*- coding: utf-8 -*-
"""
Script Name: isolation_forest_outlier_scores.py
Description: Identifies outlier scores in customer_features.csv using Isolation Forest.
Author: Ernest
Date: Jan 2025
Version: 1.0
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
import matplotlib.pyplot as plt

def load_and_preprocess(file_path):
    """
    Load customer features CSV and preprocess the data.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame, np.ndarray: Original DataFrame and scaled numerical features as NumPy array.
    """
    # Load the data
    df = pd.read_csv(file_path)

    # Drop non-numerical columns like customer_id
    if 'customer_id' in df.columns:
        features = df.drop(columns=['customer_id'])
    else:
        features = df.copy()

    # Scale the data
    scaler = StandardScaler()
    X = scaler.fit_transform(features)

    return df, X


def calculate_outlier_scores_with_isolation_forest(X, contamination=0.05):
    """
    Calculate outlier scores using Isolation Forest.

    Args:
        X (np.ndarray): Scaled numerical features.
        contamination (float): Proportion of outliers in the data.

    Returns:
        np.ndarray: Array of outlier scores.
    """
    # Initialize Isolation Forest
    model = IsolationForest(n_estimators=100, contamination=contamination, random_state=42)
    model.fit(X)

    # Compute anomaly scores
    scores = -model.decision_function(X)  # Higher scores indicate higher likelihood of being an outlier
    return scores


def visualize_outliers(X, scores):
    """
    Visualize outlier scores in 2D using PCA.

    Args:
        X (np.ndarray): Scaled input features.
        scores (np.ndarray): Outlier scores.
    """
    # Reduce dimensions for visualization
    pca = PCA(n_components=2)
    X_pca = pca.fit_transform(X)

    plt.figure(figsize=(8, 6))
    scatter = plt.scatter(X_pca[:, 0], X_pca[:, 1], c=scores, cmap='coolwarm', alpha=0.8)
    plt.title("Outlier Scores using Isolation Forest")
    plt.xlabel("PCA Component 1")
    plt.ylabel("PCA Component 2")
    plt.colorbar(scatter, label="Outlier Score")
    plt.show()


if __name__ == "__main__":
    # File paths
    input_file = "../Data/customer_features.csv"
    output_file = "../Data/customer_features_with_isolation_forest_scores.csv"

    # Load and preprocess the data
    print("Loading and preprocessing data...")
    df, X = load_and_preprocess(input_file)
    print("Data loaded successfully!")

    # Calculate outlier scores using Isolation Forest
    print("Calculating outlier scores using Isolation Forest...")
    scores = calculate_outlier_scores_with_isolation_forest(X, contamination=0.05)
    df['outlier_score'] = scores
    print("Outlier scores calculated!")

    # Save results to CSV
    df.to_csv(output_file, index=False)
    print(f"Data with outlier scores saved to {output_file}")

    # Visualize outlier scores
    print("Visualizing outlier scores...")
    visualize_outliers(X, scores)
