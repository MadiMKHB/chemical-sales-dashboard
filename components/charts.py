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

"""
Add this function to components/charts.py
"""
import plotly.graph_objects as go
import pandas as pd

def create_prediction_graph(historical_data, prediction_value, customer, product, prediction_month):
    """
    Create the signature orange-to-blue prediction graph.
    Historical = orange solid line + markers
    Prediction = blue dot with orange dashed connector
    """
    fig = go.Figure()
    
    if historical_data.empty:
        # Empty state
        fig.add_annotation(
            text="No historical data available for this combination",
            xref="paper", yref="paper",
            x=0.5, y=0.5, 
            showarrow=False,
            font=dict(size=16, color="gray")
        )
    else:
        # Historical data - orange solid line with markers
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(historical_data['date']),
            y=historical_data['Quantity_sold'],
            mode='lines+markers',
            name='Historical Sales',
            line=dict(color='#FF6B35', width=3),  # Orange to match your theme
            marker=dict(size=6, color='#FF6B35'),
            hovertemplate='<b>%{x|%B %Y}</b><br>Quantity: %{y}<br><extra></extra>'
        ))
        
        # Add prediction if available
        if prediction_value is not None and prediction_value > 0:
            last_date = pd.to_datetime(historical_data['date'].iloc[-1])
            # Calculate prediction date based on prediction_month
            pred_year, pred_month = prediction_month.split('_')
            pred_date = pd.to_datetime(f"{pred_year}-{pred_month}-01")
            last_quantity = historical_data['Quantity_sold'].iloc[-1]
            
            # Dashed orange line connecting to prediction
            fig.add_trace(go.Scatter(
                x=[last_date, pred_date],
                y=[last_quantity, prediction_value],
                mode='lines',
                name='Projection',
                line=dict(color='#FF6B35', width=2, dash='dash'),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Blue prediction dot
            fig.add_trace(go.Scatter(
                x=[pred_date],
                y=[prediction_value],
                mode='markers',
                name='ML Prediction',
                marker=dict(
                    color='#4A90E2',  # Blue
                    size=15, 
                    symbol='circle',
                    line=dict(color='#2E5C8A', width=2)
                ),
                hovertemplate='<b>Prediction</b><br>%{x|%B %Y}<br>Quantity: %{y:.1f}<br><extra></extra>'
            ))
    
    # Layout with dark theme
    fig.update_layout(
        title=dict(
            text=f"Sales Forecast: {customer} - {product}",
            font=dict(size=18, color='white'),
            x=0.5
        ),
        xaxis_title="Month",
        yaxis_title="Quantity",
        height=500,
        template='plotly_dark',
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        hovermode='x unified',
        xaxis=dict(
            tickformat='%b %Y',
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            zeroline=False
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.1)',
            zeroline=False,
            rangemode='tozero'
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(0,0,0,0.5)'
        ),
        margin=dict(t=80, b=60, l=60, r=60)
    )
    
    return fig
