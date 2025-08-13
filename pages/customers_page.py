"""
Customer analytics page.
"""
import streamlit as st
import pandas as pd
from utils.data_loader import load_customer_analytics

def render_customers_page():
    """Render the customer analytics page."""
    st.header("Customer Analytics")
    
    # Load customer data
    customer_df = load_customer_analytics()
    
    if customer_df is not None and not customer_df.empty:
        # Two-column layout
        col1, col2 = st.columns([1, 2])
        
        with col1:
            st.subheader("Customer Segments")
            segment_counts = customer_df['customer_segment'].value_counts()
            for segment, count in segment_counts.items():
                emoji = "👑" if segment == 'VIP' else "⭐" if segment == 'Premium' else "👤"
                st.write(f"{emoji} **{segment}**: {count} customers")
        
        with col2:
            st.subheader("Top 10 Customers by Revenue")
            top_customers = customer_df.head(10)[
                ['customer_id', 'total_lifetime_revenue', 'growth_status', 'churn_risk']
            ].copy()
            
            # Format revenue as Rubles
            top_customers['total_lifetime_revenue'] = top_customers[
                'total_lifetime_revenue'
            ].apply(lambda x: f"₽{x:,.0f}")
            
            # Rename columns
            top_customers.columns = ['Customer', 'Lifetime Revenue', 'Growth', 'Risk']
            
            st.dataframe(top_customers, hide_index=True, use_container_width=True)
        
        # Customer detail section
        st.markdown("---")
        st.subheader("Customer Detail View")
        
        selected_customer = st.selectbox(
            "Select a customer to view details:",
            options=customer_df['customer_id'].tolist()
        )
        
        if selected_customer:
            cust_data = customer_df[
                customer_df['customer_id'] == selected_customer
            ].iloc[0]
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Lifetime Revenue", f"₽{cust_data['total_lifetime_revenue']:,.0f}")
            
            with col2:
                st.metric("Last 3 Months", f"₽{cust_data['revenue_last_3_months']:,.0f}")
            
            with col3:
                status_color = "🟢" if cust_data['growth_status'] == 'Growing' else "🟡" if cust_data['growth_status'] == 'Stable' else "🔴"
                st.metric("Growth Status", f"{status_color} {cust_data['growth_status']}")
            
            with col4:
                risk_color = "🔴" if "High" in str(cust_data['churn_risk']) else "🟡" if "Medium" in str(cust_data['churn_risk']) else "🟢"
                st.metric("Churn Risk", f"{risk_color} {cust_data['churn_risk']}")
            
            if pd.notna(cust_data['favorite_product_1_name']):
                st.info(f"**Favorite Product:** {cust_data['favorite_product_1_name']}")
    else:
        st.info("Loading customer data...")
