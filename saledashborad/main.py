import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# ----------------------------
# Page Config
# ----------------------------
st.set_page_config(
    page_title="Sale Dashboard",
    layout="wide"
)
def getdataset():
    df = pd.read_csv('https://raw.githubusercontent.com/MyDataset/saledataset/refs/heads/main/Adidas%20US%20Sales%20Datasets.xlsx%20-%20Data%20Sales%20Adidas.csv')
    #EDA remove $ and , from Total Sales column
    df['Total Sales'] = df['Total Sales'].replace({'\$': '', ',': ''}, regex=True).astype(int)
    df['Price per Unit'] = df['Price per Unit'].replace({'\$': '', ',': ''}, regex=True).astype(float)
    df['Operating Profit'] = df['Operating Profit'].replace({'\$': '', ',': ''}, regex=True).astype(int)
    df['Units Sold'] = df['Units Sold'].replace({',': ''}, regex=True).astype(int)
    # start string with 'Men's '
    df['Gender']= df['Product'].apply(lambda x: 'Men\'s ' if 'Men' in x else 'Women\'s ' if 'Women' in x else 'Unisex')
    df['Operating Margin'] = df['Operating Margin'].str.replace('%', '').astype(float)
    df['Invoice Date'] = pd.to_datetime(df['Invoice Date'], format='%m/%d/%Y')
    df['Year'] = df['Invoice Date'].dt.year
    
    return df


st.subheader("sale dashbord")

# ----------------------------
# Sidebar
# ----------------------------
sidebar=st.sidebar.header('menu')
city = st.sidebar.header('city')
row1 = st.container()
row2 = st.container()
row3 = st.container()

with sidebar:
    region_selection = sidebar.selectbox('region', getdataset()['Region'].unique())
with city:
    city_selection = city.selectbox('City', getdataset()['City'].unique())
    
with row1:
    col1,col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Temperature", "30°F", "-9°F", border=True)
    with col2:
        st.metric("Wind", "4 mph", "2 mph", border=True)

    with col3:
        st.metric("Humidity", "77%", "5%", border=True)
    with col4:
        st.metric("Pressure", "30.34 inHg", "-2 inHg", border=True)


with row2:
    st.dataframe(getdataset().head(10))


with row3:
    st.subheader('chart')
    col1, col2 = st.columns(2)
    
    with col1:
        pivot_df = pd.pivot_table(getdataset(), values='Units Sold', index='Year', columns='Gender', aggfunc=np.sum)
        st.bar_chart(pivot_df, stack=False)
    with col2:
        # df_long = pivot_df.melt(id_vars='Year', var_name='Gender',value_name='Units Sold')
        fig = px.bar(pivot_df, barmode='group', text='Gender')
        fig.update_traces(textposition='outside')
        st.plotly_chart(fig, use_container_width=True)

