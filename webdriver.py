from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import json
import os
from datetime import datetime


def wait_for_avoxtun_element(driver):
    """Wait for the 'Ávöxtun' element to appear on the page"""
    print("Waiting for accounts table with 'Ávöxtun' to load...")
    
    try:
        wait = WebDriverWait(driver, 60)  # Increased timeout to 60 seconds
        
        # Wait specifically for the element containing "Ávöxtun" text
        # This mimics Power Automate's approach: table[Id="accounts-table"] > tbody > tr > td[Text="Ávöxtun"]
        avoxtur_element = wait.until(
            EC.presence_of_element_located((By.XPATH, "//table[@id='accounts-table']//tbody//tr//td[contains(text(), 'Ávöxtun')]"))
        )
        
        print(f"✅ Found 'Ávöxtun' element with text: '{avoxtur_element.text}'")
        return True
            
    except Exception as e:
        print(f"Could not find 'Ávöxtun' element: {e}")
        
        # Debug: Let's see what tables and content are actually available
        try:
            print("Debug: Looking for any tables...")
            tables = driver.find_elements(By.TAG_NAME, "table")
            print(f"Found {len(tables)} table(s)")
            
            for i, table in enumerate(tables):
                print(f"Table {i}: id='{table.get_attribute('id')}', class='{table.get_attribute('class')}'")
                
            # Also check for any cells with text
            cells = driver.find_elements(By.TAG_NAME, "td")
            print(f"Found {len(cells)} td elements")
            
            for cell in cells[:10]:  # Show first 10 cells only
                if cell.text.strip():
                    print(f"Cell text: '{cell.text[:50]}'")
                    
        except Exception as debug_e:
            print(f"Debug failed: {debug_e}")
        
        return False


def login_to_islandsbanki():
    # Set up Chrome options
    chrome_options = Options()
    # Remove headless mode to see the browser in action
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    
    chrome_options.add_argument("--proxy-server=http://127.0.0.1:8080")
    
    # Initialize the driver
    # Make sure you have chromedriver installed and in PATH
    # Or specify the path: service = Service('/path/to/chromedriver')
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        # Navigate to the website
        print("Navigating to Íslandsbanki website...")
        driver.get("https://netbanki.islandsbanki.is/")
        
        # Wait for the page to load
        wait = WebDriverWait(driver, 60)
        
        print("Looking for phone number input field...")
        
        # Find the input field for phone number
        try:
            input_field = wait.until(EC.presence_of_element_located(
                (By.CSS_SELECTOR, "isb-login input")
            ))
            print("Found input field, entering phone number...")
            input_field.clear()
            input_field.send_keys("8550034")
            time.sleep(1)  # Small delay to ensure input is registered
        except:
            print("Could not find input field")
            return False
        
        # Find and click the login button
        print("Looking for login button...")
        
        try:
            login_button = driver.find_element(By.ID, "forward-button")
            print("Found login button, clicking...")
            driver.execute_script("arguments[0].click();", login_button)
            print("Button clicked successfully!")
            
            # Wait longer for the result and page to fully load
            print("Waiting for page to load after login...")
            time.sleep(5)
            
            # Print current URL to see where we are
            print(f"Current URL: {driver.current_url}")
            
            # Check if we're still on the login page or have moved
            if "netbanki.islandsbanki.is" not in driver.current_url:
                print("⚠️ Not on expected domain after login attempt")
            
            # First wait for URL to change from authentication page
            print("Waiting for redirect from authentication page...")
            try:
                WebDriverWait(driver, 30).until(
                    lambda d: "audkenning" not in d.current_url
                )
                print(f"✅ Redirected to: {driver.current_url}")
            except:
                print("⚠️ Still on authentication page, continuing anyway...")
            
            # Additional wait for page content to load
            time.sleep(10)
            
            # Wait for accounts table with "Ávöxtun" text
            if wait_for_avoxtun_element(driver):
                print("✅ Login successful!")
                
                # Click the cookie accept button if present
                try:
                    print("Looking for cookie accept button...")
                    cookie_button = driver.find_element(By.ID, "accept-all-button")
                    print("Found cookie accept button, clicking...")
                    driver.execute_script("arguments[0].click();", cookie_button)
                    print("Cookie button clicked successfully!")
                    time.sleep(2)  # Small delay after clicking
                except Exception as e:
                    print(f"Cookie button not found or could not click: {e}")
                
                # Wait 10 seconds before clicking the logo
                print("Waiting 10 seconds before clicking logo...")
                time.sleep(10)
                
                # Click the logo element as specified
                try:
                    logo_element = driver.find_element(By.CSS_SELECTOR, "div[id='isb-logo'] > a > img:nth-child(2)")
                    print("Found logo element, clicking...")
                    driver.execute_script("arguments[0].click();", logo_element)
                    print("Logo clicked successfully!")
                    
                    # Wait for "Ávöxtun" again after clicking logo
                    if wait_for_avoxtun_element(driver):
                        print("✅ Found 'Ávöxtun' again after logo click!")
                        return True
                    else:
                        print("❌ Could not find 'Ávöxtun' after logo click")
                        return False
                        
                except Exception as e:
                    print(f"Could not click logo element: {e}")
                    return False
            else:
                return False
            
        except:
            print("Could not find login button")
            return False
            
        print("Login process completed!")
        return True
        
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return False
        
    finally:
        # Keep browser open for a few seconds to see the result
        time.sleep(5)
        # Uncomment the next line to close the browser automatically
        # driver.quit()
        
        print("Script finished. Browser will remain open for inspection.")

if __name__ == "__main__":
    result = login_to_islandsbanki()
    if result:
        print("🎉 Overall Status: SUCCESS")
    else:
        print("💥 Overall Status: FAILED")