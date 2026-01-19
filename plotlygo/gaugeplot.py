import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def gauge_plot(value, title="Gauge Plot", min_value=0, max_value=100):
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={'text': title},
        gauge={
            'axis': {'range': [min_value, max_value]},
            'bar': {'color': "darkblue"},
            'steps': [
                {'range': [min_value, (min_value + max_value) / 2], 'color': "lightgray"},
                {'range': [(min_value + max_value) / 2, max_value], 'color': "gray"}
            ],
        }
    ))

    st.plotly_chart(fig)
    
    
# example 2 
def gauge_plot2(value, title="Gauge Plot 2", min_value=0, max_value=100):
    fig = make_subplots(rows=1, cols=1, specs=[[{'type': 'indicator'}]])
    
    fig.add_trace(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        delta={'reference': (min_value + max_value) / 2},
        title={'text': title},
        gauge={
            'axis': {'range': [min_value, max_value]},
            'bar': {'color': "darkgreen"},
            'steps': [
                {'range': [min_value, (min_value + max_value) / 2], 'color': "lightyellow"},
                {'range': [(min_value + max_value) / 2, max_value], 'color': "yellow"}
            ],
        }
    ), row=1, col=1)

    st.plotly_chart(fig)
    
# Example usage
gauge_plot(70, title="Sample Gauge Plot", min_value=0, max_value=100)
gauge_plot2(40, title="Sample Gauge Plot 2", min_value=0, max_value=100)



