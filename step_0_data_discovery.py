import pandas as pd
import io
import sys
import re

def analyze_text_formats(df, sample_size=1000):
    """
    Analyzes object-type columns to detect common string formats like HTML, JSON, etc.
    This provides a deeper look into the content of text columns.
    
    Args:
        df (pd.DataFrame): The DataFrame to analyze.
        sample_size (int): The number of rows to sample from each column for efficiency.
    """
    print(f"7. Data Format Analysis (Sample Size: up to {sample_size} rows per column):")
    
    # Define regex patterns and simple checks for various formats
    patterns = {
        'HTML Tag': re.compile(r'<[a-z][\s\S]*>', re.IGNORECASE),
        'URL': re.compile(r'https?://\S+'),
        'Email': re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
        'JSON-like': lambda s: isinstance(s, str) and len(s) > 1 and ((s.startswith('{') and s.endswith('}')) or (s.startswith('[') and s.endswith(']'))),
        'Base64-like': re.compile(r'^(?:[A-Za-z0-9+/]{4})*(?:[A-Za-z0-9+/]{2}==|[A-Za-z0-9+/]{3}=)?$'),
        'Hexadecimal String': re.compile(r'^[0-9a-fA-F]{4,}$'), # At least 4 hex chars
    }

    object_cols = df.select_dtypes(include=['object']).columns
    if not any(object_cols):
        print("   No text columns found to analyze.")
        print("-" * 35)
        return

    found_any_format = False
    for col in object_cols:
        non_null_series = df[col].dropna()
        if non_null_series.empty:
            continue
            
        sample = non_null_series.sample(n=min(len(non_null_series), sample_size), random_state=1)
        
        format_counts = {key: 0 for key in patterns}

        for item in sample:
            if not isinstance(item, str):
                continue
            for name, pattern in patterns.items():
                if callable(pattern): # For lambda functions
                    if pattern(item):
                        format_counts[name] += 1
                elif pattern.search(item): # For regex
                    format_counts[name] += 1
        
        detected_formats = {k: v for k, v in format_counts.items() if v > 0}

        if detected_formats:
            found_any_format = True
            print(f"   Column '{col}':")
            for name, count in detected_formats.items():
                percentage = (count / len(sample)) * 100
                print(f"     - Found '{name}' content in {count} of {len(sample)} sampled rows ({percentage:.1f}%).")
    
    if not found_any_format:
        print("   No specific data formats (HTML, URL, etc.) detected in text samples.")
    
    print("-" * 35)


def analyze_dataset(filepath_or_buffer):
    """
    Reads a CSV file into a pandas DataFrame and performs a preliminary analysis.

    Args:
        filepath_or_buffer (str or file-like object): The path to the CSV file or a buffer.
    """
    try:
        # By default, read_csv uses the first row for column names.
        df = pd.read_csv(filepath_or_buffer)

        print("--- Initial Data Analysis Report ---")
        print("\n")

        # 1. Display column information and DataFrame dimensions.
        print("1. Column and Row Overview:")
        print(f"   - Column names are pulled from the first row of the file.")
        print(f"   - Number of columns: {df.shape[1]}")
        print(f"   - Number of rows: {df.shape[0]}")
        print(f"   - Column Names: {list(df.columns)}")
        print("-" * 35)

        # 2. Display the first 5 rows to get a feel for the data
        print("2. First 5 Rows (Head):")
        print(df.head())
        print("-" * 35)

        # 3. Get a concise summary of the DataFrame
        # This includes column names, non-null counts, and data types (Dtypes)
        print("3. DataFrame Info:")
        # Use a string buffer to capture the output of df.info()
        buffer = io.StringIO()
        df.info(buf=buffer)
        print(buffer.getvalue())
        print("-" * 35)

        # 4. Generate descriptive statistics for numerical columns
        # This includes count, mean, std dev, min, max, and percentiles
        print("4. Descriptive Statistics (Numerical):")
        print(df.describe())
        print("-" * 35)
        
        # 5. Generate descriptive statistics for object/categorical columns
        print("5. Descriptive Statistics (Categorical/Object):")
        print(df.describe(include=['object']))
        print("-" * 35)

        # 6. Check for and count missing (null) values in each column
        print("6. Missing Values Count:")
        missing_values = df.isnull().sum()
        # Only display columns that have missing values
        if missing_values.sum() == 0:
            print("   No missing values found.")
        else:
            print(missing_values[missing_values > 0])
        print("-" * 35)
        
        # 7. NEW: Analyze the format of data within text columns
        analyze_text_formats(df)

        print("\n--- End of Report ---")

    except FileNotFoundError:
        print(f"Error: The file '{filepath_or_buffer}' was not found.")
    except pd.errors.ParserError:
        print(f"Error: Could not parse the file '{filepath_or_buffer}'. It might not be a valid CSV.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == '__main__':
    # Check if a filename is provided as a command-line argument.
    if len(sys.argv) != 2:
        print("Usage: python analyze_data.py <path_to_csv_file>")
        sys.exit(1) # Exit the script if the usage is incorrect.

    # The second command-line argument (sys.argv[1]) is the filename.
    csv_file = sys.argv[1]
    analyze_dataset(csv_file)

