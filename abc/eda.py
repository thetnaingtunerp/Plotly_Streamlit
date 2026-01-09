import pandas as pd
import streamlit as st
# import plotly.graph_objects as go
# import plotly.figure_factory as ff
import os
import warnings

warnings.filterwarnings("ignore")

page_config = {
    "page_title": "ABC",
    "page_icon": "📊",
    "layout": "wide",
}

st.set_page_config(**page_config)


        


@st.cache_data
def get_dataset(name='abc.xlsx'):
    data = pd.read_excel(name, sheet_name='Main DFR', engine='openpyxl')
    # localdataset = pd.read_excel(abc.xlsx, sheet_name='Main DFR', engine='openpyxl')
    dataset = data.dropna(how='all')
    dataset['Filling Date'] = pd.to_datetime(dataset['Filling Date'], format='%d-%m-%Y')
    dataset['Year'] = dataset['Filling Date'].dt.year
    dataset['status'] = dataset['status'].apply(lambda x: x if x >= 0.5 else 0)
    dataset['inform'] = dataset['Water Level'].apply(lambda x: 1 if x == 'No Inform' else 0)
    return dataset


# Create form
# with st.form(key="data_form"):
#     name = st.text_input("Copy and Pate Data URL")
#     submit_btn = st.form_submit_button("Submit")

# if submit_btn:
#     if not name:
#         st.error("not fields are filled!")
#     else:
#         get_dataset(name)


#Sidebar

year_selection = st.sidebar.header('Filters')
sidebar = st.sidebar.header('Dataset Overview')

with sidebar:
    anchor_selection = sidebar.selectbox('Anchor ID', get_dataset()['Anchor ID'].unique())

# Year Selection to Sidebar
with year_selection:
    # year_selection = st.sidebar.slider(get_dataset()['Year'].min(), get_dataset()['Year'].max(), get_dataset()['Year'].min(), key='year_slider')
    yselection = st.sidebar.slider('Year', int(get_dataset()['Year'].min()), int(get_dataset()['Year'].max()), (int(get_dataset()['Year'].min()), int(get_dataset()['Year'].max())))


# st.title('Fueling Data Report')


no_inform = st.container()
home = st.container()
trends = st.container()


with home:
    st.subheader('Hight CPH Report')
    data = get_dataset()
    filtered_data = data[(data['Anchor ID'] == anchor_selection) & (data['Year'].isin(yselection))]
    status_high = filtered_data[filtered_data['status'] > 0.5]
    st.dataframe(status_high[['Anchor ID','Team Leader','Filling Date','Filling Liters', 'status']])
       


with no_inform:
    col1,col2, col3 = st.columns(3)
    with col1:
        st.subheader('No Inform Cases')
        no_inform_data = data[(data['inform'] == 1) &  (data['Year'].isin(yselection))]
        st.dataframe(no_inform_data[['Team Leader','Filling Date','Anchor ID','Filling Liters']])

    with col2:
        st.subheader('CPH High')
        cph_high = data[(data['status'] > 0.5) &  (data['Year'].isin(yselection))]
        st.dataframe(cph_high[['Team Leader','Filling Date','Anchor ID', 'status']])
    with col3:
        st.subheader('No Inform CPH High')
        no_inform_cph_high = data[(data['inform'] == 1) & (data['status'] > 0) &  (data['Year'].isin(yselection))]
        st.dataframe(no_inform_cph_high[['Team Leader','Filling Date','Anchor ID']])

with trends:
    st.subheader('Trends Over Time')
    trend_data = data[(data['Anchor ID'] == anchor_selection) & (data['Year'].isin(yselection))]
    trend_data = trend_data.sort_values(by='Filling Date')
    # fig = go.Figure()
    # fig.add_trace(go.Scatter(x=trend_data['Filling Date'], y=trend_data['status'], mode='lines+markers', name='CPH Status'))
    # fig.update_layout(title='CPH Status Over Time', xaxis_title='Filling Date', yaxis_title='CPH Status')
    # st.plotly_chart(fig, use_container_width=True)
    
    