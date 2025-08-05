from pymongo import MongoClient
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
import time


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
def get_reservation_link(restaurant_name):
    cached = get_cached_link_mongo(restaurant_name)
    if cached:
        print(f"🔁 Found cached link for {restaurant_name}")
        return cached
    
    options = Options()
    options.add_argument("--headless")
    service = Service(executable_path='chromedriver.exe')
    driver = webdriver.Chrome(service=service, options=options)

    try:
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
        return link
    except Exception as e:
        print("Error:", e)
        return None
    finally:
        driver.quit()

