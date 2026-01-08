import streamlit as st
import pandas as pd
import plotly.express as px

iris_df = px.data.iris()
st.title("Iris Dataset Dashboard")
st.write("This dashboard visualizes the Iris dataset.")
st.dataframe(iris_df)

fig = px.scatter(iris_df, x='sepal_width', y='sepal_length', color='species',
                 title='Sepal Width vs Sepal Length')
st.plotly_chart(fig)

# run with: streamlit run irisdata/dashborad1.py
# add sidebar filter for species
species = st.sidebar.multiselect("Select Species", options=iris_df['species'].unique(), default=iris_df['species'].unique())
filtered_df = iris_df[iris_df['species'].isin(species)]
st.dataframe(filtered_df)
fig_filtered = px.scatter(filtered_df, x='sepal_width', y='sepal_length', color='species',
                          title='Filtered Sepal Width vs Sepal Length')
st.plotly_chart(fig_filtered)
