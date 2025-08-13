import streamlit as st
from google.cloud import bigquery
from google.oauth2 import service_account

@st.cache_resource
def get_bigquery_client():
    """
    Initialize and return BigQuery client.
    
    This function:
    - Creates a BigQuery client using service account credentials from Streamlit secrets
    - Caches the client connection for the entire session (doesn't reconnect)
    - Handles authentication errors gracefully
    
    Returns:
        bigquery.Client or None if connection fails
    """
    try:
        credentials = service_account.Credentials.from_service_account_info(
            st.secrets["gcp_service_account"]
        )
        client = bigquery.Client(credentials=credentials)
        return client
    except Exception as e:
        st.error(f"Failed to connect to BigQuery: {e}")
        return None

@st.cache_data(ttl=600)
def run_query(query):
    """
    Execute a BigQuery query and return results as DataFrame.
    
    This function:
    - Takes any SQL query as input
    - Executes it using the cached BigQuery client
    - Returns results as a pandas DataFrame
    - Caches results for 10 minutes (600 seconds) to reduce API calls
    - Handles query errors gracefully
    
    Args:
        query (str): SQL query to execute
        
    Returns:
        pd.DataFrame or None if query fails
    """
    client = get_bigquery_client()
    if client:
        try:
            df = client.query(query).to_dataframe()
            return df
        except Exception as e:
            st.error(f"Query failed: {e}")
            return None
    return None
