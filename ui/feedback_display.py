# querypath_app/ui/feedback_display.py

import streamlit as st
import pandas as pd

from core.session_state_manager import (
    get_last_run_output,
    set_last_run_output,
    update_points,
    mark_challenge_as_solved_in_session,
    is_challenge_already_solved_in_session, # Import this
    get_current_challenge_identifier
)
from core.query_validator import validate_output


def handle_query_execution(user_query: str, conn, current_challenge_data: dict):
    current_challenge_id = get_current_challenge_identifier() # Good for logging/debugging
    try:
        user_df = pd.read_sql_query(user_query, conn)
        is_correct, normalized_user_df, normalized_expected_df = validate_output(
            user_df, current_challenge_data.get("expected_output", [])
        )
        set_last_run_output(output_df=user_df, is_correct=is_correct)

        if is_correct:
            if not is_challenge_already_solved_in_session():
                update_points(10)
                mark_challenge_as_solved_in_session()
                st.session_state.show_balloons_once = True
    except Exception as e:
        error_msg = str(e)
        if "no such table" in error_msg.lower():
            schema_info = current_challenge_data.get('schema', {})
            table_name_msg = ""
            if isinstance(schema_info, dict) and "table" in schema_info:
                table_name_msg = f"The expected table for this challenge is `{schema_info['table']}`."
            elif isinstance(schema_info, list):
                tables = [item.get('table', '?') for item in schema_info if isinstance(item, dict)]
                if tables:
                    table_name_msg = f"Expected table(s) for this challenge might include: `{', '.join(tables)}`."
            error_msg += f"\n\n*Hint: Double-check your table and column names. {table_name_msg}*"
        set_last_run_output(error_message=error_msg, is_correct=False)

# querypath_app/ui/feedback_display.py
# ... (imports and handle_query_execution remain largely the same) ...

def display_feedback(expected_output_data_for_comparison: list):
    last_run = get_last_run_output()
    challenge_was_already_solved = is_challenge_already_solved_in_session()

    if not last_run: # No run data for the current challenge view
        # If it was solved, query_input shows the "solved" message.
        # If not solved yet, and no run, this is the initial state.
        if not challenge_was_already_solved:
            st.info("📝 Enter your query and click 'Run Query' to see the results and get feedback.")
        return

    # If there is a last_run record for this challenge:

    # 1. Display SQL Error if any (This means the query didn't produce a standard output)
    if last_run.get("error_message"):
        st.error(f"❌ **SQL Error:**\n```\n{last_run['error_message']}\n```")
        # If there's a SQL error, we typically don't have a 'user_output_df_dict'
        # or 'is_correct_status' from the normal validation path.
        # 'is_correct' would have been set to False in handle_query_execution's except block.

    # 2. Display User's Output DataFrame (CRITICAL PART)
    # This block executes REGARDLESS of whether the query was correct or incorrect,
    # as long as the query ran without a fatal SQL execution error that prevented DataFrame creation.
    user_output_df_dict = last_run.get("output_df")
    if user_output_df_dict is not None: # Query ran and produced some result (even if empty)
        st.subheader("📤 Your Output")
        user_df_from_state = pd.DataFrame(user_output_df_dict)
        if user_df_from_state.empty and not last_run.get("error_message"): # Check for SQL error again
             st.write("Your query ran successfully but returned no results.")
        elif not user_df_from_state.empty:
            st.dataframe(user_df_from_state, use_container_width=True)
    elif not last_run.get("error_message"):
        # Query ran, no SQL error, but output_df is None (e.g., if pd.read_sql_query somehow returned None directly)
        # This is less common; usually, an empty result is an empty DataFrame.
        st.subheader("📤 Your Output")
        st.write("Your query ran successfully but returned no results (or an unexpected empty output type).")


    # 3. Display Correctness Feedback
    is_correct_status = last_run.get("is_correct")

    if is_correct_status is True:
        st.success("✅ Correct! Your output matches the expected result.")
        if st.session_state.get("show_balloons_once", False):
            st.balloons()
            st.session_state.show_balloons_once = False
    
    elif is_correct_status is False:
        # This means the query ran (no fatal SQL error), but the output was incorrect.
        # The user's output (from step 2) should have already been displayed above.
        if not last_run.get("error_message"): # Only show this warning if a SQL error wasn't the primary message
            st.warning("⚠️ Your output doesn't match the expected result.")
            if challenge_was_already_solved: # If they try an incorrect query on an already solved challenge
                 st.info("Note: This challenge is marked as solved from a previous correct attempt in this session.")
            
            # Show expected output for comparison
            if expected_output_data_for_comparison:
                st.subheader("🎯 Expected Output (for comparison)")
                st.dataframe(pd.DataFrame(expected_output_data_for_comparison), use_container_width=True)
    
    # If is_correct_status is None (should ideally not happen if handle_query_execution always sets it),
    # it implies an issue in the execution/feedback flow. The SQL error or absence of output would be the primary indicators.