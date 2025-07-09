#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 20:45:22 2025

@author: ernest
"""


import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
import torch
from torch import nn, optim
from torch.utils.data import DataLoader, TensorDataset


class TransformerVAE(nn.Module):
    def __init__(self, input_dim, latent_dim, num_heads, num_layers):
        super(TransformerVAE, self).__init__()

        # Adjust input_dim to be divisible by num_heads
        self.adjusted_input_dim = input_dim
        if input_dim % num_heads != 0:
            self.adjusted_input_dim = num_heads * ((input_dim // num_heads) + 1)

        # Linear layer to project input features to adjusted input dimension
        self.input_projection = nn.Linear(input_dim, self.adjusted_input_dim)

        # Encoder
        self.encoder_layer = nn.TransformerEncoderLayer(d_model=self.adjusted_input_dim, nhead=num_heads)
        self.encoder = nn.TransformerEncoder(self.encoder_layer, num_layers=num_layers)

        self.fc_mu = nn.Linear(self.adjusted_input_dim, latent_dim)
        self.fc_logvar = nn.Linear(self.adjusted_input_dim, latent_dim)

        # Decoder
        self.latent_to_embedding = nn.Linear(latent_dim, self.adjusted_input_dim)
        self.decoder_layer = nn.TransformerDecoderLayer(d_model=self.adjusted_input_dim, nhead=num_heads)
        self.decoder = nn.TransformerDecoder(self.decoder_layer, num_layers=num_layers)
        self.fc_out = nn.Linear(self.adjusted_input_dim, input_dim)  # Output back to original input_dim

    def forward(self, x):
        # Project input to adjusted dimension
        x = self.input_projection(x)

        # Encoding
        encoded = self.encoder(x)
        mu = self.fc_mu(encoded.mean(dim=0))
        logvar = self.fc_logvar(encoded.mean(dim=0))

        # Reparameterization trick
        std = torch.exp(0.5 * logvar)
        z = mu + std * torch.randn_like(std)

        # Map latent vector back to embedding size
        z_projected = self.latent_to_embedding(z)
        z_repeated = z_projected.unsqueeze(0).repeat(x.size(0), 1, 1)

        # Decoding
        decoded = self.decoder(z_repeated, encoded)
        reconstructed = self.fc_out(decoded)

        return reconstructed, mu, logvar


def load_and_preprocess(file_path):
    """
    Load customer features CSV and preprocess the data.

    Args:
        file_path (str): Path to the CSV file.

    Returns:
        pd.DataFrame, torch.Tensor: Original DataFrame and normalized numerical features as a PyTorch tensor.
    """
    df = pd.read_csv(file_path)

    # Drop non-numerical columns like customer_id
    if 'customer_id' in df.columns:
        features = df.drop(columns=['customer_id'])
    else:
        features = df.copy()

    # Replace -999 with NaN
    features.replace(-999, np.nan, inplace=True)

    # Create binary indicators for missing values
    for column in features.columns:
        if features[column].isnull().any():
            features[f'{column}_missing'] = features[column].isnull().astype(int)

    # Impute missing values with column medians
    features.fillna(features.median(), inplace=True)

    # Scale the data using MinMaxScaler
    scaler = MinMaxScaler()
    X = scaler.fit_transform(features)

    return df, torch.tensor(X, dtype=torch.float32), scaler

# # Load and preprocess data
# def load_and_preprocess(file_path):
#     """
#     Load customer features CSV and preprocess the data.

#     Args:
#         file_path (str): Path to the CSV file.

#     Returns:
#         pd.DataFrame, torch.Tensor: Original DataFrame and normalized numerical features as a PyTorch tensor.
#     """
#     df = pd.read_csv(file_path)

#     # Drop non-numerical columns like customer_id
#     if 'customer_id' in df.columns:
#         features = df.drop(columns=['customer_id'])
#     else:
#         features = df.copy()

#     # Scale the data
#     scaler = StandardScaler()
#     X = scaler.fit_transform(features)

#     return df, torch.tensor(X, dtype=torch.float32), scaler

# Train the VAE
def train_vae(model, dataloader, optimizer, epochs=50):
    model.train()
    for epoch in range(epochs):
        total_loss = 0
        for batch in dataloader:
            x = batch[0].permute(1, 0, 2)  # Transformer expects (seq_len, batch_size, feature_dim)
            optimizer.zero_grad()

            reconstructed, mu, logvar = model(x)
            reconstruction_loss = nn.MSELoss()(reconstructed, x)
            kl_divergence = -0.5 * torch.sum(1 + logvar - mu.pow(2) - logvar.exp())

            loss = reconstruction_loss + kl_divergence
            loss.backward()
            optimizer.step()

            total_loss += loss.item()

        print(f"Epoch {epoch + 1}/{epochs}, Loss: {total_loss / len(dataloader)}")

# Calculate anomaly scores
def calculate_anomaly_scores(model, dataloader):
    model.eval()
    scores = []
    with torch.no_grad():
        for batch in dataloader:
            x = batch[0].permute(1, 0, 2)
            reconstructed, _, _ = model(x)
            loss = nn.MSELoss(reduction='none')(reconstructed, x).mean(dim=-1)
            scores.extend(loss.mean(dim=0).tolist())
    return scores

if __name__ == "__main__":
    # File paths
    input_file = "../Data/customer_features.csv"
    output_file = "../Data/customer_features_with_vae_scores.csv"

    # Load and preprocess the data
    print("Loading and preprocessing data...")
    df, X, scaler = load_and_preprocess(input_file)
    print("Data loaded successfully!")

    # Create DataLoader
    dataset = TensorDataset(X.unsqueeze(1))  # Add a dimension for sequence length
    dataloader = DataLoader(dataset, batch_size=32, shuffle=True)

    # Initialize the model
    input_dim = X.size(-1)
    latent_dim = 16
    num_heads = 4
    num_layers = 2
    model = TransformerVAE(input_dim=input_dim, latent_dim=latent_dim, num_heads=num_heads, num_layers=num_layers)
    optimizer = optim.Adam(model.parameters(), lr=0.0005)

    # Train the model
    print("Training VAE...")
    train_vae(model, dataloader, optimizer, epochs=20)

    # Save the trained model
    torch.save(model.state_dict(), "../Models/transformer_vae.pth")
    print("Model saved to ../Models/transformer_vae.pth")


    # Calculate anomaly scores
    print("Calculating anomaly scores...")
    anomaly_scores = calculate_anomaly_scores(model, dataloader)
    df['outlier_score'] = anomaly_scores
    print("Anomaly scores calculated!")

    # Save results to CSV
    df.to_csv(output_file, index=False)
    print(f"Data with anomaly scores saved to {output_file}")
