# querypath_app/app.py
import streamlit as st
import pandas as pd

# Core imports (ensure all are present)
from core.session_state_manager import (
    initialize_session_state,
    get_current_user_query,
    set_current_user_query,
    update_points,
    get_last_run_output,
    set_last_run_output,
    clear_last_run_output_for_current_challenge,
    navigate_to_challenge,
    is_challenge_already_solved_in_session
)
from core.data_loader import get_challenge, get_max_challenges_for_day, get_total_days
from core.db_connector import get_connection

# UI imports
from ui.sidebar import display_sidebar
from ui.challenge_display import (
    display_challenge_context,
    display_challenge_prompt_area,
    display_reflection_and_hints
)
from ui.query_input import display_query_area # Handles Run Query button
from ui.navigation import display_navigation_buttons # Handles Prev/Conditional Next
from ui.feedback_display import display_feedback, handle_query_execution


# --- Page Configuration ---
st.set_page_config(page_title="🧠 QueryPath SQL", layout="wide", initial_sidebar_state="expanded")

# --- Initialize Session State ---
initialize_session_state()
if "show_balloons_once" not in st.session_state:
    st.session_state.show_balloons_once = False

# --- Main App UI ---
st.title("🧠 QueryPath – Improve Your SQL")
st.markdown(
    "Welcome to QueryPath! Sharpen your SQL skills with realistic challenges and get instant feedback. "
    "Solve the current challenge to proceed to the next."
)
st.divider()

# --- Sidebar ---
display_sidebar()

# --- Load Current Challenge Data ---
current_day = st.session_state.current_day
current_challenge_idx = st.session_state.current_challenge_index
current_challenge_data = get_challenge(current_day, current_challenge_idx)

if not current_challenge_data:
    st.error(f"🚨 Oops! Could not load challenge data for Day {current_day}, Challenge {current_challenge_idx + 1}.")
    st.warning("This might be due to a missing or corrupted challenge file. Please check your `challenges` folder.")
    if st.button("Go to First Challenge (Day 1, Challenge 1)"):
        navigate_to_challenge(1, 0)
    st.stop()

# --- Main Two-Column Layout ---
col_challenge_context, col_solution_area = st.columns(2)

with col_challenge_context:
    st.header("Challenge Details")
    display_challenge_context(current_challenge_data)

with col_solution_area:
    st.header("Solve the Challenge")

    # 1. Display the Challenge Prompt and Starter Code
    display_challenge_prompt_area(current_challenge_data)
    st.markdown("---")

    # 2. Display the Query Input Area (text box) AND "Run Query" button
    starter_query = current_challenge_data.get("starter_code", "-- Write your SQL query here")
    initial_query_text = get_current_user_query(starter_query)
    run_button_clicked, current_query_in_box = display_query_area(initial_query_text) # display_query_area now defines the Run button

    # REORDERING STARTS HERE
    # 3. Handle Query Execution FIRST if "Run Query" was clicked
    if run_button_clicked:
        st.session_state.show_balloons_once = False # Reset balloon flag
        db_conn = get_connection()
        if db_conn:
            handle_query_execution(current_query_in_box, db_conn, current_challenge_data)
            # After execution, the solved state is updated.
            # Now, display_navigation_buttons will see the fresh state.
        else:
            st.error("❌ Critical Error: Could not establish database connection.")

    # 4. Display Navigation Buttons (Previous / Conditional Next)
    # This will now read the potentially updated solved state from handle_query_execution
    display_navigation_buttons(current_query_in_box)
    st.divider() # Placed after navigation, before feedback

    # 5. Display Feedback (after potential execution)
    display_feedback(current_challenge_data.get("expected_output", []))
    # REORDERING ENDS HERE

# --- Reflection and Hints ---
st.divider()
with st.expander("🤔 Reflection & Hints", expanded=False):
    display_reflection_and_hints(
        current_challenge_data,
        st.session_state.current_day,
        st.session_state.current_challenge_index
    )

# --- Debugging (Optional) ---
# (Commented out debug code remains the same)