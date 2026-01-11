import pandas as pd
import streamlit as st
import plotly.graph_objects as go
import plotly.figure_factory as ff
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
def get_dataset():
    url = "https://github.com/thetnaingtunerp/Plotly_Streamlit/blob/c03c056263caf7c4e42d7ffa2c34e69ce559c9c0/abc/dataset/abc.xlsx?raw=true"
    data = pd.read_excel(url, sheet_name='Main DFR', engine='openpyxl')
    # localdataset = pd.read_excel(abc.xlsx, sheet_name='Main DFR', engine='openpyxl')
    dataset = data.dropna(how='all')
    dataset['Filling Date'] = pd.to_datetime(dataset['Filling Date'], format='%d-%m-%Y')
    dataset['Year'] = dataset['Filling Date'].dt.year
    dataset['status'] = dataset['status'].apply(lambda x: x if x >= 0.5 else 0)
    dataset['inform'] = dataset['Water Level'].apply(lambda x: 1 if x == 'No Inform' else 0)
    return dataset



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




site_info = st.container()
multi_select = st.container()
home = st.container()

no_inform = st.container()

with site_info:
    st.subheader('Fuel Filling Summary')
    a,b,c,d = st.columns(4)
    with a:
        #last filling liter of archor
        fill_liter = get_dataset()[(get_dataset()['Anchor ID'] == anchor_selection) & (get_dataset()['Year'].isin(yselection))]['Filling Liters'].iloc[-1]
        st.metric('Last Filling L', f"{fill_liter:,}", border=True)
    with b:
        #last Nominal of archor
        fill_liter = get_dataset()[(get_dataset()['Anchor ID'] == anchor_selection) & (get_dataset()['Year'].isin(yselection))]['Nominal '].iloc[-1]
        st.metric('Nominal', f"{fill_liter:,}", border=True)
    with c:
        #last Actual of archor
        fill_liter = get_dataset()[(get_dataset()['Anchor ID'] == anchor_selection) & (get_dataset()['Year'].isin(yselection))]['Actual CPH'].iloc[-1]
        st.metric('Actual CPH', f"{fill_liter:,}", border=True)
    with d:
        st.metric('No Inform Cases', f"{get_dataset()[(get_dataset()['Anchor ID'] == anchor_selection) & (get_dataset()['inform'] == 1) & (get_dataset()['Year'].isin(yselection))].shape[0]:,}", border=True)

with multi_select:
    st.subheader('Select Columns to Display')
    columns = st.multiselect('Select Columns', get_dataset().columns.tolist(), default=get_dataset().columns.tolist())

with home:
    st.subheader('Hight CPH Report')
    data = get_dataset()
    filtered_data = data[(data['Anchor ID'] == anchor_selection) & (data['Year'].isin(yselection))]
    status_high = filtered_data[filtered_data['status'] > 0.5]
    st.dataframe(status_high[columns])
    # st.dataframe(status_high[['Anchor ID','Team Leader','Filling Date','Filling Liters', 'Actual CPH', 'DGRH Difference' , 'KWH Difference', 'KWH/HR', 'DGRH/day', 'Nominal ', 'status']])
       

with no_inform:
    col1,col2 = st.columns(2)
    with col1:
        st.subheader('No Inform Cases')
        no_inform_data = data[(data['inform'] == 1) &  (data['Year'].isin(yselection)) & (data['Anchor ID'] == anchor_selection)]
        st.dataframe(no_inform_data[['Team Leader','Filling Date','Anchor ID','Filling Liters']])

    with col2:
        st.subheader('CPH High')
        cph_high = data[(data['status'] > 0.5) &  (data['Year'].isin(yselection)) & (data['Anchor ID'] == anchor_selection)]
        st.dataframe(cph_high[['Filling Date','Anchor ID', 'status']])
    
# with trends:
#     st.subheader('Trends of CPH Status Over')
#     trend_data = data[(data['Anchor ID'] == anchor_selection) & (data['Year'].isin(yselection))]
#     trend_data = trend_data.sort_values(by='Filling Date')
#     fig = go.Figure()
#     fig.add_trace(go.Scatter(x=trend_data['Filling Date'], y=trend_data['status'], mode='lines+markers', name='CPH Status'))
#     fig.update_layout(title='CPH Status Over', xaxis_title='Filling Date', yaxis_title='CPH Status')
#     st.plotly_chart(fig, use_container_width=True)









    
    