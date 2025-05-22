# querypath_app/ui/sidebar.py
import streamlit as st
from core.data_loader import get_max_challenges_for_day # Import this

def display_sidebar():
    st.sidebar.header("🗓️ Your Progress")
    st.sidebar.markdown(f"**Day**: {st.session_state.current_day}")

    # Display current challenge out of total for the day
    current_challenge_num_display = st.session_state.current_challenge_index + 1 # 1-indexed for display
    total_challenges_for_day = get_max_challenges_for_day(st.session_state.current_day)

    if total_challenges_for_day > 0:
        st.sidebar.markdown(
            f"**Challenge**: {current_challenge_num_display} of {total_challenges_for_day}"
        )
    else:
        # Fallback if total_challenges_for_day is 0 (e.g., day file missing or empty)
        st.sidebar.markdown(f"**Challenge**: {current_challenge_num_display}")

    st.sidebar.markdown(f"🏆 **Points**: {st.session_state.points}")
    st.sidebar.markdown("---")
    st.sidebar.info(
        "Solve challenges to earn points and unlock the next one. "
        "Use the navigation buttons below your query to move between solved challenges."
    )
    st.sidebar.markdown("---")
    # Optional: Add a reset progress button or other global controls here
    # if st.sidebar.button("Reset All Progress (Debug)"):
    #     # This would require a function in session_state_manager to clear relevant states
    #     # e.g., st.session_state.user_queries = {}, st.session_state.points = 0, etc.
    #     # And then st.rerun()
    #     st.warning("Reset functionality not fully implemented.")