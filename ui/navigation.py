# querypath_app/ui/navigation.py
import streamlit as st
from core.session_state_manager import (
    navigate_to_challenge,
    set_current_user_query,
    is_challenge_already_solved_in_session # Import this
)
from core.data_loader import get_max_challenges_for_day, get_total_days

def display_navigation_buttons(current_query_text_for_saving: str):
    # Save current query text before navigating (if text_area value is passed)
    # This is important if the text_area's on_change isn't used to update session state continuously.
    # Our current display_query_area sets the query in session_state on "Run" click,
    # so this might be redundant if only navigating after a run.
    # However, if user types then immediately clicks Prev/Next without running, this is needed.
    # Let's assume current_query_text_for_saving is the most up-to-date text.

    # --- Prepare navigation data ---
    day = st.session_state.current_day
    challenge_idx = st.session_state.current_challenge_index
    max_challenges_curr_day = get_max_challenges_for_day(day)
    total_days_available = get_total_days() # Get total number of day files

    can_go_previous = not (day == 1 and challenge_idx == 0)
    current_challenge_solved = is_challenge_already_solved_in_session()

    # Determine if there's a next challenge available
    has_next_challenge_on_day = max_challenges_curr_day > 0 and challenge_idx < max_challenges_curr_day - 1
    has_next_day = day < total_days_available
    can_go_next = has_next_challenge_on_day or has_next_day

    # --- Layout for buttons ---
    # We want "Previous" on the left, "Next" (conditional) on the right.
    # The "Run Query" button is now handled in ui/query_input.py.
    # This function is now *only* for Prev/Next navigation.

    nav_cols = st.columns([1, 1]) # Two columns for Prev and Next

    with nav_cols[0]: # Previous Button
        if can_go_previous:
            if st.button("⬅️ Previous Challenge", use_container_width=True, key="prev_challenge_button"):
                set_current_user_query(current_query_text_for_saving) # Save before nav
                if challenge_idx > 0:
                    navigate_to_challenge(day, challenge_idx - 1)
                elif day > 1: # Go to last challenge of previous day
                    prev_day = day - 1
                    max_challenges_prev_day = get_max_challenges_for_day(prev_day)
                    navigate_to_challenge(prev_day, max(0, max_challenges_prev_day - 1))
        else:
            st.button("⬅️ Previous Challenge", use_container_width=True, disabled=True, key="prev_challenge_button_disabled")


    with nav_cols[1]: # Next Button (Conditional)
        if current_challenge_solved and can_go_next:
            if st.button("Next Challenge ➡️", type="primary", use_container_width=True, key="next_challenge_button"):
                set_current_user_query(current_query_text_for_saving) # Save before nav
                if has_next_challenge_on_day:
                    navigate_to_challenge(day, challenge_idx + 1)
                elif has_next_day: # Go to first challenge of next day
                    navigate_to_challenge(day + 1, 0)
        elif not current_challenge_solved and can_go_next:
            # Show a disabled "Next Challenge" button or a message
            st.button("Next Challenge ➡️", use_container_width=True, disabled=True, help="Solve the current challenge to proceed.", key="next_challenge_button_disabled")
            # Or, alternatively, don't show it at all:
            # pass
        elif current_challenge_solved and not can_go_next:
            st.success("🎉 You've completed all available challenges!")
        # If not solved and no next challenge, the disabled button above handles it, or show nothing.