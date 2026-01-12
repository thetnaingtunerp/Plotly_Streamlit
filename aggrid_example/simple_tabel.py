import streamlit as st
import pandas as pd
from st_aggrid import AgGrid

# Create sample data
data = {
    'Name': ['John', 'Alice', 'Bob', 'Emily'],
    'Age': [25, 30, 35, 28],
    'Salary': [50000, 60000, 55000, 65000],
    'Department': ['IT', 'HR', 'IT', 'Finance']
}
df = pd.DataFrame(data)

st.title("Ag-Grid Basic Example")
AgGrid(df)