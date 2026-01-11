import streamlit as st
import pandas as pd


pages = {
    "Your account": [
        st.Page("create.py", title="Create your account"),
        st.Page("manage.py", title="Manage your account"),
    ],
    "Resources": [
        st.Page("learn.py", title="Learn about us"),
        st.Page("trial.py", title="Try it out"),
    ],
}

pg = st.navigation(pages, position="top")
pg.run()

