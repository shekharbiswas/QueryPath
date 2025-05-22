# querypath_app/ui/query_input.py
import streamlit as st
from core.session_state_manager import (
    get_current_user_query,
    set_current_user_query,
    get_current_challenge_identifier,
    is_challenge_already_solved_in_session # Crucial import
)

def display_query_area(default_query=""):
    """
    Displays the SQL query input area.
    If the challenge is already solved in the session, the text area and
    run button are disabled.
    """
    text_area_key = f"query_area_{get_current_challenge_identifier()}"
    query_val = st.session_state.get(text_area_key, get_current_user_query(default_query))
    
    challenge_is_solved_in_session = is_challenge_already_solved_in_session()

    # Display the text area for the SQL query
    user_query_text = st.text_area(
        "✏️ **Write your SQL query below:**",
        value=query_val,
        height=200,
        key=text_area_key,
        help="This challenge has been solved correctly. The query area is locked for this session." if challenge_is_solved_in_session else "Type your SQL query here and click 'Run Query' to check your solution.",
        disabled=challenge_is_solved_in_session # Key change: disable text area if solved
    )

    run_button_was_clicked = False # Initialize

    if challenge_is_solved_in_session:
        # If challenge is solved, show a success message and no active "Run Query" button
        st.success("✅ Challenge Solved! You can review your solution or navigate to another challenge.")
        # Optionally, show a disabled button for visual consistency, or nothing.
        # col1, col_btn, col3 = st.columns([1,1,1])
        # with col_btn:
        #     st.button("▶️ Run Query", type="primary", key="run_query_button_disabled_solved", disabled=True, use_container_width=True)
    else:
        # If challenge is not solved, display the active "Run Query" button
        col1, col_run_btn_container, col3 = st.columns([1, 1, 1]) # For centering
        with col_run_btn_container:
            if st.button(
                "▶️ Run Query",
                type="primary",
                key="run_query_button_active", # Unique key for the active button state
                use_container_width=True # Make button fill its column
            ):
                run_button_was_clicked = True

    if run_button_was_clicked: # This will only be true if challenge_is_solved_in_session was False
        set_current_user_query(user_query_text) # Save the query that was just run
        return True, user_query_text # Signal run and return the query text

    # If not clicked or if challenge was already solved, return False and the current query text
    return False, user_query_text