import pandas as pd
import unicodedata

def normalize_df(df):
    if df is None:
        return None
    if not isinstance(df, pd.DataFrame):
        st.error(f"Expected a DataFrame for normalization, got {type(df)}")
        return pd.DataFrame() # Return empty DF to prevent further errors

    def clean(val):
        if pd.isnull(val): return val
        val_str = str(val).strip().lower()
        # Attempt to convert to numeric if possible, helps with type mismatches from SQL
        try:
            if '.' in val_str: # Potentially float
                num_val = float(val_str)
                if num_val == int(num_val): # if it's like 5.0, treat as int 5
                    return int(num_val)
                return num_val
            else: # Potentially int
                return int(val_str)
        except ValueError:
            # Not numeric, proceed with string normalization
            return unicodedata.normalize("NFC", val_str)

    df_copy = df.copy()
    df_copy.columns = [str(col).strip().lower() for col in df_copy.columns]

    # Apply cleaning to all cells
    for col in df_copy.columns:
        df_copy[col] = df_copy[col].apply(clean)

    # Sort columns and then rows for consistent comparison
    df_copy = df_copy.reindex(sorted(df_copy.columns), axis=1)
    if not df_copy.empty:
        df_copy = df_copy.sort_values(by=df_copy.columns.tolist()).reset_index(drop=True)
    return df_copy


def validate_output(user_df: pd.DataFrame, expected_output_data: list):
    if user_df is None:
        return False, None, None # Not correct, no normalized user_df, no normalized_expected_df

    expected_df = pd.DataFrame(expected_output_data)
    
    norm_user_df = normalize_df(user_df)
    norm_expected_df = normalize_df(expected_df)

    # Debug:
    # st.write("Normalized User DF:")
    # st.dataframe(norm_user_df)
    # st.write("Normalized Expected DF:")
    # st.dataframe(norm_expected_df)

    # Check column names
    if list(norm_user_df.columns) != list(norm_expected_df.columns):
        # st.warning(f"Column mismatch. User: {list(norm_user_df.columns)}, Expected: {list(norm_expected_df.columns)}")
        return False, norm_user_df, norm_expected_df
    
    # Check number of rows
    if len(norm_user_df) != len(norm_expected_df):
        # st.warning(f"Row count mismatch. User: {len(norm_user_df)}, Expected: {len(norm_expected_df)}")
        return False, norm_user_df, norm_expected_df

    # Final check with .equals after sorting
    is_correct = norm_user_df.equals(norm_expected_df)
    return is_correct, norm_user_df, norm_expected_df