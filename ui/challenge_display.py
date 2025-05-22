import streamlit as st

# This function now focuses on title, scenario, and schema
def display_challenge_context(challenge_data):
    if not challenge_data:
        st.error("No challenge data to display.")
        return # Or return False to indicate failure

    st.subheader(f"📘 {challenge_data.get('title', 'N/A')}")
    st.write(f"**Scenario:** {challenge_data.get('scenario', 'N/A')}")

    st.subheader("📊 Table Schema")
    schema_data = challenge_data.get("schema", {}) # Renamed for clarity

    # Handle both single table schema (dict) and multiple table schema (list of dicts)
    if isinstance(schema_data, dict) and "columns" in schema_data: # Single table
        if "table" in schema_data:
             st.markdown(f"**Table:** `{schema_data['table']}`")
        for col, dtype in schema_data.get("columns", {}).items():
            st.code(f"{col}: {dtype}", language="plaintext")
    elif isinstance(schema_data, list): # List of tables
        for table_schema_item in schema_data:
            if isinstance(table_schema_item, dict) and "table" in table_schema_item and "columns" in table_schema_item:
                st.markdown(f"**Table:** `{table_schema_item['table']}`")
                for col, dtype in table_schema_item.get("columns", {}).items():
                    st.code(f"{col}: {dtype}", language="plaintext")
                st.markdown("---") # Separator if multiple tables
            else:
                st.write("Schema item not in the expected format.")
        if schema_data and isinstance(schema_data[-1], dict): # Remove last separator if it was added
             pass # A bit hacky, better to control separator logic more precisely if needed
    else:
        st.write("Schema not available or not in the expected format.")

# New function specifically for the prompt and starter code
def display_challenge_prompt_area(challenge_data):
    if not challenge_data:
        return # Or return False

    st.subheader("🧪 Challenge Prompt")
    st.markdown(challenge_data.get("prompt", "N/A"))
    st.code(challenge_data.get("starter_code", ""), language="sql")

# display_reflection_and_hints remains the same
def display_reflection_and_hints(challenge_data, current_day, current_challenge_idx):
    if not challenge_data:
        return

    st.subheader("💬 Reflection Prompts")
    reflection_prompts = challenge_data.get("reflection", [])
    if reflection_prompts:
        for r in reflection_prompts:
            st.markdown(f"- {r}")
    else:
        st.markdown("_No reflection prompts for this challenge._")

    st.markdown("---")

    hints = challenge_data.get("hints", [])
    if hints:
        toggle_key = f"show_hints_day{current_day}_chal{current_challenge_idx}"
        show_hints = st.toggle("💡 Need a Hint?", key=toggle_key, value=False, help="Click to see hints")
        if show_hints:
            for hint in hints:
                st.markdown(f"- {hint}")