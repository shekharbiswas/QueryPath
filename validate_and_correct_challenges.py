# validate_and_correct_challenges.py
import json
import os
import sqlite3
import pandas as pd
from jsonschema import validate, exceptions as jsonschema_exceptions
import copy # To deepcopy data structures for comparison

# --- Configuration ---
CHALLENGES_DIR = "challenges"
DB_PATH = "data/challenges.db"
BACKUP_DIR = "challenges_backup" # Optional: create a backup directory

# --- Import or Define normalize_df ---
# Ensure this is your robust normalization function from core/query_validator.py
try:
    # Assuming the script is run from the project root (same level as app.py)
    # and your project structure is querypath_app/core/query_validator.py
    from core.query_validator import normalize_df
    print("INFO: Successfully imported normalize_df from core.query_validator")
except ImportError:
    print("WARNING: Could not import normalize_df from core.query_validator.")
    print("         Using a placeholder normalize_df. Ensure this is correct for accurate validation!")
    def normalize_df(df):
        if df is None: return pd.DataFrame()
        if not isinstance(df, pd.DataFrame): return pd.DataFrame()
        if df.empty: return df

        df_copy = df.copy()
        df_copy.columns = [str(col).strip().lower() for col in df_copy.columns]

        def clean_value(val):
            if pd.isnull(val): return None # Consistent handling of NaN/None
            val_str = str(val).strip().lower()
            try: # Attempt numeric conversion
                if '.' in val_str or 'e' in val_str.lower(): # Potential float
                    num_val = float(val_str)
                    return int(num_val) if num_val.is_integer() else num_val
                else: # Potential int
                    return int(val_str)
            except ValueError: # Not numeric, treat as string
                import unicodedata
                return unicodedata.normalize("NFC", val_str)

        for col in df_copy.columns:
            df_copy[col] = df_copy[col].apply(clean_value)
        
        # Sort columns alphabetically, then sort rows by all columns
        df_copy = df_copy.reindex(sorted(df_copy.columns), axis=1)
        if not df_copy.empty:
            df_copy = df_copy.sort_values(by=df_copy.columns.tolist()).reset_index(drop=True)
        return df_copy

# --- JSON Schemas (same as before) ---
challenge_schema_def = {
    "type": "object",
    "properties": {
        "title": {"type": "string"},
        "scenario": {"type": "string"},
        "schema": {"type": ["object", "array"]},
        "prompt": {"type": "string"},
        "starter_code": {"type": "string"},
        "expected_query": {"type": "string"},
        "expected_output": {"type": "array", "items": {"type": "object"}},
        "reflection": {"type": "array", "items": {"type": "string"}},
        "hints": {"type": "array", "items": {"type": "string"}},
    },
    "required": ["title", "scenario", "schema", "prompt", "starter_code", "expected_query", "expected_output"]
}
day_file_schema = {
    "type": "object",
    "properties": {
        "day": {"type": "integer"},
        "challenges": {"type": "array", "items": challenge_schema_def}
    },
    "required": ["day", "challenges"]
}

