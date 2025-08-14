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

"""
Updated chart functions in components/charts.py for your existing data structure
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

def create_product_performance_graph_existing(historical_data, prediction_data, product_name, prediction_month):
    """
    Create product performance graph using your existing data structure.
    Shows total market demand for this product + prediction.
    """
    fig = go.Figure()
    
    if historical_data.empty:
        # Empty state
        fig.add_annotation(
            text="No historical data available for this product",
            xref="paper", yref="paper",
            x=0.5, y=0.5, 
            showarrow=False,
            font=dict(size=16, color="gray")
        )
    else:
        # Historical data - orange solid line with markers
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(historical_data['month']),
            y=historical_data['total_quantity'],
            mode='lines+markers',
            name='Historical Market Demand',
            line=dict(color='#FF6B35', width=3),
            marker=dict(size=6, color='#FF6B35'),
            hovertemplate='<b>%{x|%B %Y}</b><br>Total Demand: %{y} units<br>Active Customers: %{customdata}<br><extra></extra>',
            customdata=historical_data['customer_count']
        ))
        
        # Add prediction if available
        if prediction_data and prediction_data['total_predicted_quantity'] > 0:
            last_date = pd.to_datetime(historical_data['month'].iloc[-1])
            pred_year, pred_month = prediction_month.split('_')
            pred_date = pd.to_datetime(f"{pred_year}-{pred_month}-01")
            last_quantity = historical_data['total_quantity'].iloc[-1]
            pred_quantity = prediction_data['total_predicted_quantity']
            
            # Dashed orange line connecting to prediction
            fig.add_trace(go.Scatter(
                x=[last_date, pred_date],
                y=[last_quantity, pred_quantity],
                mode='lines',
                name='Projection',
                line=dict(color='#FF6B35', width=2, dash='dash'),
                showlegend=False,
                hoverinfo='skip'
            ))
            
            # Blue prediction dot
            confidence_text = ""
            if prediction_data.get('avg_confidence'):
                confidence_text = f"<br>Confidence: {prediction_data['avg_confidence']:.1%}"
            
            fig.add_trace(go.Scatter(
                x=[pred_date],
                y=[pred_quantity],
                mode='markers',
                name='Market Forecast',
                marker=dict(
                    color='#4A90E2',
                    size=15, 
                    symbol='circle',
                    line=dict(color='#2E5C8A', width=2)
                ),
                hovertemplate=f'<b>Forecast</b><br>%{{x|%B %Y}}<br>Predicted Demand: %{{y:.1f}} units<br>Expected Customers: {prediction_data["customer_count"]}{confidence_text}<br><extra></extra>'
            ))
    
    # Layout
    fig.update_layout(
        title=dict(
            text=f"Market Demand Forecast: {product_name}",
            font=dict(size=18, color='white'),
            x=0.5
        ),
        xaxis_title="Month",
        yaxis_title="Total Market Demand (Units)",
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

def create_product_comparison_chart_existing(comparison_data):
    """Create comparison chart for multiple products using your data."""
    if comparison_data.empty:
        return go.Figure()
    
    fig = go.Figure()
    
    # Color palette for different products
    colors = ['#FF6B35', '#4A90E2', '#50C878', '#FFD700', '#FF69B4', '#20B2AA']
    
    # Create a line for each product
    for i, product_code in enumerate(comparison_data['Product_code'].unique()):
        product_data = comparison_data[comparison_data['Product_code'] == product_code]
        product_name = product_data['product_name'].iloc[0]
        color = colors[i % len(colors)]
        
        fig.add_trace(go.Scatter(
            x=pd.to_datetime(product_data['month']),
            y=product_data['total_quantity'],
            mode='lines+markers',
            name=f"{product_name}",
            line=dict(width=3, color=color),
            marker=dict(size=6, color=color),
            hovertemplate=f'<b>{product_name}</b><br>%{{x|%B %Y}}<br>Demand: %{{y}} units<br>Customers: %{{customdata}}<extra></extra>',
            customdata=product_data['customer_count']
        ))
    
    fig.update_layout(
        title="Product Comparison - Market Demand Trends",
        xaxis_title="Month",
        yaxis_title="Total Market Demand (Units)",
        height=500,
        template='plotly_dark',
        hovermode='x unified',
        legend=dict(
            orientation="v",
            yanchor="top",
            y=1,
            xanchor="left",
            x=1.02
        )
    )
    
    return fig

def create_category_revenue_pie_existing(category_data):
    """Create pie chart using your category revenue data."""
    if category_data.empty:
        return go.Figure()
    
    fig = go.Figure(data=[go.Pie(
        labels=category_data['product_type'],
        values=category_data['category_revenue'],
        hole=.3,
        textposition='inside',
        textinfo='percent+label',
        hovertemplate='<b>%{label}</b><br>Revenue: ₽%{value:,.0f}<br>Products: %{customdata} products<br>Share: %{percent}<extra></extra>',
        customdata=category_data['product_count']
    )])
    
    fig.update_layout(
        title="Revenue Distribution by Product Category",
        height=400,
        template='plotly_dark',
        showlegend=True,
        margin=dict(t=60, b=40, l=40, r=40)
    )
    
    return fig

def create_growth_chart_existing(growth_data):
    """Create growth chart using your existing growth data."""
    if growth_data.empty:
        return go.Figure()
    
    # Color code by growth level
    colors = []
    for growth in growth_data['quantity_growth_pct']:
        if growth > 50:
            colors.append('#4CAF50')  # Dark green for high growth
        elif growth > 20:
            colors.append('#8BC34A')  # Light green for good growth
        else:
            colors.append('#FFC107')  # Yellow for moderate growth
    
    fig = go.Figure(data=[
        go.Bar(
            x=growth_data['quantity_growth_pct'],
            y=growth_data['product_name'],
            orientation='h',
            marker_color=colors,
            hovertemplate='<b>%{y}</b><br>Growth: %{x:.1f}%<br>Status: %{customdata}<extra></extra>',
            customdata=growth_data['trend_direction']
        )
    ])
    
    fig.update_layout(
        title=f"Top Growing Products (Quantity Growth)",
        xaxis_title="Growth Rate (%)",
        yaxis_title="Product",
        height=400,
        template='plotly_dark',
        margin=dict(l=200)
    )
    
    return fig

def create_seasonality_heatmap_existing(seasonality_data):
    """Create seasonality heatmap using your seasonal_patterns data."""
    if seasonality_data.empty:
        return go.Figure()
    
    month_names = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 
                   'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
    
    # Take top 10 products by seasonality strength
    top_seasonal = seasonality_data.head(10)
    
    # Create matrix for heatmap
    heatmap_data = []
    product_names = []
    
    for _, product in top_seasonal.iterrows():
        product_names.append(product['product_name'] if pd.notna(product['product_name']) else product['product_code'])
        
        # Extract monthly indices
        monthly_values = [
            product['jan_index'], product['feb_index'], product['mar_index'],
            product['apr_index'], product['may_index'], product['jun_index'],
            product['jul_index'], product['aug_index'], product['sep_index'],
            product['oct_index'], product['nov_index'], product['dec_index']
        ]
        
        # Convert NaN to 1.0 (average)
        monthly_values = [val if pd.notna(val) else 1.0 for val in monthly_values]
        heatmap_data.append(monthly_values)
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_data,
        x=month_names,
        y=product_names,
        colorscale='RdYlBu_r',  # Red for high, blue for low
        colorbar=dict(title="Seasonal Index"),
        hovertemplate='<b>%{y}</b><br>%{x}: %{z:.2f}x average<extra></extra>'
    ))
    
    fig.update_layout(
        title="Product Seasonality Patterns",
        height=400,
        template='plotly_dark',
        yaxis=dict(tickmode='linear'),
        xaxis=dict(side='top')
    )
    
    return fig

def create_penetration_scatter_existing(product_data):
    """Create scatter plot of penetration vs revenue."""
    if product_data.empty:
        return go.Figure()
    
    # Convert pandas Series to lists for Plotly compatibility
    x_data = product_data['customer_penetration_pct'].tolist()
    y_data = product_data['total_revenue_all_time'].tolist()
    size_data = (product_data['total_quantity_all_time'] / 50).tolist()
    color_data = product_data['quantity_growth_pct'].fillna(0).tolist()  # Fill NaN with 0
    text_data = product_data['product_name'].tolist()
    
    fig = go.Figure(data=go.Scatter(
        x=x_data,
        y=y_data,
        mode='markers',
        marker=dict(
            size=size_data,  # Size by quantity (converted to list)
            color=color_data,  # Color by growth (converted to list)
            colorscale='RdYlGn',
            colorbar=dict(title="Growth Rate (%)"),
            sizemode='diameter',
            sizemin=4
        ),
        text=text_data,
        hovertemplate='<b>%{text}</b><br>Penetration: %{x:.1f}%<br>Revenue: ₽%{y:,.0f}<br>Growth: %{marker.color:.1f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title="Product Portfolio Analysis",
        xaxis_title="Customer Penetration (%)",
        yaxis_title="Total Revenue (₽)",
        height=500,
        template='plotly_dark'
    )
    
    return fig
