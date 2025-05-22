import streamlit as st
import json
import os

CHALLENGES_DIR = "challenges"

@st.cache_data # Cache the loaded JSON data
def load_challenge_file_data(day: int):
    # Check session state cache first
    if day in st.session_state.challenges_data_cache:
        return st.session_state.challenges_data_cache[day]

    filepath = os.path.join(CHALLENGES_DIR, f"day{day}.json")
    try:
        with open(filepath, encoding="utf-8") as f:
            data = json.load(f)
            st.session_state.challenges_data_cache[day] = data # Store in session state cache
            return data
    except FileNotFoundError:
        st.error(f"Challenge file for Day {day} not found at {filepath}")
        return None
    except json.JSONDecodeError:
        st.error(f"Error decoding JSON from {filepath}")
        return None

def get_challenge(day: int, challenge_index: int):
    day_data = load_challenge_file_data(day)
    if day_data and "challenges" in day_data and 0 <= challenge_index < len(day_data["challenges"]):
        # Store max challenges for this day if not already stored
        if day not in st.session_state.max_challenges_per_day:
             st.session_state.max_challenges_per_day[day] = len(day_data["challenges"])
        return day_data["challenges"][challenge_index]
    return None

def get_max_challenges_for_day(day: int):
    if day in st.session_state.max_challenges_per_day:
        return st.session_state.max_challenges_per_day[day]
    # If not in session state, load it (get_challenge will populate it)
    load_challenge_file_data(day)
    return st.session_state.max_challenges_per_day.get(day, 0)

def get_total_days():
    # Dynamically find total number of day files
    # This could be slow if many files, consider hardcoding or a manifest file
    day_files = [f for f in os.listdir(CHALLENGES_DIR) if f.startswith("day") and f.endswith(".json")]
    return len(day_files) # A simple count, assumes day1.json, day2.json, etc.