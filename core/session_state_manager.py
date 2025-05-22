import streamlit as st

DEFAULT_DAY = 1
DEFAULT_CHALLENGE_INDEX = 0

def get_challenge_id(day, challenge_index):
    return f"day{day}_chal{challenge_index}"

def initialize_session_state():
    if "current_day" not in st.session_state:
        st.session_state.current_day = DEFAULT_DAY
    if "current_challenge_index" not in st.session_state:
        st.session_state.current_challenge_index = DEFAULT_CHALLENGE_INDEX
    if "points" not in st.session_state:
        st.session_state.points = 0
    if "user_queries" not in st.session_state:
        st.session_state.user_queries = {}
    if "last_run_outputs" not in st.session_state:
        st.session_state.last_run_outputs = {}
    if "challenges_data_cache" not in st.session_state:
        st.session_state.challenges_data_cache = {}
    if "max_challenges_per_day" not in st.session_state:
        st.session_state.max_challenges_per_day = {}
    # NEW: Track challenges solved in the current session to prevent re-rewarding
    if "solved_challenges_in_session" not in st.session_state:
        st.session_state.solved_challenges_in_session = set()


def get_current_challenge_identifier():
    return get_challenge_id(st.session_state.current_day, st.session_state.current_challenge_index)

def get_current_user_query(starter_code=""):
    challenge_id = get_current_challenge_identifier()
    return st.session_state.user_queries.get(challenge_id, starter_code)

def set_current_user_query(query_text):
    challenge_id = get_current_challenge_identifier()
    st.session_state.user_queries[challenge_id] = query_text

def get_last_run_output():
    challenge_id = get_current_challenge_identifier()
    return st.session_state.last_run_outputs.get(challenge_id)

def set_last_run_output(output_df=None, is_correct=None, error_message=None):
    challenge_id = get_current_challenge_identifier()
    st.session_state.last_run_outputs[challenge_id] = {
        "output_df": output_df.to_dict('records') if output_df is not None else None,
        "is_correct": is_correct,
        "error_message": error_message
    }

def clear_last_run_output_for_current_challenge(): # Not currently used, but could be
    challenge_id = get_current_challenge_identifier()
    if challenge_id in st.session_state.last_run_outputs:
        del st.session_state.last_run_outputs[challenge_id]

def update_points(earned_points): # This function seems fine
    st.session_state.points += earned_points

def mark_challenge_as_solved_in_session():
    challenge_id = get_current_challenge_identifier()
    st.session_state.solved_challenges_in_session.add(challenge_id)

def is_challenge_already_solved_in_session():
    challenge_id = get_current_challenge_identifier()
    return challenge_id in st.session_state.solved_challenges_in_session

def navigate_to_challenge(day, challenge_index):
    st.session_state.current_day = day
    st.session_state.current_challenge_index = challenge_index
    # When navigating, we don't necessarily clear last_run_output here,
    # as the user might want to see their previous attempt on that challenge.
    # The logic to re-show balloons/points will check `solved_challenges_in_session`.
    st.rerun()