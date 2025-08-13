import streamlit as st
from utils.data_loader import load_customer_analytics
from components.kpi_cards import display_customer_metrics

def render_customers_page():
    """
    Render the customer analytics page.
    
    This page includes:
    - Customer segment breakdown (VIP, Premium, Standard, Basic)
    - Top 10 customers table by revenue
    - Customer selector for detailed view
    - Individual customer metrics and risk indicators
    
    Layout:
    - Left column: Segment counts
    - Right column: Top customers table
    - Bottom: Customer detail selector and metrics
    """
    st.header("Customer Analytics")
    
    # Load customer data
    customer_df = load_customer_analytics()
    
    if customer_df is not None and not customer_df.empty:
        # Two-column layout for segments and top customers
        col1, col2 = st.columns([1, 2])
        
        with col1:
            render_segment_summary(customer_df)
        
        with col2:
            render_top_customers(customer_df)
        
        # Customer detail section
        st.markdown("---")
        render_customer_detail(customer_df)
    else:
        st.info("Loading customer data...")

def render_segment_summary(customer_df):
    """
    Display customer segment distribution.
    
    Shows:
    - Count of customers in each segment
    - Segment names with counts
    - Could be extended with a pie chart
    
    Args:
        customer_df (DataFrame): Customer analytics data
    """
    st.subheader("Customer Segments")
    segment_counts = customer_df['customer_segment'].value_counts()
    for segment, count in segment_counts.items():
        # Use different emoji for each segment
        if segment == 'VIP':
            emoji = "👑"
        elif segment == 'Premium':
            emoji = "⭐"
        elif segment == 'Standard':
            emoji = "👤"
        else:
            emoji = "🆕"
        st.write(f"{emoji} **{segment}**: {count} customers")

def render_top_customers(customer_df):
    """
    Display top customers table.
    
    Shows:
    - Top 10 customers by lifetime revenue
    - Customer ID, revenue, growth status
    - Formatted as interactive dataframe
    
    Args:
        customer_df (DataFrame): Customer analytics data
    """
    st.subheader("Top 10 Customers by Revenue")
    
    # Select and format top customers
    top_customers = customer_df.head(10)[
        ['customer_id', 'total_lifetime_revenue', 'growth_status', 'churn_risk']
    ].copy()
    
    # Format revenue as currency
    top_customers['total_lifetime_revenue'] = top_customers[
        'total_lifetime_revenue'
    ].apply(lambda x: f"${x:,.0f}")
    
    # Rename columns for display
    top_customers.columns = ['Customer', 'Lifetime Revenue', 'Growth', 'Risk']
    
    # Display as interactive dataframe
    st.dataframe(
        top_customers, 
        hide_index=True, 
        use_container_width=True
    )

def render_customer_detail(customer_df):
    """
    Render detailed view for selected customer.
    
    Shows:
    - Customer selector dropdown
    - 4 metric cards for selected customer
    - Favorite product information
    - Growth and risk indicators with color coding
    
    Args:
        customer_df (DataFrame): Customer analytics data
    """
    st.subheader("Customer Detail View")
    
    # Customer selector
    selected_customer = st.selectbox(
        "Select a customer to view details:",
        options=customer_df['customer_id'].tolist(),
        format_func=lambda x: f"{x} - {customer_df[customer_df['customer_id']==x]['customer_segment'].iloc[0]}"
    )
    
    if selected_customer:
        # Get selected customer's data
        cust_data = customer_df[
            customer_df['customer_id'] == selected_customer
        ].iloc[0]
        
        # Display customer metrics
        display_customer_metrics(cust_data)
        
        # Show favorite product if available
        if pd.notna(cust_data['favorite_product_1_name']):
            st.info(f"**Favorite Product:** {cust_data['favorite_product_1_name']}")
