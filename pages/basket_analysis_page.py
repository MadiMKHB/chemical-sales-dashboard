"""
Create new file: pages/basket_analysis_page.py
Complete basket analysis page with market basket insights
"""
import streamlit as st
import pandas as pd
from utils.data_loader import (
    load_basket_analysis,
    load_top_bundles,
    load_cross_sell_recommendations,
    get_category_cross_sell_stats,
    get_association_strength_distribution,
    load_product_list_for_basket
)
from components.charts import (
    create_association_network,
    create_confidence_matrix,
    create_bundle_opportunity_chart,
    create_category_cross_sell_pie,
    create_lift_distribution_histogram,
    create_confidence_vs_support_scatter
)

def render_basket_analysis_page():
    """Render the complete basket analysis page."""
    st.header("🛒 Basket Analysis")
    
    # Load basket analysis data
    basket_df = load_basket_analysis()
    
    if basket_df is None or basket_df.empty:
        st.error("Unable to load basket analysis data. Please check your BigQuery connection.")
        return
    
    # Page tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "🎯 Bundle Opportunities", 
        "📊 Association Analysis", 
        "🔄 Cross-Sell Engine",
        "📈 Market Insights"
    ])
    
    with tab1:
        render_bundle_opportunities_tab(basket_df)
    
    with tab2:
        render_association_analysis_tab(basket_df)
    
    with tab3:
        render_cross_sell_tab(basket_df)
    
    with tab4:
        render_market_insights_tab(basket_df)

def render_bundle_opportunities_tab(basket_df):
    """Bundle opportunities and recommendations."""
    st.subheader("🎁 Product Bundle Opportunities")
    
    # Load top bundles
    top_bundles = load_top_bundles(15)
    
    if top_bundles is not None and not top_bundles.empty:
        # Bundle opportunity chart
        st.markdown("### 🏆 Top Bundle Opportunities")
        bundle_fig = create_bundle_opportunity_chart(top_bundles)
        st.plotly_chart(bundle_fig, use_container_width=True)
        
        # Bundle recommendations table
        st.markdown("### 📋 Bundle Recommendations")
        
        # Format the table for display
        display_bundles = top_bundles.copy()
        display_bundles['Revenue Potential'] = display_bundles['avg_bundle_revenue'].apply(lambda x: f"₽{x:,.0f}")
        display_bundles['Association'] = display_bundles['association_strength']
        display_bundles['Bundle Score'] = display_bundles['bundle_score'].astype(str) + '/100'
        display_bundles['Support'] = display_bundles['support_pct'].astype(str) + '%'
        display_bundles['Confidence'] = display_bundles['confidence_a_to_b_pct'].astype(str) + '%'
        
        bundle_table = display_bundles[[
            'bundle_name_suggestion', 'Bundle Score', 'Revenue Potential', 
            'Association', 'Support', 'Confidence'
        ]].copy()
        bundle_table.columns = ['Bundle Name', 'Score', 'Avg Revenue', 'Strength', 'Support', 'Confidence']
        
        st.dataframe(bundle_table, hide_index=True, use_container_width=True)
        
        # Bundle insights
        st.markdown("### 💡 Bundle Insights")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            high_score_bundles = len(top_bundles[top_bundles['bundle_score'] >= 70])
            st.metric("High-Value Bundles", f"{high_score_bundles}")
        
        with col2:
            avg_revenue = top_bundles['avg_bundle_revenue'].mean()
            st.metric("Avg Bundle Revenue", f"₽{avg_revenue:,.0f}")
        
        with col3:
            strong_associations = len(top_bundles[top_bundles['association_strength'].str.contains('Strong', na=False)])
            st.metric("Strong Associations", f"{strong_associations}")
        
        # Category analysis
        category_stats = get_category_cross_sell_stats()
        if category_stats is not None and not category_stats.empty:
            st.markdown("### 📊 Bundle Patterns by Category")
            
            # Show category performance
            best_category = category_stats.loc[category_stats['avg_lift'].idxmax()]
            worst_category = category_stats.loc[category_stats['avg_lift'].idxmin()]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.success(f"**Best Cross-Sell Category**\n{best_category['category_relationship']}\nAvg Lift: {best_category['avg_lift']:.2f}x")
            
            with col2:
                st.info(f"**Most Common Pattern**\n{category_stats.iloc[0]['category_relationship']}\n{category_stats.iloc[0]['pair_count']} product pairs")
    
    else:
        st.warning("No bundle opportunities found.")

