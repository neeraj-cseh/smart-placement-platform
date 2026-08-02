import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def test_prep_pages_light():
    chrome_options = Options()
    chrome_options.add_argument("--headless") # run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1200,1000")

    # Set capabilities to capture logs
    chrome_options.set_capability('goog:loggingPrefs', {'browser': 'ALL'})

    print("Initializing webdriver...")
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
    
    try:
        print("Visiting login page...")
        driver.get("http://localhost:5174/login")
        time.sleep(2)
        
        print("Logging in...")
        driver.find_element(By.CSS_SELECTOR, "input[type='email']").send_keys("student@prepsmart.dev")
        driver.find_element(By.CSS_SELECTOR, "input[type='password']").send_keys("PrepSmart@123")
        driver.find_element(By.CSS_SELECTOR, "button[type='submit']").click()
        
        time.sleep(4)
        print("Login completed. Current URL:", driver.current_url)

        # Visit Roadmap Page first to load data
        driver.get("http://localhost:5174/prep/roadmaps")
        time.sleep(4)

        # Toggle theme to light mode by clicking the sidebar theme btn
        print("Toggling theme to light mode...")
        theme_btn = driver.find_element(By.CSS_SELECTOR, ".sidebar__theme-btn")
        theme_btn.click()
        time.sleep(2)

        pages = [
            ("roadmaps_light", "http://localhost:5174/prep/roadmaps"),
            ("journey_light", "http://localhost:5174/prep/journey"),
            ("milestones_light", "http://localhost:5174/prep/milestones")
        ]

        for name, url in pages:
            print(f"Navigating to {name} page: {url}...")
            driver.get(url)
            time.sleep(4)
            
            # Take a screenshot to visualize
            screenshot_path = f"C:\\Users\\neera\\.gemini\\antigravity\\brain\\e15fdf45-f6d5-4221-a029-1d0aeff2bd50\\scratch\\prep_{name}.png"
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")

    except Exception as e:
        print("An error occurred during browser testing:", str(e))
    finally:
        driver.quit()

if __name__ == '__main__':
    test_prep_pages_light()
