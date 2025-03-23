import time
import pandas as pd
import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

# ✅ Setup Chrome options (Headless mode)
chrome_options = Options()
chrome_options.add_argument("--window-size=1920x1080")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

# ✅ Start the browser
driver = uc.Chrome(options=chrome_options)

# 📌 Base URL with pagination
base_url = "https://www.myntra.com/men-tshirts?p="

# 📌 Storage for data
products = []

# ✅ Function to scroll and load more items on each page
def scroll_page():
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Allow time for new products to load
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# ✅ Loop through pages (Set a limit to avoid infinite loop)
max_pages = 5  # Change this to 3732 to scrape everything
for page in range(1, max_pages + 1):
    print(f"📌 Scraping page {page}...")
    driver.get(base_url + str(page))
    time.sleep(5)  # Wait for page to load

    # Scroll and load items
    scroll_page()

    # ✅ Extract product data
    items = driver.find_elements(By.XPATH, "//li[@class='product-base']")
    for item in items:
        try:
            name = item.find_element(By.XPATH, ".//h3").text
            brand = item.find_element(By.XPATH, ".//h4").text
            price = item.find_element(By.XPATH, ".//span[@class='product-discountedPrice']").text
            original_price = item.find_element(By.XPATH, ".//span[@class='product-strike']").text
            discount = item.find_element(By.XPATH, ".//span[@class='product-discountPercentage']").text
            image_url = item.find_element(By.XPATH, ".//img").get_attribute("src")
            product_link = item.find_element(By.XPATH, ".//a").get_attribute("href")

            # Some products may not have ratings, so we handle exceptions
            try:
                rating = item.find_element(By.XPATH, ".//div[@class='product-ratingsContainer']//span").text
            except:
                rating = "N/A"

            # Some products may not have review counts, so we handle exceptions
            try:
                reviews = item.find_element(By.XPATH, ".//div[@class='product-ratingsContainer']//span[2]").text
            except:
                reviews = "N/A"

            products.append([brand, name, price, original_price, discount, rating, reviews, image_url, product_link])
        except:
            continue

    print(f"✅ Page {page} scraped successfully!")

# ✅ Save data to Excel
df = pd.DataFrame(products, columns=["Brand", "Name", "Price", "Original Price", "Discount", "Rating", "Reviews", "Image URL", "Product Link"])
df.to_excel("myntra_products_detailed.xlsx", index=False)

# ✅ Close browser
driver.quit()

print("✅ All pages scraped successfully! Data saved to myntra_products_detailed.xlsx.")
