#!/bin/bash

# ==============================================================================
# Automated Test Script for the Amazon Review Categorization Pipeline
# ==============================================================================
# This script clones the repository, sets up the environment, and runs two
# key tests:
#   1. A "sad path" test with an invalid argument to verify error handling.
#   2. A "happy path" test using the final production settings to verify a
#      successful, end-to-end execution.
#
# Instructions:
# 1. Ensure the required data files exist in the project's 'client_files' directory:
#    - client_files/Reviews.csv (the raw data)
#    - client_files/pre_scraped_data.zip (the pre-generated labeled data archive)
# 2. Run this script from the root of the project directory (e.g., /protege_interview_task).
#    It will create a new test directory ('protege_pipeline_test') and handle the rest.
# ==============================================================================

# --- Configuration ---
REPO_URL="https://github.com/thedudehimself/data_pipeline_task.git"
TEST_DIR="protege_pipeline_test"
SOURCE_DATA_DIR="../client_files"
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

# 1. Clean up and set up the test directory
echo "Step 1: Setting up a clean test directory..."
rm -rf "$TEST_DIR"
mkdir "$TEST_DIR"
cd "$TEST_DIR"

# 2. Clone the repository
echo "Step 2: Cloning the repository from GitHub..."
if ! git clone "$REPO_URL" .; then
    echo "❌ FATAL: Failed to clone the repository. Please check the REPO_URL."
    exit 1
fi

# 3. Set up the Python environment
echo "Step 3: Setting up Python virtual environment and installing dependencies..."
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 4. Prepare the data for the test run
echo "Step 4: Preparing data files for the --noscrape mode..."
# --- FIX: Use correct relative paths to the source data directory ---


# Check if the source files exist in the original project's client_files directory
if [ ! -f "$SOURCE_DATA_DIR/Reviews.csv" ] || [ ! -f "$SOURCE_DATA_DIR/pre_scraped_data.zip" ]; then
    echo "❌ FATAL: Required data files not found in '$SOURCE_DATA_DIR/'."
    echo "Please ensure 'Reviews.csv' and 'pre_scraped_data.zip' exist in the project's 'client_files' directory."
    exit 1
fi

# Create the client_files directory inside the new test directory
mkdir -p client_files

# Copy the data files from the source directory into the test's client_files directory
cp "$SOURCE_DATA_DIR/Reviews.csv" client_files/
cp "$SOURCE_DATA_DIR/pre_scraped_data.zip" client_files/

# 5. Make the master script executable
chmod +x interview_task.sh

# --- TEST CASE 1: MALFORMED ARGUMENTS ---
print_header "Running Test Case 1: Malformed Argument..."
echo "Testing with an invalid argument '--mike'. The script should fail gracefully."

# We expect this command to fail, so we reverse the exit code check
if ! ./interview_task.sh --noscrape auto --mike > /dev/null 2>&1; then
    echo "✅ PASSED: The script correctly rejected the invalid argument."
else
    echo "❌ FAILED: The script did not exit with an error on an invalid argument."
    exit 1
fi

# --- TEST CASE 2: FINAL PRODUCTION RUN ---
print_header "Running Test Case 2: Final Production Run (--noscrape --final auto)..."
./interview_task.sh --noscrape --final auto

# --- VERIFICATION ---
print_header "Verifying the final output..."

# 1. Check if the file was created
if [ ! -f "$FINAL_OUTPUT_FILE" ]; then
    echo "❌ FAILED: The final output file '$FINAL_OUTPUT_FILE' was not created."
    exit 1
fi
echo "✅ Final output file was created successfully."

# 2. Check if the file has content
LINE_COUNT=$(wc -l < "$FINAL_OUTPUT_FILE")
if [ "$LINE_COUNT" -le 1 ]; then
    echo "❌ FAILED: The final output file is empty or contains only a header."
    exit 1
fi
echo "✅ File contains data ($LINE_COUNT lines)."

# 3. Check if the --final flag worked (the text column should NOT be present)
HEADER=$(head -n 1 "$FINAL_OUTPUT_FILE")
if [[ "$HEADER" == *"CleanedText"* ]]; then
    echo "❌ FAILED: The --final flag did not work. 'CleanedText' column is present in the output."
    exit 1
fi
echo "✅ The --final flag worked correctly. Output is lean."

# --- FINAL REPORT ---
print_header "🎉🎉🎉 ALL TESTS PASSED SUCCESSFULLY! 🎉🎉🎉"

# Go back to the original directory
cd ..
echo "Test complete. All artifacts can be inspected in the '$TEST_DIR' directory."
