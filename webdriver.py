from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import time
import logging

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
            
            # Wait a bit to see the result
            time.sleep(3)
            
            # Wait for web page content - accounts table with "Ávöxtun" text
            print("Waiting for accounts table with 'Ávöxtun' to load...")
            try:
                avoxtur_element = wait.until(EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "table[id='accounts-table'] > tbody > tr > td")
                ))
                print("Found accounts table!")
                
                # Now look specifically for the Ávöxtun cell
                avoxtur_cell = driver.find_element(By.CSS_SELECTOR, "table[id='accounts-table'] > tbody > tr > td")
                if "Ávöxtun" in avoxtur_cell.text:
                    print("Found 'Ávöxtun' element!")
                else:
                    print(f"Found table cell but text was: '{avoxtur_cell.text}'")
            except:
                print("Could not find 'Ávöxtun' element")
            
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
    login_to_islandsbanki()