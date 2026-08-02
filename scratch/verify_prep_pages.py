import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def verify_prep():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1400,1800")
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
        print("Login complete. Current URL:", driver.current_url)

        # 1. Visit Roadmaps page
        print("Visiting Learning Roadmaps...")
        driver.get("http://localhost:5174/prep/roadmaps")
        time.sleep(4)
        screenshot_roadmaps = "C:\\Users\\neera\\.gemini\\antigravity\\brain\\e15fdf45-f6d5-4221-a029-1d0aeff2bd50\\scratch\\prep_roadmaps.png"
        driver.save_screenshot(screenshot_roadmaps)
        print(f"Roadmaps screenshot saved: {screenshot_roadmaps}")

        # 2. Visit Topic Journey page
        print("Visiting Topic Journey...")
        driver.get("http://localhost:5174/prep/journey?track=1")
        time.sleep(4)
        screenshot_journey = "C:\\Users\\neera\\.gemini\\antigravity\\brain\\e15fdf45-f6d5-4221-a029-1d0aeff2bd50\\scratch\\prep_journey.png"
        driver.save_screenshot(screenshot_journey)
        print(f"Topic Journey screenshot saved: {screenshot_journey}")

        # 3. Visit Milestones page
        print("Visiting Timed Milestones...")
        driver.get("http://localhost:5174/prep/milestones")
        time.sleep(4)
        screenshot_milestones = "C:\\Users\\neera\\.gemini\\antigravity\\brain\\e15fdf45-f6d5-4221-a029-1d0aeff2bd50\\scratch\\prep_milestones.png"
        driver.save_screenshot(screenshot_milestones)
        print(f"Milestones screenshot saved: {screenshot_milestones}")

        print("Browser Console Logs:")
        for log in driver.get_log('browser'):
            if log['level'] in ['WARNING', 'SEVERE']:
                print(log)

    except Exception as e:
        print("An error occurred during browser testing:", str(e))
    finally:
        driver.quit()

if __name__ == '__main__':
    verify_prep()
