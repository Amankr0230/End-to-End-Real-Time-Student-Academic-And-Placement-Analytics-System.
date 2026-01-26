import pandas as pd
import os

def load_data():
    """
    Load final prediction data for Streamlit dashboard.
    For deployment, we use CSV instead of local MySQL.
    """
    # Ensure the path works both locally and in cloud
    csv_path = os.path.join(os.path.dirname(__file__), "final_predictions.csv")
    df = pd.read_csv(csv_path)
    return df
