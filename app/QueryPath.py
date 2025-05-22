import streamlit as st
import sqlite3
import pandas as pd
import json
import unicodedata

# --- Session State Initialization ---
if "day" not in st.session_state:
    st.session_state.day = 1
if "challenge" not in st.session_state:
    st.session_state.challenge = 0
if "points" not in st.session_state:
    st.session_state.points = 0
if "last_output" not in st.session_state:
    st.session_state.last_output = None
if "last_correct" not in st.session_state:
    st.session_state.last_correct = None

# --- Load Challenge JSON ---
def load_challenge(day: int, challenge_index: int = 0):
    with open(f"challenges/day{day}.json", encoding="utf-8") as f:
        data = json.load(f)
    return data["challenges"][challenge_index]

# --- Connect to SQLite Database ---
@st.cache_resource
def get_connection():
    return sqlite3.connect("challenges.db", check_same_thread=False)

# --- Normalize DataFrame for Comparison ---
def normalize_df(df):
    def clean(val):
        if pd.isnull(val): return val
        val = str(val).strip().lower()
        return unicodedata.normalize("NFC", val)

    df = df.copy()
    df.columns = [col.strip().lower() for col in df.columns]
    return df.applymap(clean).sort_values(by=df.columns.tolist()).reset_index(drop=True)

# --- UI Header ---
st.title("🧠 QueryPath – Improve SQL")
st.markdown("Practice your SQL with realistic challenges and get instant feedback.")

# --- Sidebar Progress ---
st.sidebar.markdown(f"📅 **Day**: {st.session_state.day}")
st.sidebar.markdown(f"🎯 **Challenge**: {st.session_state.challenge}")
st.sidebar.markdown(f"🏆 **Points**: {st.session_state.points}")

# --- Load Current Challenge ---
day = st.session_state.day
challenge_index = st.session_state.challenge
challenge = load_challenge(day, challenge_index)

# --- Display Challenge Info ---
st.subheader(f"📘 {challenge['title']}")
st.write(f"**Scenario:** {challenge['scenario']}")

st.subheader("📊 Table Schema")
for col, dtype in challenge["schema"]["columns"].items():
    st.code(f"{col}: {dtype}")

st.subheader("🧪 Challenge Prompt")
st.markdown(challenge["prompt"])
st.code(challenge["starter_code"], language="sql")

user_query = st.text_area("Write your SQL query below:")

# --- Navigation Buttons ---
col1, col2, col3 = st.columns([1, 2, 1])

with col1:
    if st.button("⬅️ Previous"):
        if st.session_state.challenge > 0:
            st.session_state.challenge -= 1
        elif st.session_state.day > 1:
            st.session_state.day -= 1
            st.session_state.challenge = 4
        st.session_state.last_output = None
        st.rerun()

with col2:
    run_clicked = st.button("▶️ Run Query")

with col3:
    if st.button("➡️ Next"):
        st.session_state.challenge += 1
        if st.session_state.challenge > 4:
            st.session_state.challenge = 0
            st.session_state.day += 1
        st.session_state.last_output = None
        st.rerun()

# --- Query Execution ---
if run_clicked:
    conn = get_connection()
    try:
        user_df = pd.read_sql_query(user_query, conn)
        expected_df = pd.DataFrame(challenge["expected_output"])

        st.session_state.last_output = user_df.to_dict()

        if normalize_df(user_df).equals(normalize_df(expected_df)):
            st.session_state.points += 10
            st.session_state.last_correct = True
            st.success("✅ Correct! Your output matches the expected result.")
            st.balloons()
        else:
            st.session_state.last_correct = False
            st.warning("⚠️ Your output doesn't match the expected result.")
            st.subheader("✅ Expected Output")
            st.dataframe(expected_df)

    except Exception as e:
        st.session_state.last_output = None
        st.session_state.last_correct = False
        st.error(f"❌ Error in your SQL: {e}")

# --- Show Last Output ---
if st.session_state.last_output:
    st.subheader("📤 Your Output")
    user_df = pd.DataFrame(st.session_state.last_output)
    st.dataframe(user_df)

    # Offer "Next Challenge" button only after correct answer
    if st.session_state.last_correct:
        if st.button("✅ Next Challenge"):
            st.session_state.challenge += 1
            if st.session_state.challenge > 4:
                st.session_state.challenge = 0
                st.session_state.day += 1
            st.session_state.last_output = None
            st.session_state.last_correct = None
            st.rerun()

# --- Reflection Prompts ---
st.subheader("💬 Reflection Prompts")
for r in challenge["reflection"]:
    st.markdown(f"- {r}")

# --- Hints ---
if "hints" in challenge:
    with st.expander("💡 Need a Hint?"):
        for hint in challenge["hints"]:
            st.markdown(f"- {hint}")
