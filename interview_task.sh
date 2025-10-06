#!/bin/bash

# ==============================================================================
# Master Orchestration Script for Protege Interview Task (v8 - Final)
# ==============================================================================
# This script runs the entire data processing and machine learning pipeline.
# Now with robust validation and correct handling of optional arguments.
#
# Usage:
#   ./interview_task.sh [--noscrape] [--final] [auto | <number>]
# ==============================================================================

# --- Configuration ---
set -e
STEP0_SCRIPT="step_0_data_discovery.py"
STEP1_SCRIPT="step_1_elt.py"
STEP2_SCRIPT="step_2_webscraping_labelled_training_data.py"
STEP2_5_SCRIPT="step_2.5_training_parameter_tuning_optional.py"
STEP3_SCRIPT="step_3_NLP_data_classification_arg.py"
DATA_ARCHIVE="client_files/pre_scraped_data.zip"
RAW_DATA_FILE="client_files/Reviews.csv"

# --- Setup: Ensure output directory exists ---
echo "Ensuring client_files directory exists..."
mkdir -p client_files

# --- Robust Argument Parsing ---
NOSCRAPE=false
FINAL_FLAG=""
MAX_FEATURES_ARG=""

for arg in "$@"; do
  case $arg in
    --noscrape)
      NOSCRAPE=true
      ;;
    --final)
      FINAL_FLAG="--final"
      ;;
    auto)
      MAX_FEATURES_ARG="auto"
      ;;
    *)
      if [[ $arg =~ ^[0-9]+$ ]]; then
        MAX_FEATURES_ARG=$arg
      else
        echo "❌ Error: Invalid argument '$arg'"
        echo "Usage: ./interview_task.sh [--noscrape] [--final] [auto | <number>]"
        exit 1
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

# --- Step 0, 1, and 2 ---
print_header "Running Step 0: Data Discovery..."
python3 "$STEP0_SCRIPT" "$RAW_DATA_FILE"

print_header "Running Step 1: Data Cleaning (ELT)..."
python3 "$STEP1_SCRIPT"

if [ "$NOSCRAPE" = true ]; then
    print_header "Skipping Step 2 (Web Scraping) due to --noscrape flag."
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
        echo -e "❌ Error: The tuning script (Step 2.5) failed.\n--- Python Error Output ---\n$TUNE_OUTPUT\n--------------------------"
        exit 1
    fi
    echo "$TUNE_OUTPUT"
    BEST_FEATURES=$(echo "$TUNE_OUTPUT" | grep "Best performance found with" | awk '{print $7}')
    if [ -z "$BEST_FEATURES" ]; then
        echo "❌ Error: Could not automatically determine the best max_features value."
        exit 1
    fi
    echo "Found optimal max_features = $BEST_FEATURES"
    
    # --- FIX: Build argument array to handle optional flags ---
    PYTHON_ARGS=("--max_features" "$BEST_FEATURES")
    if [ -n "$FINAL_FLAG" ]; then
        PYTHON_ARGS+=("$FINAL_FLAG")
    fi
    
    print_header "Running Step 3: NLP Classification with optimal settings..."
    python3 "$STEP3_SCRIPT" "${PYTHON_ARGS[@]}"
else
    # --- FIX: Build argument array to handle optional flags ---
    PYTHON_ARGS=("--max_features" "$MAX_FEATURES_ARG")
    if [ -n "$FINAL_FLAG" ]; then
        PYTHON_ARGS+=("$FINAL_FLAG")
    fi

    print_header "Running Step 3 (Manual Mode): NLP Classification with max_features = $MAX_FEATURES_ARG..."
    python3 "$STEP3_SCRIPT" "${PYTHON_ARGS[@]}"
fi

print_header "🎉🎉🎉 Project Pipeline Complete! 🎉🎉🎉"

