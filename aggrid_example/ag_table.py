import streamlit as st
import pandas as pd
import numpy as np
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode

st.set_page_config(layout="wide")
st.title("📊 Enterprise Data Grid Dashboard")

# Generate sample sales data
@st.cache_data
def generate_data():
    np.random.seed(42)
    dates = pd.date_range('2024-01-01', periods=200)
    data = pd.DataFrame({
        'OrderID': [f'ORD{1000+i}' for i in range(200)],
        'Date': dates,
        'Customer': np.random.choice(['Customer A', 'Customer B', 'Customer C', 'Customer D'], 200),
        'Product': np.random.choice(['Laptop', 'Phone', 'Tablet', 'Monitor', 'Keyboard'], 200),
        'Region': np.random.choice(['North', 'South', 'East', 'West'], 200),
        'Sales': np.random.randint(100, 10000, 200),
        'Quantity': np.random.randint(1, 50, 200),
        'Profit': np.random.randint(-500, 2000, 200),
        'Status': np.random.choice(['Delivered', 'Pending', 'Cancelled', 'Shipped'], 200)
    })
    data['Revenue'] = data['Sales'] * data['Quantity']
    return data

df = generate_data()

# Sidebar filters
st.sidebar.header("🔍 Filters")
regions = st.sidebar.multiselect("Select Regions", df['Region'].unique(), default=df['Region'].unique())
statuses = st.sidebar.multiselect("Select Status", df['Status'].unique(), default=df['Status'].unique())

# Filter data
filtered_df = df[(df['Region'].isin(regions)) & (df['Status'].isin(statuses))]

# Build grid options
gb = GridOptionsBuilder.from_dataframe(filtered_df)

# Configure default columns
gb.configure_default_column(
    min_column_width=10,
    resizable=True,
    filterable=True,
    sortable=True,
    editable=False,
    groupable=True
)

# Configure pagination
gb.configure_pagination(
    paginationPageSize=10,
    paginationAutoPageSize=False
)

# Configure selection
gb.configure_selection(
    selection_mode='multiple',
    use_checkbox=False,
    rowMultiSelectWithClick=True,
    suppressRowDeselection=False
)

# Configure specific columns
gb.configure_column("Date", type=["dateColumnFilter", "customDateTimeFormat"], 
                   custom_format_string='yyyy-MM-dd', width=120)
gb.configure_column("Sales", type=["numericColumn", "numberColumnFilter"], 
                   valueFormatter="'$' + value.toLocaleString()")
gb.configure_column("Revenue", type=["numericColumn", "numberColumnFilter"], 
                   valueFormatter="'$' + value.toLocaleString()")
gb.configure_column("Profit", 
                   cellStyle=JsCode("""
                       function(params) {
                           if (params.value < 0) {
                               return {color: 'red', fontWeight: 'bold'};
                           } else if (params.value > 1000) {
                               return {color: 'green', fontWeight: 'bold'};
                           }
                           return null;
                       }
                   """))
gb.configure_column("Status",
                   cellStyle=JsCode("""
                       function(params) {
                           if (params.value === 'Delivered') {
                               return {backgroundColor: '#d4edda'};
                           } else if (params.value === 'Cancelled') {
                               return {backgroundColor: '#f8d7da'};
                           } else if (params.value === 'Pending') {
                               return {backgroundColor: '#fff3cd'};
                           }
                           return null;
                       }
                   """))

# Enable grouping and aggregation
gb.configure_grid_options(
    domLayout='normal',
    enableRangeSelection=True,
    enableCharts=True,
    enableCellChangeFlash=True
)

# Configure side panel
gb.configure_side_bar(
    filters_panel=True,
    columns_panel=True,
    defaultToolPanel="filters"
)

grid_options = gb.build()

# Main content
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Orders", len(filtered_df))
with col2:
    st.metric("Total Revenue", f"${filtered_df['Revenue'].sum():,.0f}")
with col3:
    st.metric("Average Profit", f"${filtered_df['Profit'].mean():,.0f}")
with col4:
    st.metric("Unique Customers", filtered_df['Customer'].nunique())

# Display the grid
st.subheader("📋 Interactive Data Grid")
grid_response = AgGrid(
    filtered_df,
    gridOptions=grid_options,
    height=600,
    width='100%',
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    update_mode=GridUpdateMode.MODEL_CHANGED,
    allow_unsafe_jscode=True,
    theme='alpine',  # Modern theme
    reload_data=False,
    custom_css={
        ".ag-header-cell-label": {"font-size": "14px", "font-weight": "bold"},
        ".ag-row": {"font-size": "13px"},
        ".ag-header": {"background-color": "#f8f9fa"}
    }
)

# Display selected data
if grid_response['selected_rows']:
    st.subheader("Selected Orders")
    selected_df = pd.DataFrame(grid_response['selected_rows'])
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.dataframe(selected_df, use_container_width=True)
    
    with col2:
        st.subheader("Selection Summary")
        st.metric("Total Selected", len(selected_df))
        st.metric("Total Revenue", f"${selected_df['Revenue'].sum():,.0f}")
        
        # Pie chart of selected statuses
        if not selected_df.empty:
            status_counts = selected_df['Status'].value_counts()
            st.bar_chart(status_counts)

# Export functionality
st.sidebar.header("📤 Export")
if st.sidebar.button("Export Selected to CSV") and grid_response['selected_rows']:
    selected_df.to_csv('selected_orders.csv', index=False)
    st.sidebar.success("File exported successfully!")
    
if st.sidebar.button("Export All to CSV"):
    filtered_df.to_csv('all_orders.csv', index=False)
    st.sidebar.success("All data exported!")