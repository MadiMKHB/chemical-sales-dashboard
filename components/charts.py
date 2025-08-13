"""
Chart components using Plotly.
All charts use dark theme and Ruble currency.
"""
import plotly.graph_objects as go
import pandas as pd
import streamlit as st

def create_revenue_trend_chart(data):
    """Create interactive revenue trend line chart."""
    fig = go.Figure()
    
    # Sort data chronologically
    chart_data = data.sort_values('report_month')
    
    fig.add_trace(go.Scatter(
        x=pd.to_datetime(chart_data['report_month']),
        y=chart_data['total_revenue'],
        mode='lines+markers',
        name='Revenue',
        line=dict(color='#FF6B35', width=3),
        marker=dict(size=8),
        hovertemplate='<b>%{x|%B %Y}</b><br>Revenue: ₽%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        xaxis_title="Month",
        yaxis_title="Revenue (₽)",
        height=400,
        hovermode='x unified',
        template='plotly_dark',
        yaxis=dict(tickformat=',.0f', tickprefix='₽'),
        xaxis=dict(tickformat='%B %Y')
    )
    
    return fig

def create_customer_segment_pie(data):
    """Create customer segment distribution pie chart."""
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
