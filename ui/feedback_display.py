# querypath_app/ui/feedback_display.py
import streamlit as st
import pandas as pd

# Crucial imports from session_state_manager needed by handle_query_execution and display_feedback
from core.session_state_manager import (
    get_last_run_output,
    set_last_run_output,
    update_points,
    mark_challenge_as_solved_in_session,
    is_challenge_already_solved_in_session,
    get_current_challenge_identifier,
    # user_queries is accessed via st.session_state directly if needed
)
from core.query_validator import validate_output
from core.rag_helper import get_vector_db_hints # For Vector DB only hints

# --- Definition of handle_query_execution ---
# This function processes the query execution and updates the state.
def handle_query_execution(user_query: str, conn, current_challenge_data: dict): # <<<< FUNCTION 1
    """
    Executes the user's SQL query, validates the output, updates points,
    and sets flags for feedback display (like balloons).
    """
    current_challenge_id = get_current_challenge_identifier()
    try:
        user_df = pd.read_sql_query(user_query, conn) # conn is the sqlite3 connection object
        
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


# --- Definition of display_feedback ---
# This function shows the results of the query execution to the user.
def display_feedback(expected_output_data_for_comparison: list, current_challenge_data: dict): # <<<< FUNCTION 2
    """
    Displays feedback to the user based on the last query execution result
    stored in session state. Shows user output, correctness, expected output,
    and hints if applicable.
    """
    last_run = get_last_run_output() # Fetches output for the CURRENT challenge
    challenge_was_already_solved = is_challenge_already_solved_in_session()

    if not last_run: # No run data for the current challenge view
        if not challenge_was_already_solved:
            st.info("📝 Enter your query and click 'Run Query' to see the results and get feedback.")
        return

    sql_error_message = last_run.get("error_message")
    current_challenge_id = get_current_challenge_identifier()
    # Get the query that was actually run for this feedback from session_state
    user_query_that_was_run = st.session_state.user_queries.get(current_challenge_id, "")


    # 1. Display SQL Error if any
    if sql_error_message:
        st.error(f"❌ **SQL Error:**\n```\n{sql_error_message}\n```")

    # 2. Display User's Output DataFrame
    user_output_df_dict = last_run.get("output_df")
    if user_output_df_dict is not None:
        st.subheader("📤 Your Output")
        user_df_from_state = pd.DataFrame(user_output_df_dict)
        if user_df_from_state.empty and not sql_error_message:
             st.write("Your query ran successfully but returned no results.")
        elif not user_df_from_state.empty:
            st.dataframe(user_df_from_state, use_container_width=True)
    elif not sql_error_message: # Query ran, no SQL error, but output_df is None
        st.subheader("📤 Your Output")
        st.write("Your query ran successfully but returned no results (or an unexpected empty output type).")

    # 3. Display Correctness Feedback
    is_correct_status = last_run.get("is_correct")

    if is_correct_status is True:
        st.success("✅ Correct! Your output matches the expected result.")
        if st.session_state.get("show_balloons_once", False):
            st.balloons()
            st.session_state.show_balloons_once = False # Consume the flag
    
    elif is_correct_status is False:
        # This implies the query ran (no fatal SQL error), but the output was incorrect.
        if not sql_error_message: # Only show this warning if a SQL error wasn't the primary message
            st.warning("⚠️ Your output doesn't match the expected result.")
        
        if challenge_was_already_solved: # If they try an incorrect query on an already solved challenge
             st.info("Note: This challenge is marked as solved from a previous correct attempt in this session.")
        
        # Show expected output for comparison if the query was incorrect (and not a SQL error)
        if not sql_error_message and expected_output_data_for_comparison:
            st.subheader("🎯 Expected Output (for comparison)")
            st.dataframe(pd.DataFrame(expected_output_data_for_comparison), use_container_width=True)

        # --- Vector DB Hint Button (only if answer is incorrect) ---
        st.markdown("---") 
        # Make sure the button key is unique and consistent for the current challenge view
        hint_button_key = f"vector_db_hint_button_{current_challenge_id}"
        if st.button("💡 Get a Hint from Knowledge Base", key=hint_button_key):
            if user_query_that_was_run: 
                challenge_prompt_for_embedding = current_challenge_data.get("prompt", "N/A")
                
                # Call the function that only queries the vector DB
                retrieved_hints = get_vector_db_hints( 
                    user_query=user_query_that_was_run,
                    challenge_prompt=challenge_prompt_for_embedding,
                    sql_error=sql_error_message,
                    top_k=2 # Get top 2 hints, for example
                )
                
                if retrieved_hints and any(h.strip() for h in retrieved_hints if "No specific pre-written hint found" not in h and "Error retrieving hints" not in h):
                    st.markdown("💡 **Here are some potentially relevant hints:**")
                    for i, hint_text in enumerate(retrieved_hints):
                        # Only show non-empty hints or actual hints
                        if hint_text.strip() and "No specific pre-written hint found" not in hint_text and "Error retrieving hints" not in hint_text:
                            with st.expander(f"Hint #{i+1}", expanded=(i==0)): # Expand the first valid hint
                                st.markdown(hint_text)
                elif retrieved_hints: # It returned a list, but maybe default messages
                    st.info(retrieved_hints[0]) # Show the default message from get_vector_db_hints
                else: # Should ideally be handled by get_vector_db_hints returning a default message list
                    st.info("No specific hint found in the knowledge base for this situation.")
            else:
                st.warning("Please run a query first to get hints based on your attempt.")