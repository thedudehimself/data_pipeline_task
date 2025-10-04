#!/bin/bash

# ==============================================================================
# Master Orchestration Script for Protege Interview Task (v6 - Final)
# ==============================================================================
# This script runs the entire data processing and machine learning pipeline,
# from initial data discovery to final classification.
# ==============================================================================

# --- Configuration ---
set -e
STEP0_SCRIPT="step_0_data_discovery.py"
STEP1_SCRIPT="step_1_elt.py"
STEP2_SCRIPT="step_2_webscraping_labelled_training_data.py"
STEP2_5_SCRIPT="step_2.5_training_parameter_tuning_optional.py"
STEP3_SCRIPT="step_3_NLP_data_classification.py"
DATA_ARCHIVE="client_files/pre_scraped_data.zip"
RAW_DATA_FILE="client_files/Reviews.csv"

# --- Setup: Ensure output directory exists ---
echo "Ensuring client_files directory exists..."
mkdir -p client_files

# --- Robust Argument Parsing ---
NOSCRAPE=false
MAX_FEATURES_ARG=""

for arg in "$@"; do
  case $arg in
    --noscrape)
      NOSCRAPE=true
      ;;
    auto)
      MAX_FEATURES_ARG="auto"
      ;;
    *)
      if [[ $arg =~ ^[0-9]+$ ]]; then
        MAX_FEATURES_ARG=$arg
      fi
      ;;
  esac
done

# --- Helper Functions ---
print_header() {
    echo ""
    echo "=============================================================================="
    echo "$1"
    echo "=============================================================================="
}

# --- Script Logic ---
if [ -z "$MAX_FEATURES_ARG" ]; then
    echo "❌ Error: Missing argument. Please provide 'auto' or a numeric value for max_features."
    exit 1
fi

# --- Step 0: Data Discovery ---
print_header "Running Step 0: Data Discovery..."
python3 "$STEP0_SCRIPT" "$RAW_DATA_FILE"

# --- Step 1: Data Cleaning (ELT) ---
print_header "Running Step 1: Data Cleaning (ELT)..."
python3 "$STEP1_SCRIPT"

# --- Step 2: Web Scraping or Data Extraction ---
if [ "$NOSCRAPE" = true ]; then
    print_header "Skipping Step 2 (Web Scraping) due to --noscrape flag."
    echo "Extracting pre-scraped data from $DATA_ARCHIVE..."
    
    if [ ! -f "$DATA_ARCHIVE" ]; then
        echo "❌ Error: Archive file not found at $DATA_ARCHIVE"
        exit 1
    fi
    
    unzip -o "$DATA_ARCHIVE" product_categories_standardized.csv -d client_files/
    echo "✅ Pre-scraped data extracted successfully."
else
    print_header "Running Step 2: Web Scraping for Labeled Training Data..."
    python3 "$STEP2_SCRIPT"
fi

# --- Step 2.5 / 3: Tuning and Classification ---
if [ "$MAX_FEATURES_ARG" == "auto" ]; then
    print_header "Running Step 2.5 (Auto Mode): Tuning for optimal max_features..."
    
    if ! TUNE_OUTPUT=$(python3 "$STEP2_5_SCRIPT" 2>&1); then
        echo "❌ Error: The tuning script (Step 2.5) failed to execute."
        echo "--- Python Error Output ---"
        echo "$TUNE_OUTPUT"
        echo "--------------------------"
        exit 1
    fi
    echo "$TUNE_OUTPUT"
    
    BEST_FEATURES=$(echo "$TUNE_OUTPUT" | grep "Best performance found with" | awk '{print $7}')
    
    if [ -z "$BEST_FEATURES" ]; then
        echo "❌ Error: Could not automatically determine the best max_features value."
        exit 1
    fi
    
    echo "Found optimal max_features = $BEST_FEATURES"
    
    print_header "Running Step 3: NLP Classification with optimal settings..."
    python3 "$STEP3_SCRIPT" --max_features "$BEST_FEATURES"
else
    print_header "Running Step 3 (Manual Mode): NLP Classification with max_features = $MAX_FEATURES_ARG..."
    python3 "$STEP3_SCRIPT" --max_features "$MAX_FEATURES_ARG"
fi

print_header "🎉🎉🎉 Project Pipeline Complete! 🎉🎉🎉"

