import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def test_prep_pages():
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

        # Visit Roadmap Page first to make sure roadmaps are loaded
        pages = [
            ("roadmaps", "http://localhost:5174/prep/roadmaps"),
            ("journey", "http://localhost:5174/prep/journey"),
            ("milestones", "http://localhost:5174/prep/milestones")
        ]

        for name, url in pages:
            print(f"Navigating to {name} page: {url}...")
            driver.get(url)
            time.sleep(5)
            print(f"Current URL: {driver.current_url}")
            
            # Take a screenshot to visualize
            screenshot_path = f"C:\\Users\\neera\\.gemini\\antigravity\\brain\\e15fdf45-f6d5-4221-a029-1d0aeff2bd50\\scratch\\prep_{name}.png"
            driver.save_screenshot(screenshot_path)
            print(f"Screenshot saved to: {screenshot_path}")
            
            # Get browser logs
            print(f"Browser Console Logs for {name}:")
            for log in driver.get_log('browser'):
                print(log)

            body_text = driver.find_element(By.TAG_NAME, "body").text
            print(f"=== {name.upper()} BODY TEXT ===")
            print(body_text[:1000])
            print("=================")

    except Exception as e:
        print("An error occurred during browser testing:", str(e))
    finally:
        driver.quit()

if __name__ == '__main__':
    test_prep_pages()
