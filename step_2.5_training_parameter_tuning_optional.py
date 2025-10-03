import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import sys
import warnings

# Suppress warnings from sklearn about categories with no predictions
warnings.filterwarnings('ignore', category=UserWarning)

# --- Configuration ---
LABELED_CATEGORIES_FILE = './output/product_categories_standardized.csv'

# --- Hyperparameters to Test ---
# We'll test a range of vocabulary sizes for our model.
MAX_FEATURES_TO_TEST = [100, 500, 1000, 2000, 5000, 10000]

def tune_hyperparameters():
    """
    Loads the labeled data and tests different 'max_features' settings
    to find the one that yields the highest accuracy.
    """
    print("--- Hyperparameter Tuning for max_features ---")
    try:
        # 1. Load and Prepare the Data (same as Phase 2)
        print(f"Loading labeled data from '{LABELED_CATEGORIES_FILE}'...")
        training_data_raw = pd.read_csv(LABELED_CATEGORIES_FILE)
        
        training_data_raw = training_data_raw[training_data_raw['Category'] != 'Uncategorized'].dropna(subset=['CleanedText'])
        
        if len(training_data_raw) < 50:
            print(f"❌ ERROR: Not enough data ({len(training_data_raw)}) for tuning.")
            sys.exit(1)
            
        category_counts = training_data_raw['Category'].value_counts()
        viable_categories = category_counts[category_counts >= 2].index.tolist()
        training_data = training_data_raw[training_data_raw['Category'].isin(viable_categories)]
        
        # 2. Split the data ONCE. We use the same split for every test for a fair comparison.
        X = training_data['CleanedText']
        y = training_data['Category']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        results = {}

        # 3. Loop through each setting and test it
        for features in MAX_FEATURES_TO_TEST:
            print(f"\n--- Testing with max_features = {features} ---")
            
            # Vectorize the text with the current setting
            tfidf = TfidfVectorizer(stop_words='english', max_features=features, ngram_range=(1, 2))
            X_train_tfidf = tfidf.fit_transform(X_train)
            X_test_tfidf = tfidf.transform(X_test)
            
            # Train the model
            model = LogisticRegression(class_weight='balanced', random_state=42, max_iter=1000)
            model.fit(X_train_tfidf, y_train)
            
            # Evaluate and store the result
            y_pred = model.predict(X_test_tfidf)
            accuracy = accuracy_score(y_test, y_pred)
            print(f"  ✅ Accuracy: {accuracy:.2%}")
            results[features] = accuracy

        # 4. Report the best result
        best_features = max(results, key=results.get)
        best_accuracy = results[best_features]
        
        print("\n--- Tuning Complete ---")
        print(f"Best performance found with max_features = {best_features}")
        print(f"Best Accuracy: {best_accuracy:.2%}")

    except FileNotFoundError:
        print(f"❌ ERROR: The file '{LABELED_CATEGORIES_FILE}' was not found.")
        sys.exit(1)

if __name__ == "__main__":
    tune_hyperparameters()
