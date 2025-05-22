# querypath_app/ui/query_input.py
import streamlit as st
from core.session_state_manager import get_current_user_query, set_current_user_query, get_current_challenge_identifier

def display_query_area(default_query=""):
    text_area_key = f"query_area_{get_current_challenge_identifier()}"
    query_val = st.session_state.get(text_area_key, get_current_user_query(default_query))

    user_query = st.text_area(
        "✏️ **Write your SQL query below:**",
        value=query_val,
        height=200,
        key=text_area_key,
        help="Type your SQL query here and click 'Run Query' to check your solution."
    )

    # "Run Query" button: type="primary" for prominence.
    # Remove use_container_width=True to make it smaller (fit content).
    # To center it or give it a specific smaller width, use columns.
    
    # Example: Centering a smaller "Run Query" button
    col1, col_run, col3 = st.columns([1, 1, 1]) # Adjust ratios as needed, e.g., [2,1,2] for more space around
    with col_run:
        run_clicked = st.button(
            "▶️ Run Query",
            type="primary",
            key="run_query_button",
            use_container_width=True # Make it fill its smaller column
        )
    # If you just want it to be its natural size, not full width:
    # run_clicked = st.button("▶️ Run Query", type="primary", key="run_query_button")


    if run_clicked:
        set_current_user_query(user_query)
        return True, user_query

    return False, user_query