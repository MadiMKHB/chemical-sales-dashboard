import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def create_revenue_trend_chart(data):
    """
    Create interactive revenue trend line chart.
    
    This chart:
    - Shows revenue over time with line and markers
    - Uses orange color (#FF6B35) for brand consistency
    - Interactive hover shows exact values
    - Dark theme matches dashboard style
    - Auto-formats currency on Y-axis
    - Shows month names on X-axis
    
    Args:
        data (DataFrame): Monthly KPI data with report_month and total_revenue
        
    Returns:
        plotly.graph_objects.Figure
    """
    fig = go.Figure()
    
    # Sort data chronologically for proper line drawing
    chart_data = data.sort_values('report_month')
    
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(chart_data['report_month']),
        y=chart_data['total_revenue'],
        mode='lines+markers',
        name='Revenue',
        line=dict(color='#FF6B35', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x|%B %Y}</b><br>Revenue: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue ($)",
        height=400,
        hovermode='x unified',
        template='plotly_dark',
        yaxis=dict(tickformat='$,.0f'),
        xaxis=dict(tickformat='%B %Y')
    )
    
    return fig

def create_customer_segment_pie(data):
    """
    Create customer segment distribution pie chart.
    
    This chart:
    - Shows breakdown of customer segments (VIP, Premium, Standard, Basic)
    - Donut style with hole in center
    - Shows percentages on hover
    - Dark theme with auto-colored segments
    
    Args:
        data (DataFrame): Customer data with customer_segment column
        
    Returns:
        plotly.graph_objects.Figure
    """
    segment_counts = data['customer_segment'].value_counts()
    
    fig = go.Figure(data=[go.Pie(
        labels=segment_counts.index,
        values=segment_counts.values,
        hole=.3,
        textposition='inside',
        textinfo='percent+label'
    )])
    
    fig.update_layout(
        height=300,
        template='plotly_dark',
        showlegend=True
    )
    
    return fig

def create_prediction_graph(historical_data, prediction_data, customer, product):
    """
    Create the signature orange-to-blue prediction graph.
    
    This chart:
    - Orange solid line: Historical actual sales
    - Orange dashed line: Connects last historical to prediction
    - Blue dot: Next month's prediction
    - Shows customer-product combination
    - Highlights the prediction transition
    
    Args:
        historical_data (DataFrame): Historical sales with date and quantity
        prediction_data (DataFrame): Single prediction point
        customer (str): Customer ID for title
        product (str): Product name for title
        
    Returns:
        plotly.graph_objects.Figure
    """
    fig = go.Figure()
    
    # Historical data - orange line
    fig.add_trace(go.Scatter(
        x=historical_data['date'],
        y=historical_data['Quantity_sold'],
        mode='lines+markers',
        name='Historical Sales',
        line=dict(color='orange', width=3),
        marker=dict(size=6)
    ))
    
    # Connection line - dashed orange
    if not prediction_data.empty:
        last_historical = historical_data.iloc[-1]
        fig.add_trace(go.Scatter(
            x=[last_historical['date'], prediction_data['date'].iloc[0]],
            y=[last_historical['Quantity_sold'], prediction_data['predicted_quantity'].iloc[0]],
            mode='lines',
            name='Projection',
            line=dict(color='orange', width=2, dash='dash'),
            showlegend=False
        ))
        
        # Prediction point - blue dot
        fig.add_trace(go.Scatter(
            x=prediction_data['date'],
            y=prediction_data['predicted_quantity'],
            mode='markers',
            name='Prediction',
            marker=dict(color='blue', size=12, symbol='circle')
        ))
    
    fig.update_layout(
        title=f"Sales Forecast: {customer} - {product}",
        xaxis_title="Month",
        yaxis_title="Quantity",
        height=500,
        template='plotly_dark',
        hovermode='x unified'
    )
    
    return fig

def create_product_ranking_bar(data, top_n=10):
    """
    Create horizontal bar chart of top products.
    
    This chart:
    - Shows top N products by revenue
    - Horizontal bars for readability of product names
    - Color gradient based on performance
    - Shows exact values on hover
    
    Args:
        data (DataFrame): Product data with product_name and total_revenue_all_time
        top_n (int): Number of top products to show
        
    Returns:
        plotly.graph_objects.Figure
    """
    top_products = data.nlargest(top_n, 'total_revenue_all_time')
    
    fig = go.Figure(go.Bar(
        x=top_products['total_revenue_all_time'],
        y=top_products['product_name'],
        orientation='h',
        marker=dict(
            color=top_products['total_revenue_all_time'],
            colorscale='Viridis'
        ),
        text=top_products['total_revenue_all_time'].apply(lambda x: f'${x:,.0f}'),
        textposition='auto'
    ))
    
    fig.update_layout(
        title=f"Top {top_n} Products by Revenue",
        xaxis_title="Total Revenue ($)",
        yaxis_title="",
        height=400,
        template='plotly_dark',
        yaxis=dict(autorange="reversed")  # Highest at top
    )
    
    return fig
