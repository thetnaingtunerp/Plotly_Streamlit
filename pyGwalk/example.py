import streamlit as st
import pandas as pd
import pygwalker as pyg

# Load sample dataset
df = pd.DataFrame({
    'A': range(1, 11),
    'B': [x ** 2 for x in range(1, 11)],
    'C': ['Category1', 'Category2'] * 5
})

# Title for the Streamlit app
st.title("PyGWalker with Streamlit - Basic Example")

# Display the dataset
st.write("### Sample Data")
st.dataframe(df)

pyg.walk(df)
