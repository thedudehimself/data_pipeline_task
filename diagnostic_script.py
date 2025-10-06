import pandas as pd
import sys

# --- Configuration ---
LABELED_DATA_FILE = './client_files/product_categories_standardized.csv'

def analyze_data_balance():
    """
    Reads the scraped category data and prints the distribution
    of categories to diagnose imbalance.
    """
    print("--- Analyzing Training Data Balance ---")
    try:
        df = pd.read_csv(LABELED_DATA_FILE)
        
        # Filter out the 'Uncategorized' rows as they aren't used for training
        df_labeled = df[df['Category'] != 'Uncategorized']
        
        print(f"Total labeled products for training: {len(df_labeled)}\n")
        
        print("Category Distribution:")
        # The value_counts() function is perfect for this
        category_counts = df_labeled['Category'].value_counts()
        
        print(category_counts)
        
        print("\n--- Diagnosis ---")
        if category_counts.iloc[0] / len(df_labeled) > 0.8:
            print("The training data is heavily skewed towards one category.")
            print("This explains why the model predicts the same category for most products.")
        else:
            print("The training data is reasonably balanced.")

    except FileNotFoundError:
        print(f"❌ ERROR: The file '{LABELED_DATA_FILE}' was not found.")
        sys.exit(1)

if __name__ == "__main__":
    analyze_data_balance()