def render_association_analysis_tab(basket_df):
    """Association rules and network analysis."""
    st.subheader("🔗 Product Association Analysis")
    
    # Association network
    st.markdown("### 🕸️ Product Association Network")
    
    col1, col2 = st.columns([3, 1])
    
    with col2:
        min_lift = st.slider(
            "Minimum Association Strength:",
            min_value=1.0,
            max_value=3.0,
            value=1.2,
            step=0.1,
            help="Higher values show stronger associations"
        )
    
    with col1:
        network_fig = create_association_network(basket_df, min_lift)
        st.plotly_chart(network_fig, use_container_width=True)
    
    # Association analysis
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📈 Association Strength Distribution")
        lift_fig = create_lift_distribution_histogram(basket_df)
        st.plotly_chart(lift_fig, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Support vs Confidence Analysis")
        scatter_fig = create_confidence_vs_support_scatter(basket_df)
        st.plotly_chart(scatter_fig, use_container_width=True)
    
    # Confidence matrix
    st.markdown("### 🔥 Cross-Sell Confidence Matrix")
    st.markdown("*Shows probability of buying product B when customer buys product A*")
    
    confidence_fig = create_confidence_matrix(basket_df)
    st.plotly_chart(confidence_fig, use_container_width=True)
    
    # Association strength breakdown
    strength_dist = get_association_strength_distribution()
    if strength_dist is not None and not strength_dist.empty:
        st.markdown("### 📊 Association Strength Breakdown")
        
        strength_table = strength_dist.copy()
        strength_table['Average Lift'] = strength_table['avg_lift'].round(2)
        strength_table['Bundle Score'] = strength_table['avg_bundle_score'].round(0)
        strength_table['Product Pairs'] = strength_table['count']
        
        display_strength = strength_table[['association_strength', 'Product Pairs', 'Average Lift', 'Bundle Score']]
        display_strength.columns = ['Association Type', 'Pairs', 'Avg Lift', 'Avg Score']
        
        st.dataframe(display_strength, hide_index=True, use_container_width=True)

def render_cross_sell_tab(basket_df):
    """Cross-sell recommendations engine."""
    st.subheader("🎯 Cross-Sell Recommendation Engine")
    
    # Product selector
    products_df = load_product_list_for_basket()
    
    if products_df is not None and not products_df.empty:
        product_options = {}
        for _, row in products_df.iterrows():
            product_options[row['Product_code']] = f"{row['Product_code']} - {row['Product_name']}"
        
        selected_product = st.selectbox(
            "🔍 Select a product to see cross-sell recommendations:",
            options=list(product_options.keys()),
            format_func=lambda x: product_options.get(x, x),
            help="Choose a product to find what customers typically buy with it"
        )
        
        if selected_product:
            # Load cross-sell recommendations
            cross_sell_data = load_cross_sell_recommendations(selected_product)
            
            if cross_sell_data is not None and not cross_sell_data.empty:
                product_name = product_options[selected_product]
                st.markdown(f"### 🛍️ Customers who buy **{product_name}** also buy:")
                
                # Display recommendations
                for idx, rec in cross_sell_data.head(5).iterrows():
                    with st.container():
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        
                        with col1:
                            st.write(f"**{rec['recommended_product_name']}**")
                            st.caption(f"Bundle: {rec['bundle_name_suggestion']}")
                        
                        with col2:
                            confidence_color = "🟢" if rec['confidence_pct'] >= 70 else "🟡" if rec['confidence_pct'] >= 50 else "🔴"
                            st.metric("Confidence", f"{confidence_color} {rec['confidence_pct']:.0f}%")
                        
                        with col3:
                            st.metric("Lift", f"{rec['lift']:.1f}x")
                        
                        with col4:
                            st.metric("Revenue", f"₽{rec['avg_bundle_revenue']:,.0f}")
                
                # Cross-sell insights
                st.markdown("### 💡 Cross-Sell Insights")
                
                top_rec = cross_sell_data.iloc[0]
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.info(f"""
                    **Best Cross-Sell Opportunity:**  
                    {top_rec['recommended_product_name']}  
                    {top_rec['confidence_pct']:.0f}% of customers buy both
                    """)
                
                with col2:
                    avg_bundle_revenue = cross_sell_data['avg_bundle_revenue'].mean()
                    st.success(f"""
                    **Bundle Revenue Potential:**  
                    ₽{avg_bundle_revenue:,.0f} average  
                    {len(cross_sell_data)} cross-sell opportunities
                    """)
            
            else:
                st.warning(f"No cross-sell recommendations found for {product_options[selected_product]}")
    
    else:
        st.error("Unable to load product list for cross-sell analysis.")

def render_market_insights_tab(basket_df):
    """Market basket insights and trends."""
    st.subheader("📈 Market Basket Insights")
    
    # Category cross-sell analysis
    category_stats = get_category_cross_sell_stats()
    
    if category_stats is not None and not category_stats.empty:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏷️ Cross-Sell by Category")
            category_fig = create_category_cross_sell_pie(category_stats)
            st.plotly_chart(category_fig, use_container_width=True)
        
        with col2:
            st.markdown("### 📊 Category Performance")
            
            # Show category stats table
            display_categories = category_stats.copy()
            display_categories['Avg Lift'] = display_categories['avg_lift'].round(2)
            display_categories['Avg Support'] = display_categories['avg_support'].round(1).astype(str) + '%'
            display_categories['Avg Revenue'] = display_categories['avg_revenue'].apply(lambda x: f"₽{x:,.0f}")
            display_categories['Pairs'] = display_categories['pair_count']
            
            category_table = display_categories[['category_relationship', 'Pairs', 'Avg Lift', 'Avg Support', 'Avg Revenue']]
            category_table.columns = ['Category Pattern', 'Pairs', 'Lift', 'Support', 'Revenue']
            
            st.dataframe(category_table, hide_index=True, use_container_width=True)
    
    # Market basket summary
    st.markdown("### 💡 Key Market Insights")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_pairs = len(basket_df)
        st.metric("Total Product Pairs", f"{total_pairs}")
    
    with col2:
        strong_associations = len(basket_df[basket_df['lift'] > 1.5])
        st.metric("Strong Associations", f"{strong_associations}")
    
    with col3:
        avg_bundle_revenue = basket_df['avg_bundle_revenue'].mean()
        st.metric("Avg Bundle Revenue", f"₽{avg_bundle_revenue:,.0f}")
    
    with col4:
        high_confidence = len(basket_df[basket_df['confidence_a_to_b_pct'] >= 70])
        st.metric("High Confidence Pairs", f"{high_confidence}")
    
    # Business recommendations
    st.markdown("### 🎯 Business Recommendations")
    
    # Find best opportunities
    best_bundle = basket_df.loc[basket_df['bundle_score'].idxmax()]
    highest_revenue = basket_df.loc[basket_df['avg_bundle_revenue'].idxmax()]
    strongest_lift = basket_df.loc[basket_df['lift'].idxmax()]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.success(f"""
        **🏆 Best Bundle Opportunity**  
        {best_bundle['bundle_name_suggestion']}  
        Score: {best_bundle['bundle_score']}/100
        """)
    
    with col2:
        st.info(f"""
        **💰 Highest Revenue Bundle**  
        {highest_revenue['product_a_name']} + {highest_revenue['product_b_name']}  
        ₽{highest_revenue['avg_bundle_revenue']:,.0f} average
        """)
    
    with col3:
        st.warning(f"""
        **🔗 Strongest Association**  
        {strongest_lift['product_a_name']} + {strongest_lift['product_b_name']}  
        {strongest_lift['lift']:.1f}x more likely together
        """)
    
    # Footer
    st.markdown("---")
    st.markdown("""
    **ℹ️ About Basket Analysis:**
    - **Support**: Percentage of customers who buy both products
    - **Confidence**: Probability of buying product B when buying product A
    - **Lift**: How much more likely products are bought together vs independently
    - **Bundle Score**: Overall recommendation score for creating product bundles
    """)
