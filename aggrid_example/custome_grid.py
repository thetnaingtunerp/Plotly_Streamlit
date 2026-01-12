import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode

st.title("Advanced Ag-Grid Configuration")

# Load sample data
df = pd.read_csv('https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv')

# Configure grid options
gb = GridOptionsBuilder.from_dataframe(df)

# Enable features
gb.configure_pagination(paginationAutoPageSize=True)  # Auto pagination
gb.configure_side_bar()  # Side filters panel
gb.configure_selection('multiple', use_checkbox=True)  # Multi-row selection
gb.configure_default_column(
    editable=False,  # Make cells non-editable
    filterable=True,
    sortable=True,
    resizable=True
)

# Column-specific configurations
gb.configure_column("Age", type=["numericColumn", "numberColumnFilter"])
gb.configure_column("Fare", type=["numericColumn", "currencyColumnFilter"])
gb.configure_column("Name", headerName="Passenger Name", width=200)

grid_options = gb.build()

# Display grid
grid_response = AgGrid(
    df,
    gridOptions=grid_options,
    height=500,
    width='100%',
    update_mode=GridUpdateMode.SELECTION_CHANGED,
    theme='streamlit',  # Try 'alpine', 'balham', 'material'
    fit_columns_on_grid_load=False
)

# Display selected rows
if grid_response['selected_rows']:
    selected_df = pd.DataFrame(grid_response['selected_rows'])
    st.subheader("Selected Rows")
    st.dataframe(selected_df)