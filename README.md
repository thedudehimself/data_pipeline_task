
# Amazon Product Review Categorization Pipeline

### 1. Executive Summary

This project is a complete, end-to-end data engineering pipeline designed to solve the business problem of categorizing a large, unstructured dataset of Amazon product reviews.

Starting with over 500,000 rows of raw, messy data, the final solution is an automated, multi-step system that intelligently analyzes the data, builds a targeted training set, and uses a machine learning model to categorize all ~74,000 unique products, **achieving a 97% prediction accuracy** on a validation set.

The entire pipeline is orchestrated by a single master script, making it fully automated, reproducible, and easy to run.

### 2. The Engineering Journey: From Discovery to Delivery

The final solution was the result of a multi-stage engineering process that involved diagnosing problems and strategically pivoting based on data.

#### Step 0: Initial Data Discovery

Before writing a single line of processing code, an automated discovery script (`step_0_data_discovery.py`) was run on the raw data. This initial analysis provided critical insights into the dataset's size, structure, and challenges—most notably, the presence of embedded HTML in the review text. This data-first approach ensured the subsequent pipeline was built on a solid foundation of understanding.

#### Step 1: Foundational Data Cleaning (ELT)

A robust Python script (`step_1_elt.py`) was built to create a clean foundation. It processes the data in memory-efficient chunks to handle the large file size and strips all HTML, preparing the text for analysis.

#### Step 2: The Critical Insight - Diagnosing Data Bias

An initial machine learning model misleadingly predicted one category ("Grocery") for everything. **Instead of trusting the flawed output, a diagnostic script was written to analyze the training data.** This proved the source dataset was over 90% food-related, explaining the model's biased behavior. This data-driven insight was critical to avoiding a flawed final deliverable.

#### Step 3: The Pivot to Intelligent Data Collection

Based on the diagnosis, the strategy pivoted. The final pipeline uses a **targeted acquisition** process (`step_2_webscraping...py`). It pre-scans all reviews for keywords related to under-represented categories (like "Pet Supplies" or "Beauty") to create a more balanced and intelligent training dataset for the model.

### 3. Key Results & Outcome

The final machine learning model (`step_3_NLP...py`), trained on the intelligently-gathered data, achieved:

-   **Final Model Accuracy: 97%**
    

This result significantly exceeded the project's stretch goal of 90%+ accuracy, validating the final hybrid strategy. The system successfully produced a complete list of all unique products and their predicted categories, a deliverable that is both comprehensive and trustworthy.

### 4. The Scripts: An Overview

The project is orchestrated by a master shell script, `interview_task.sh`, which executes the following Python scripts in order:

-   **`step_0_data_discovery.py`**: Analyzes the raw `Reviews.csv` and generates a high-level statistical and structural report.
    
-   **`step_1_elt.py`**: Cleans the raw data, stripping HTML and saving a clean `Cleaned_Reviews.csv`.
    
-   **`step_2_webscraping...py`**: Performs the targeted web scrape to create a balanced, labeled training dataset.
    
-   **`step_2.5_training...py` (Optional)**: Automatically tests multiple model configurations to find the most accurate one.
    
-   **`step_3_NLP...py`**: Trains the final machine learning model and predicts categories for the entire dataset.
    

### 5. How to Run

**Prerequisites:**

-   A Linux environment (or similar shell).
    
-   Python 3 and the Google Chrome browser.
    

**Instructions:**

1.  **Clone the repository** and navigate into the directory.
    
2.  **Create a virtual environment:**  
    ```
    python3 -m venv venv && source venv/bin/activate
    ```
    
3.  **Install dependencies:**  
    ```
    pip install -r requirements.txt
    ```
    
4.  **Add data:** Place the raw `Reviews.csv` and the `pre_scraped_data.zip` into the `client_files` directory.
    
5.  **Run the pipeline:**
    
    ```
    # Make the script executable
    chmod +x interview_task.sh
    
    # Run the full pipeline in auto-tuning mode, using the pre-scraped data, with the final output deduplicated "final list of product IDs to product categories... you do not need to run every single row"
    ./interview_task.sh --noscrape auto
    
    ```
