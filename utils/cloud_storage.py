"""
Cloud Storage utilities for loading prediction files.
Add this to utils/cloud_storage.py (create new file)
"""
import streamlit as st
import pandas as pd
import io
from google.cloud import storage
from google.oauth2 import service_account

@st.cache_resource
def get_storage_client():
    """Initialize and return Cloud Storage client."""
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        client = storage.Client(credentials=credentials)
        return client
    except Exception as e:
        st.error(f"Failed to connect to Cloud Storage: {e}")
        return None

@st.cache_data(ttl=300)  # Cache for 5 minutes
def get_available_prediction_months():
    """Get list of available prediction months from Cloud Storage."""
    client = get_storage_client()
    if not client:
        return []
    
    try:
        bucket = client.bucket('ml-goldman-hotels-vit-vertex-bucket')
        blobs = bucket.list_blobs(prefix='streamlit_exports/predictions_')
        
        months = set()
        for blob in blobs:
            if blob.name.endswith('.csv'):
                # Extract YYYY_MM from filename like predictions_2025_07_20250810_203934.csv
                filename = blob.name.split('/')[-1]  # Get filename only
                if filename.startswith('predictions_'):
                    parts = filename.split('_')
                    if len(parts) >= 3:
                        year = parts[1]
                        month = parts[2]
                        months.add(f"{year}_{month}")
        
        return sorted(list(months), reverse=True)  # Latest first
    except Exception as e:
        st.error(f"Failed to get available months: {e}")
        return []

@st.cache_data(ttl=300)
def load_predictions_from_gcs(year_month="2025_07"):
    """Load predictions from Cloud Storage CSV for specific month."""
    client = get_storage_client()
    if not client:
        return pd.DataFrame()
    
    try:
        bucket = client.bucket('ml-goldman-hotels-vit-vertex-bucket')
        
        # Find prediction file for the month (with timestamp)
        blobs = bucket.list_blobs(prefix=f'streamlit_exports/predictions_{year_month}')
        
        for blob in blobs:
            if blob.name.endswith('.csv'):
                # Download CSV content
                content = blob.download_as_text()
                df = pd.read_csv(io.StringIO(content))
                return df
        
        return pd.DataFrame()
    except Exception as e:
        st.error(f"Failed to load predictions for {year_month}: {e}")
        return pd.DataFrame()

def format_month_display(year_month):
    """Convert '2025_07' to 'July 2025' for display."""
    try:
        year, month = year_month.split('_')
        month_names = {
            '01': 'January', '02': 'February', '03': 'March', '04': 'April',
            '05': 'May', '06': 'June', '07': 'July', '08': 'August',
            '09': 'September', '10': 'October', '11': 'November', '12': 'December'
        }
        return f"{month_names.get(month, month)} {year}"
    except:
        return year_month
