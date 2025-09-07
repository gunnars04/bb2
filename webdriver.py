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

def save_auth_data(driver, filename="auth_data.json"):
    """
    Save all authentication data (cookies, localStorage, sessionStorage) to a file
    """
    try:
        auth_data = {
            "timestamp": datetime.now().isoformat(),
            "url": driver.current_url,
            "cookies": driver.get_cookies(),
            "local_storage": {},
            "session_storage": {}
        }
        
        # Get localStorage data
        try:
            local_storage_script = "return Object.keys(localStorage).reduce((obj, key) => { obj[key] = localStorage.getItem(key); return obj; }, {});"
            auth_data["local_storage"] = driver.execute_script(local_storage_script)
        except Exception as e:
            print(f"Could not retrieve localStorage: {e}")
        
        # Get sessionStorage data
        try:
            session_storage_script = "return Object.keys(sessionStorage).reduce((obj, key) => { obj[key] = sessionStorage.getItem(key); return obj; }, {});"
            auth_data["session_storage"] = driver.execute_script(session_storage_script)
        except Exception as e:
            print(f"Could not retrieve sessionStorage: {e}")
        
        # Save to file
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(auth_data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Auth data saved to {filename}")
        print(f"   - Cookies: {len(auth_data['cookies'])}")
        print(f"   - LocalStorage keys: {len(auth_data['local_storage'])}")
        print(f"   - SessionStorage keys: {len(auth_data['session_storage'])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to save auth data: {e}")
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
        wait = WebDriverWait(driver, 10)
        
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
            
            # Wait for accounts table with "Ávöxtun" text
            print("Waiting for accounts table with 'Ávöxtun' to load...")
            
            try:
                wait = WebDriverWait(driver, 30)  # Increased timeout
                
                # Wait specifically for the element containing "Ávöxtun" text
                # This mimics Power Automate's approach: table[Id="accounts-table"] > tbody > tr > td[Text="Ávöxtun"]
                avoxtur_element = wait.until(
                    EC.presence_of_element_located((By.XPATH, "//table[@id='accounts-table']//tbody//tr//td[contains(text(), 'Ávöxtun')]"))
                )
                
                print(f"✅ Found 'Ávöxtun' element with text: '{avoxtur_element.text}'")
                print("✅ Login successful!")
                
                # Save all authentication data to file
                print("\n🔐 Saving authentication data...")
                save_auth_data(driver, "islandsbanki_auth.json")
                
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