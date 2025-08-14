"""
Main application entry point.
Chemical Sales Dashboard with modular structure.
"""
import streamlit as st
from pages.overview_page import render_overview_page
from pages.customers_page import render_customers_page
from pages.predictions_page import render_predictions_page

# Page configuration
st.set_page_config(
    page_title="Chemical Sales Dashboard",
    page_icon="🧪",
    layout="wide"
)

st.title("🧪 Chemical Sales Dashboard")

# Navigation tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Overview", 
    "📈 Predictions", 
    "👥 Customers",
    "📦 Products"
])

with tab1:
    render_overview_page()

with tab2:
    render_predictions_page()

with tab3:
    render_customers_page()

with tab4:
    st.header("Product Analytics")
    st.info("Coming soon: Product performance metrics")

# Footer
st.markdown("---")
st.markdown("*Dashboard refreshes weekly via scheduled BigQuery queries.*")
