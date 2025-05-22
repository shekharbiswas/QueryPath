import streamlit as st
import sqlite3

DB_PATH = "data/challenges.db"

@st.cache_resource # Caches the connection object itself
def get_connection():
    # check_same_thread=False is important for Streamlit with SQLite
    return sqlite3.connect(DB_PATH, check_same_thread=False)