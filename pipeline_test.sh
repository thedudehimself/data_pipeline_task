#!/bin/bash

# ==============================================================================
# Automated Test Script for the Amazon Review Categorization Pipeline
# ==============================================================================
# This script clones the repository, sets up the environment, and runs three
# key tests:
#   1. A "sad path" test with MISSING arguments.
#   2. A "sad path" test with an INVALID argument.
#   3. A "happy path" test using the final production settings.
#
# Instructions:
# 1. Ensure data files exist in the project's 'client_files' directory:
#    - client_files/Reviews.csv
#    - client_files/pre_scraped_data.zip
# 2. Run this script from the root of the project directory.
# ==============================================================================

# --- Configuration ---
REPO_URL="https://github.com/thedudehimself/data_pipeline_task.git"
TEST_DIR="protege_pipeline_test"
FINAL_OUTPUT_FILE="client_files/reviews_with_predicted_categories.csv"

# Stop the script if any command fails
set -e

# --- Helper Functions ---
print_header() {
    echo ""
    echo "=============================================================================="
    echo "$1"
    echo "=============================================================================="
}

# --- Script Logic ---
print_header "STARTING AUTOMATED PIPELINE TEST"

# 1. Setup
echo "Step 1: Setting up a clean test directory..."
rm -rf "$TEST_DIR"
mkdir "$TEST_DIR"
cd "$TEST_DIR"

echo "Step 2: Cloning the repository from GitHub..."
if ! git clone "$REPO_URL" .; then
    echo "❌ FATAL: Failed to clone the repository. Please check the REPO_URL."
    exit 1
fi

echo "Step 3: Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

echo "Step 4: Preparing data files..."
SOURCE_DATA_DIR="../client_files"
if [ ! -f "$SOURCE_DATA_DIR/Reviews.csv" ] || [ ! -f "$SOURCE_DATA_DIR/pre_scraped_data.zip" ]; then
    echo "❌ FATAL: Required data files not found in '$SOURCE_DATA_DIR/'."
    exit 1
fi
mkdir -p client_files
cp "$SOURCE_DATA_DIR/Reviews.csv" client_files/
cp "$SOURCE_DATA_DIR/pre_scraped_data.zip" client_files/

chmod +x interview_task.sh

# --- TEST CASE 1: MISSING ARGUMENTS ---
print_header "Running Test Case 1: Missing Arguments..."
echo "Testing with no arguments. The script should fail gracefully."

# We expect this command to fail, so we reverse the exit code check (!)
if ! ./interview_task.sh > /dev/null 2>&1; then
    echo "✅ PASSED: The script correctly exited with an error on missing arguments."
else
    echo "❌ FAILED: The script did not exit with an error on missing arguments."
    exit 1
fi

# --- TEST CASE 2: MALFORMED ARGUMENT ---
print_header "Running Test Case 2: Malformed Argument..."
echo "Testing with an invalid argument '--mike'. The script should fail gracefully."

if ! ./interview_task.sh --noscrape auto --mike > /dev/null 2>&1; then
    echo "✅ PASSED: The script correctly rejected the invalid argument."
else
    echo "❌ FAILED: The script did not exit with an error on an invalid argument."
    exit 1
fi

# --- TEST CASE 3: FINAL PRODUCTION RUN ---
print_header "Running Test Case 3: Final Production Run (--noscrape --final auto)..."
./interview_task.sh --noscrape --final auto

# --- VERIFICATION ---
print_header "Verifying the final output..."

# 1. Check if the file was created
if [ ! -f "$FINAL_OUTPUT_FILE" ]; then
    echo "❌ FAILED: The final output file '$FINAL_OUTPUT_FILE' was not created."
    exit 1
fi
echo "✅ Final output file was created successfully."

# 2. Check for content
LINE_COUNT=$(wc -l < "$FINAL_OUTPUT_FILE")
if [ "$LINE_COUNT" -le 1 ]; then
    echo "❌ FAILED: The final output file is empty or contains only a header."
    exit 1
fi
echo "✅ File contains data ($LINE_COUNT lines)."

# 3. Check if --final flag worked
HEADER=$(head -n 1 "$FINAL_OUTPUT_FILE")
if [[ "$HEADER" == *"CleanedText"* ]]; then
    echo "❌ FAILED: The --final flag did not work. 'CleanedText' column is present."
    exit 1
fi
echo "✅ The --final flag worked correctly. Output is lean."

# --- FINAL REPORT ---
print_header "🎉🎉🎉 ALL TESTS PASSED SUCCESSFULLY! 🎉🎉🎉"

cd ..
echo "Test complete. Artifacts are in the '$TEST_DIR' directory."

