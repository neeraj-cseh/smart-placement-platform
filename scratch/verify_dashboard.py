import os
import sys
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

def test_dashboard():
    chrome_options = Options()
    chrome_options.add_argument("--headless") # run in headless mode
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--window-size=1400,3200")

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

        # Navigating to dashboard (usually root page)
        driver.get("http://localhost:5174/")
        time.sleep(5)
        print("Dashboard loaded. Current URL:", driver.current_url)

        # Take a screenshot to visualize expanded state
        screenshot_path = "C:\\Users\\neera\\.gemini\\antigravity\\brain\\e15fdf45-f6d5-4221-a029-1d0aeff2bd50\\scratch\\dashboard_expanded.png"
        driver.save_screenshot(screenshot_path)
        print(f"Expanded screenshot saved to: {screenshot_path}")

        # Minimize the sidebar by clicking toggle button
        print("Toggling sidebar to minimized...")
        toggle_btn = driver.find_element(By.CSS_SELECTOR, ".sidebar__toggle-btn")
        toggle_btn.click()
        time.sleep(1)

        # Move mouse away to avoid triggering hover expansion
        print("Moving mouse away from sidebar...")
        content_el = driver.find_element(By.CSS_SELECTOR, ".topbar__title")
        from selenium.webdriver.common.action_chains import ActionChains
        actions = ActionChains(driver)
        actions.move_to_element(content_el).perform()
        time.sleep(2.5) # wait for width transition to complete

        # Take a screenshot to visualize minimized state
        screenshot_path_min = "C:\\Users\\neera\\.gemini\\antigravity\\brain\\e15fdf45-f6d5-4221-a029-1d0aeff2bd50\\scratch\\dashboard_minimized.png"
        driver.save_screenshot(screenshot_path_min)
        print(f"Minimized screenshot saved to: {screenshot_path_min}")
        
        # Get browser logs
        print("Browser Console Logs:")
        for log in driver.get_log('browser'):
            print(log)

    except Exception as e:
        print("An error occurred during browser testing:", str(e))
        try:
            print("Browser Console Logs on failure:")
            for log in driver.get_log('browser'):
                print(log)
        except Exception as log_err:
            print("Failed to retrieve browser logs:", str(log_err))
    finally:
        driver.quit()

if __name__ == '__main__':
    test_dashboard()
