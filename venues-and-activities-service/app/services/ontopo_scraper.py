from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time
import os
import platform


def get_mongo_collection():
   
    client = MongoClient("mongodb+srv://dartoledano11:DarToledano111@cluster0.qymb8gz.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")

    db = client["places_db"]
    return db["ontopo_links"]


def get_cached_link_mongo(name):
    collection = get_mongo_collection()
    doc = collection.find_one({"name": name})
    return doc["link"] if doc else None

def save_link_mongo(name, link):
    collection = get_mongo_collection()
    collection.update_one(
        {"name": name},
        {"$set": {"link": link}},
        upsert=True
    )

def get_chromedriver_path():
    """Get the correct ChromeDriver path based on OS and location"""
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Go up to the service root directory
    service_root = os.path.dirname(os.path.dirname(script_dir))
    
    # Define possible ChromeDriver locations
    possible_paths = [
        # In the service root directory
        os.path.join(service_root, "chromedriver.exe"),  # Windows
        os.path.join(service_root, "chromedriver"),      # Linux/Mac
        
        # In the current working directory
        "chromedriver.exe",  # Windows
        "chromedriver",      # Linux/Mac
        
        # In system PATH (if installed globally)
        "chromedriver.exe" if platform.system() == "Windows" else "chromedriver"
    ]
    
    # Check which path exists
    for path in possible_paths:
        if os.path.exists(path):
            print(f"Found ChromeDriver at: {path}")
            return path
    
    # If none found, return None
    print("ChromeDriver not found in any of these locations:")
    for path in possible_paths:
        print(f"   - {path}")
    return None

def get_reservation_link(restaurant_name):
    cached = get_cached_link_mongo(restaurant_name)
    if cached:
        print(f"Found cached link for {restaurant_name}")
        return cached
    
    # Get ChromeDriver path
    chromedriver_path = get_chromedriver_path()
    if not chromedriver_path:
        print("ChromeDriver not found. Cannot scrape Ontopo.")
        return None
    
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    try:
        service = Service(executable_path=chromedriver_path)
        driver = webdriver.Chrome(service=service, options=options)
        print(f"Starting Chrome browser for {restaurant_name}")
        
        driver.get("https://ontopo.com/he/il")
        WebDriverWait(driver, 15).until(EC.presence_of_element_located((By.CLASS_NAME, "search-container")))
        time.sleep(2)
        search_box = driver.find_element(
            By.XPATH,
            "//p[contains(text(), 'חיפוש עסק לפי שם')]/ancestor::div[@class='search-container cursor-pointer relative bg-white']"
        )
        driver.execute_script("arguments[0].click();", search_box)
        time.sleep(2)
        search_input = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.CSS_SELECTOR, "input[placeholder='חיפוש']"))
        )
        search_input.clear()
        search_input.send_keys(restaurant_name)
        time.sleep(2)
        result = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, ".results .result"))
        )
        result.click()
        reserve_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//p[text()='הזמנת מקום']/ancestor::div[contains(@class, 'venue-search-btn')]"))
        )
        reserve_button.click()
        WebDriverWait(driver, 10).until(lambda d: "/he/il/page/" in d.current_url)
        link = driver.current_url
        save_link_mongo(restaurant_name, link)
        print(f"Successfully found Ontopo link for {restaurant_name}")
        return link
    except Exception as e:
        print(f"Error scraping Ontopo for {restaurant_name}: {e}")
        return None
    finally:
        try:
            driver.quit()
        except:
            pass

