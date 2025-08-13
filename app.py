import streamlit as st
from pages.overview_page import render_overview_page
from pages.customers_page import render_customers_page

# Page configuration - must be first Streamlit command
st.set_page_config(
    page_title="Chemical Sales Dashboard",
    page_icon="🧪",
    layout="wide",  # Use full screen width
    initial_sidebar_state="collapsed"  # Start with sidebar closed
)

# Application title with emoji for visual appeal
st.title("🧪 Chemical Sales Dashboard")

# Create navigation tabs
# Each tab represents a major section of the dashboard
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Overview",      # KPIs and trends
    "📈 Predictions",   # Sales forecasting
    "👥 Customers",     # Customer analytics
    "📦 Products",      # Product performance
    "🛒 Basket"         # Basket analysis
])

# Render content for each tab
with tab1:
    # Overview page with KPIs
    render_overview_page()

with tab2:
    # Predictions page (to be implemented)
    st.header("Sales Predictions")
    st.info("Coming soon: Historical vs Predicted sales graph with customer/product selection")
    # TODO: Add render_predictions_page() when ready

with tab3:
    # Customer analytics page
    render_customers_page()

with tab4:
    # Products page (to be implemented)
    st.header("Product Analytics")
    st.info("Coming soon: Product rankings, seasonality, and performance metrics")
    # TODO: Add render_products_page() when ready

with tab5:
    # Basket analysis page (to be implemented)
    st.header("Basket Analysis")
    st.info("Coming soon: Product associations and bundling opportunities")
    # TODO: Add render_basket_page() when ready

# Footer with metadata
st.markdown("---")
st.markdown("*Dashboard refreshes weekly via scheduled BigQuery queries. "
           "Data sourced from Vertex AI ML pipeline.*")

# Sidebar (if needed in future)
# with st.sidebar:
#     st.header("Filters")
#     # Add global filters here