def process_challenge_file(filepath, db_conn, auto_correct=False):
    print(f"\n--- Processing {filepath} ---")
    file_errors = 0
    file_corrections = 0
    original_data = None
    modified_data = None

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            original_data = json.load(f)
            modified_data = copy.deepcopy(original_data) # Work on a copy
    except Exception as e:
        print(f"  ERROR: Could not load or parse JSON: {e}")
        return 1, 0 # 1 error, 0 corrections

    # 1. Validate overall file schema
    try:
        validate(instance=modified_data, schema=day_file_schema)
        print("  INFO: Overall file schema OK.")
    except jsonschema_exceptions.ValidationError as e:
        print(f"  ERROR: File schema validation failed: {e.message} (Path: {list(e.path)})")
        file_errors += 1
        # If basic schema is wrong, probably not safe to auto-correct outputs
        return file_errors, file_corrections

    # 2. Process individual challenges
    for i, challenge_data in enumerate(modified_data.get("challenges", [])):
        challenge_title = challenge_data.get('title', f'Challenge {i+1}')
        print(f"  - Processing: '{challenge_title}'")

        expected_query_str = challenge_data.get("expected_query")
        current_expected_output_json = challenge_data.get("expected_output")

        if not expected_query_str:
            print(f"    WARNING: Missing 'expected_query' for '{challenge_title}'. Skipping output processing.")
            continue
        if current_expected_output_json is None:
            print(f"    WARNING: Missing 'expected_output' in JSON for '{challenge_title}'. Attempting to generate.")
            # Fall through to generate it if auto_correct is True

        try:
            # Generate correct output from DB
            actual_df_from_db = pd.read_sql_query(expected_query_str, db_conn)
            correct_expected_output_records = actual_df_from_db.to_dict(orient='records')

            # Normalize current JSON output and newly generated output for comparison
            # Ensure current_expected_output_json is not None before making a DataFrame
            if current_expected_output_json is not None:
                current_expected_df_from_json = pd.DataFrame(current_expected_output_json)
            else:
                current_expected_df_from_json = pd.DataFrame() # Empty if missing

            correct_expected_df_generated = pd.DataFrame(correct_expected_output_records)

            norm_current_json_df = normalize_df(current_expected_df_from_json)
            norm_correct_generated_df = normalize_df(correct_expected_df_generated)

            if not norm_current_json_df.equals(norm_correct_generated_df):
                print(f"    MISMATCH: 'expected_output' for '{challenge_title}' differs from query result.")
                # print(f"      Current JSON (Normalized):\n{norm_current_json_df.to_string() if not norm_current_json_df.empty else 'Empty'}")
                # print(f"      Query Result (Normalized):\n{norm_correct_generated_df.to_string() if not norm_correct_generated_df.empty else 'Empty'}")
                file_errors += 1 # Count as an error/mismatch
                if auto_correct:
                    print(f"    CORRECTING: Updating 'expected_output' for '{challenge_title}'.")
                    # Update the 'expected_output' in the modified_data structure
                    modified_data["challenges"][i]["expected_output"] = correct_expected_output_records
                    file_corrections += 1
            else:
                print(f"    INFO: 'expected_output' for '{challenge_title}' matches query result.")

        except Exception as e:
            print(f"    ERROR: SQL query execution or DataFrame processing failed for '{challenge_title}': {e}")
            print(f"      Query: {expected_query_str}")
            file_errors += 1
            # Do not attempt to correct if the query itself is problematic

    # 3. Save the file if corrections were made and auto_correct is True
    if auto_correct and file_corrections > 0:
        try:
            # Optional: Create a backup before overwriting
            if not os.path.exists(BACKUP_DIR):
                os.makedirs(BACKUP_DIR)
            backup_filepath = os.path.join(BACKUP_DIR, os.path.basename(filepath) + ".bak")
            with open(filepath, 'r', encoding='utf-8') as f_orig, open(backup_filepath, 'w', encoding='utf-8') as f_bak:
                f_bak.write(f_orig.read())
            print(f"  INFO: Original file backed up to {backup_filepath}")

            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(modified_data, f, indent=2)
            print(f"  SUCCESS: File '{filepath}' updated with {file_corrections} corrections.")
        except Exception as e:
            print(f"  ERROR: Could not write updated JSON to '{filepath}': {e}")
            file_errors += 1 # Failed to save correction

    elif file_corrections == 0 and file_errors == 0:
        print("  INFO: No corrections needed and no errors found in this file.")
    elif file_errors > 0:
        print(f"  SUMMARY: Found {file_errors} issues in this file. Corrections made: {file_corrections} (if auto_correct was True).")


    return file_errors, file_corrections

if __name__ == "__main__":
    # --- User Confirmation for Auto-Correction ---
    auto_correct_mode = False
    confirm = input("Do you want to enable AUTO-CORRECTION mode? This will modify JSON files. (yes/no): ").strip().lower()
    if confirm == 'yes':
        confirm_again = input("ARE YOU SURE you want to auto-correct files? Make sure you have backups! (yes/no): ").strip().lower()
        if confirm_again == 'yes':
            auto_correct_mode = True
            print("\n*** AUTO-CORRECTION ENABLED. Files will be modified. ***\n")
        else:
            print("\nAuto-correction cancelled by user.\n")
    else:
        print("\nRunning in validation-only mode. No files will be modified.\n")


    db_conn = None
    try:
        db_conn = sqlite3.connect(DB_PATH)
        print(f"INFO: Connected to database at {DB_PATH}")
    except Exception as e:
        print(f"CRITICAL ERROR: Could not connect to database at {DB_PATH}: {e}")
        exit(1)

    total_files_processed = 0
    total_file_level_errors = 0 # Files that had at least one error (schema or output mismatch)
    total_output_corrections = 0

    for filename in sorted(os.listdir(CHALLENGES_DIR)): # Sort for consistent processing order
        if filename.startswith("day") and filename.endswith(".json"):
            filepath = os.path.join(CHALLENGES_DIR, filename)
            errors_in_file, corrections_in_file = process_challenge_file(filepath, db_conn, auto_correct_mode)
            if errors_in_file > 0:
                total_file_level_errors +=1
            total_output_corrections += corrections_in_file
            total_files_processed += 1
    
    db_conn.close()

    print("\n--- SCRIPT SUMMARY ---")
    print(f"Total files processed: {total_files_processed}")
    if auto_correct_mode:
        print(f"Total 'expected_output' corrections made across all files: {total_output_corrections}")
    print(f"Total files with at least one identified issue (mismatch or error): {total_file_level_errors}")

    if total_file_level_errors == 0 and total_output_corrections == 0 and auto_correct_mode is False:
        print("\nSUCCESS: All challenge files validated successfully! No discrepancies found.")
    elif total_file_level_errors == 0 and total_output_corrections > 0 and auto_correct_mode is True:
        print("\nCOMPLETED: All identified discrepancies were corrected. Please review the changes.")
    elif total_file_level_errors > 0:
        print("\nWARNING: Issues found. Please review the logs above.")
    else: # No errors, no corrections, but auto-correct was enabled (meaning all were already correct)
        print("\nSUCCESS: All files were already consistent with query results (or no auto-correct was run).")