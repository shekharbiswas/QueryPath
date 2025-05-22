# querypath_app/ui/feedback_display.py

import streamlit as st
import pandas as pd

# Import necessary functions from session_state_manager
from core.session_state_manager import (
    get_last_run_output,
    set_last_run_output,
    update_points,
    mark_challenge_as_solved_in_session,
    is_challenge_already_solved_in_session,
    get_current_challenge_identifier # For debugging or more specific logging if needed
)

# Import from query_validator
from core.query_validator import validate_output


def handle_query_execution(user_query: str, conn, current_challenge_data: dict):
    """
    Executes the user's SQL query, validates the output, updates points,
    and sets flags for feedback display (like balloons).
    """
    current_challenge_id = get_current_challenge_identifier()
    try:
        user_df = pd.read_sql_query(user_query, conn)
        
        is_correct, normalized_user_df, normalized_expected_df = validate_output(
            user_df, current_challenge_data.get("expected_output", [])
        )

        # Store the original user_df for display, and correctness status
        set_last_run_output(output_df=user_df, is_correct=is_correct)

        if is_correct:
            # Check if this challenge was already solved and rewarded in this session
            if not is_challenge_already_solved_in_session():
                update_points(10)  # Award points
                mark_challenge_as_solved_in_session() # Mark as solved for this session
                st.session_state.show_balloons_once = True # Flag to show balloons in display_feedback
            # else:
                # Already solved in this session, no new points, no new balloons.
                # The success message will still show.
                # st.session_state.show_balloons_once = False # Ensure it's false if re-running an already solved one
                # This reset is better handled in app.py before calling this function
                pass
        # else: # Incorrect query
            # st.session_state.show_balloons_once = False # No balloons for incorrect answers
            # This reset is better handled in app.py
            pass


    except Exception as e:
        error_msg = str(e)
        # Enhance error message for common "no such table" error
        if "no such table" in error_msg.lower():
            schema_info = current_challenge_data.get('schema', {})
            table_name_msg = ""
            if isinstance(schema_info, dict) and "table" in schema_info:
                table_name_msg = f"The expected table for this challenge is `{schema_info['table']}`."
            elif isinstance(schema_info, list): # For multiple tables in schema
                tables = [item.get('table', '?') for item in schema_info if isinstance(item, dict)]
                if tables:
                    table_name_msg = f"Expected table(s) for this challenge might include: `{', '.join(tables)}`."
            error_msg += f"\n\n*Hint: Double-check your table and column names against the provided schema. {table_name_msg}*"
        
        # Set last run output with error information
        set_last_run_output(error_message=error_msg, is_correct=False)
        # st.session_state.show_balloons_once = False # No balloons on error
        # This reset is better handled in app.py

def display_feedback(expected_output_data_for_comparison: list):
    """
    Displays feedback to the user based on the last query execution result
    stored in session state. Shows user output, correctness, expected output,
    and balloons if applicable.
    """
    last_run = get_last_run_output() # Fetches output for the CURRENT challenge

    if not last_run:
        # No run information for the current challenge yet.
        # Could be the first time viewing, or navigated from another challenge.
        # st.info("Run your query to see the output and get feedback.") # Optional placeholder
        return

    # 1. Display SQL Error if any
    if last_run.get("error_message"):
        st.error(f"❌ **SQL Error:**\n```\n{last_run['error_message']}\n```")
        # Even with an error, there might be no 'output_df' or 'is_correct'
        # If an error occurred, 'is_correct' should be False (set by handle_query_execution)

    # 2. Display User's Output (if the query ran and produced a DataFrame)
    user_output_df_dict = last_run.get("output_df")
    if user_output_df_dict is not None: # Check if output_df key exists and is not None
        st.subheader("📤 Your Output")
        # Reconstruct DataFrame from the list of dicts stored in session state
        user_df_from_state = pd.DataFrame(user_output_df_dict)
        if user_df_from_state.empty and not last_run.get("error_message"):
             st.write("Your query returned no results.")
        elif not user_df_from_state.empty:
            st.dataframe(user_df_from_state, use_container_width=True)
    elif not last_run.get("error_message"): # Query ran, no error, but output_df is None (empty result from SQL)
        st.subheader("📤 Your Output")
        st.write("Your query returned no results.")


    # 3. Display Correctness Feedback (if the query ran without SQL error)
    is_correct_status = last_run.get("is_correct") # Can be True, False, or None

    if is_correct_status is True:
        st.success("✅ Correct! Your output matches the expected result.")
        if st.session_state.get("show_balloons_once", False):
            st.balloons()
            st.session_state.show_balloons_once = False # Consume the flag: show balloons only once
    
    elif is_correct_status is False:
        # This implies the query ran successfully (no SQL error, or error handled) but the result was wrong.
        # Avoid showing this warning if a SQL error was already displayed.
        if not last_run.get("error_message"):
            st.warning("⚠️ Your output doesn't match the expected result.")
            # Show expected output only if the user's query was incorrect (not if it had a SQL error)
            if expected_output_data_for_comparison:
                st.subheader("🎯 Expected Output")
                st.dataframe(pd.DataFrame(expected_output_data_for_comparison), use_container_width=True)
    
    # If is_correct_status is None, it means the query might not have been evaluated for correctness
    # (e.g., due to an earlier SQL error where set_last_run_output wasn't called with is_correct).
    # The error message display should cover this.