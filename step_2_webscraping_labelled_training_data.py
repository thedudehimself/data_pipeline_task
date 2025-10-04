import pandas as pd
from bs4 import BeautifulSoup
import time
import random
from tqdm import tqdm
import sys
import os

# --- Imports for Selenium ---
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
CLEANED_REVIEWS_FILE = './client_files/Cleaned_Reviews.csv'
OUTPUT_FILE = './client_files/product_categories_standardized.csv'
TOTAL_PRODUCTS_TO_SCRAPE = 2500

# --- Keyword Dictionary for Targeted Sampling ---
KEYWORD_MAP = {
    'Pet Supplies': ['dog', 'cat', 'puppy', 'kitten', 'pet', 'fish', 'ferret'],
    'Beauty': ['lotion', 'shampoo', 'conditioner', 'makeup', 'lipstick', 'mascara', 'skin'],
    'Health & Personal Care': ['vitamin', 'supplement', 'pill', 'medical', 'health', 'dental'],
    'Toys & Games': ['toy', 'game', 'puzzle', 'doll', 'fun', 'play'],
    'Automotive & Powersports': ['car', 'vehicle', 'tire', 'engine', 'automotive'],
    'Outdoors': ['outdoor', 'camping', 'hiking', 'sports', 'tent'],
    'Books': ['book', 'read', 'author', 'novel', 'pages'],
}

# --- Official Category List ---
OFFICIAL_CATEGORIES = [
    "Amazon Device Accessories", "Amazon Kindle", "Automotive & Powersports",
    "Baby Products", "Beauty", "Books", "Camera & Photo", "Cell Phones & Accessories",
    "Collectible Coins", "Consumer Electronics", "Entertainment Collectibles",
    "Fine Art", "Grocery & Gourmet Food", "Health & Personal Care", "Home & Garden",
    "Industrial & Scientific", "Kindle Accessories and Amazon Fire TV Accessories",
    "Major Appliances", "Music and DVD", "Musical Instruments", "Office Products",
    "Outdoors", "Personal Computers", "Pet Supplies", "Software", "Sports",
    "Sports Collectibles", "Tools & Home Improvement", "Toys & Games",
    "Video, DVD & Blu-ray", "Video Games", "Watches"
]

# --- Enforce Consistency on the Categories Aquired ---
def standardize_category(scraped_text):
    if not scraped_text or scraped_text.startswith("Category Not Found") or scraped_text.startswith("Request Failed"):
        return "Uncategorized"
    for official_cat in OFFICIAL_CATEGORIES:
        if official_cat in scraped_text:
            return official_cat
    return "Uncategorized"

# --- Headless Chrome ProductID Lookup (Loop) ---
def get_raw_category(driver, product_id):
    url = f"https://www.amazon.com/dp/{product_id}"
    try:
        driver.get(url)
        wait = WebDriverWait(driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, "wayfinding-breadcrumbs_feature_div")))
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        breadcrumb_div_soup = soup.find('div', id='wayfinding-breadcrumbs_feature_div')
        if breadcrumb_div_soup:
            return breadcrumb_div_soup.get_text(separator=' ', strip=True)
        else:
            return "Category Not Found"
    except Exception:
        return "Request Failed"

def create_targeted_list():
    """Scans reviews to create a balanced DataFrame of products to scrape."""
    print("--- Creating a Targeted List for Scraping ---")
    df = pd.read_csv(CLEANED_REVIEWS_FILE)
    df['CleanedText'] = df['CleanedText'].astype(str)

    # Aggregate all text for each product first
    product_reviews = df.groupby('ProductId')['CleanedText'].apply(' '.join).str.lower().reset_index()

    targeted_products = pd.DataFrame()
    for category, keywords in KEYWORD_MAP.items():
        pattern = '|'.join(keywords)
        matches = product_reviews[product_reviews['CleanedText'].str.contains(pattern, na=False)]
        print(f"  - Found {len(matches)} potential '{category}' products.")
        targeted_products = pd.concat([targeted_products, matches])
    
    # Remove duplicates in case a product matched multiple categories
    targeted_products = targeted_products.drop_duplicates(subset=['ProductId'])
    print(f"\nFound {len(targeted_products)} unique products through keyword targeting.")
    
    final_list_df = targeted_products
    if len(final_list_df) < TOTAL_PRODUCTS_TO_SCRAPE:
        print(f"Topping up list with random products to reach {TOTAL_PRODUCTS_TO_SCRAPE}.")
        remaining_needed = TOTAL_PRODUCTS_TO_SCRAPE - len(final_list_df)
        
        # Get IDs we've already targeted
        targeted_ids = set(final_list_df['ProductId'])
        # Find products that were not targeted
        random_pool_df = product_reviews[~product_reviews['ProductId'].isin(targeted_ids)]
        # Add a random sample from the remaining pool
        final_list_df = pd.concat([final_list_df, random_pool_df.sample(n=remaining_needed, random_state=42)])
        
    return final_list_df.head(TOTAL_PRODUCTS_TO_SCRAPE)

def main():
    df_to_scrape = create_targeted_list()

    print("\n--- Phase 1 (Targeted Scrape): Creating a Balanced Dataset ---")
    print("Setting up headless Chrome browser...")
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
    driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()), options=options)
    print("Browser setup complete.")

    try:
        results = []
        if os.path.exists(OUTPUT_FILE): #perform cleanup between runs
            os.remove(OUTPUT_FILE)

        for index, row in tqdm(df_to_scrape.iterrows(), total=len(df_to_scrape), desc="Targeted Scrape"): #Add progress bar here MWMW
            product_id = row['ProductId']
            cleaned_text = row['CleanedText'] # Get text from our targeted list
            
            raw_category = get_raw_category(driver, product_id)
            standardized_category = standardize_category(raw_category)
            
            # Include CleanedText in the results
            results.append({'ProductId': product_id, 'Category': standardized_category, 'CleanedText': cleaned_text})
            
            time.sleep(random.uniform(0.5, 1.5))

            if len(results) % 50 == 0:
                pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)
        
        pd.DataFrame(results).to_csv(OUTPUT_FILE, index=False)
        print(f"\n✅ Targeted scrape complete! Balanced data saved to: {OUTPUT_FILE}")

    except FileNotFoundError:
        print(f"❌ ERROR: The input file was not found at '{CLEANED_REVIEWS_FILE}'")
    finally:
        driver.quit()
        print("Browser closed.")

if __name__ == "__main__":
    main()

