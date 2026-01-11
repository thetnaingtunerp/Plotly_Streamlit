import streamlit as st
import pandas as pd
import sqlite3



st.set_page_config(
    page_title="Create Account",
    page_icon="🆕",
    layout="wide",
    initial_sidebar_state="auto",)


st.sidebar.title("Create Your Account")
st.title("Create Your Account")

conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (   id INTEGER PRIMARY KEY AUTOINCREMENT,
                 username TEXT, 
                 password TEXT)''')
conn.commit()
conn.close()