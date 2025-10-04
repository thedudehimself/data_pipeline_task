import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report
import sys
import argparse

# --- Configuration ---
CLEANED_REVIEWS_FILE = './client_files/Cleaned_Reviews.csv'
LABELED_CATEGORIES_FILE = './client_files/product_categories_standardized.csv'
FINAL_OUTPUT_FILE = './client_files/reviews_with_predicted_categories.csv'

def main(max_features_value, is_final_run):
    """
    Trains a balanced NLP model and predicts categories.
    Outputs a final, lean CSV if is_final_run is True.
    """
    print("\n--- Phase 2: Training NLP Model on Balanced Data ---")
    try:
        # 1. Load Data
        print(f"Loading labeled data from '{LABELED_CATEGORIES_FILE}'...")
        training_data_raw = pd.read_csv(LABELED_CATEGORIES_FILE)
        
        training_data_raw = training_data_raw[training_data_raw['Category'] != 'Uncategorized'].dropna(subset=['CleanedText'])
        
        if len(training_data_raw) < 50:
            print(f"❌ ERROR: Not enough data ({len(training_data_raw)}) for training.")
            sys.exit(1)

        print(f"Loaded {len(training_data_raw)} successfully scraped categories for training.")

        category_counts = training_data_raw['Category'].value_counts()
        viable_categories = category_counts[category_counts >= 2].index.tolist()
        training_data = training_data_raw[training_data_raw['Category'].isin(viable_categories)]
        
        # 2. Train-Test Split
        X = training_data['CleanedText']
        y = training_data['Category']
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # 3. Feature Extraction (TF-IDF)
        print(f"Vectorizing text using TF-IDF with max_features = {max_features_value}...")
        tfidf = TfidfVectorizer(stop_words='english', max_features=max_features_value, ngram_range=(1, 2))
        X_train_tfidf = tfidf.fit_transform(X_train)
        X_test_tfidf = tfidf.transform(X_test)
        
        # 4. Train the Model
        model = LogisticRegression(class_weight='balanced', random_state=42, max_iter=1000)
        model.fit(X_train_tfidf, y_train)
        
        # 5. Evaluate the Model
        print("\n--- Model Performance Evaluation ---")
        y_pred = model.predict(X_test_tfidf)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"✅ Model Accuracy on Test Set: {accuracy:.2%}")
        
        # 6. Prepare Full Dataset
        print("\nLoading and aggregating all reviews for final prediction...")
        df_reviews = pd.read_csv(CLEANED_REVIEWS_FILE).dropna(subset=['CleanedText'])
        product_reviews = df_reviews.groupby('ProductId')['CleanedText'].apply(' '.join).reset_index()

        # 7. Predict on Entire Dataset
        all_reviews_tfidf = tfidf.transform(product_reviews['CleanedText'])
        product_reviews['PredictedCategory'] = model.predict(all_reviews_tfidf)
        
        # 8. Save Final File
        if is_final_run:
            print("Saving final, production-ready output (without text column)...")
            final_df = product_reviews[['ProductId', 'PredictedCategory']]
        else:
            print("Saving final output file for validation (with text column)...")
            final_df = product_reviews[['ProductId', 'PredictedCategory', 'CleanedText']]
        
        final_df.to_csv(FINAL_OUTPUT_FILE, index=False)
        
        print(f"\n✅ Phase 2 Complete! Final data saved to: {FINAL_OUTPUT_FILE}")

    except FileNotFoundError as e:
        print(f"❌ ERROR: A required file was not found. Please check paths: {e}")
        sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train and run the NLP classifier.")
    parser.add_argument(
        '--max_features', 
        type=int, 
        default=5000,
        help='The maximum number of features for the TfidfVectorizer.'
    )
    # --- NEW ARGUMENT ---
    parser.add_argument(
        '--final',
        action='store_true', # Makes this a True/False flag
        help='If set, saves the final output without the CleanedText column.'
    )
    args = parser.parse_args()
    
    main(args.max_features, args.final)

