#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

options = Options()
options.add_argument('--headless')

# Set browser driver
driver = webdriver.Chrome(options=options)

# Load webpage
driver.get("https://deploy-preview-13--ghg-demo.netlify.app/")

# Enter password and hit enter to sign in
password_input = driver.find_element(By.XPATH, '/html/body/div/div/div[2]/form/input[2]')
password_input.send_keys("partnership")
password_input.send_keys(Keys.ENTER)

driver.implicitly_wait(5)

# Check first paragraph text
text = driver.find_element(By.XPATH, '//*[@id="app-container"]/div/div[2]/main/div[2]/div/p[1]')
retrieved_text = text.text
expected_text = "Welcome to the U.S. GHG Center, your one-stop destination for all things related to greenhouse gas emissions! Our website offers a vast collection of datasets that are designed to help researchers, policymakers, and concerned citizens understand and mitigate the effects of climate change. Our team of experts has curated and compiled the most up-to-date and comprehensive data on greenhouse gas emissions from various sources, such as industry, transportation, and agriculture."

print("Returned text: " + retrieved_text)

if retrieved_text != expected_text:
    driver.quit()
    raise ValueError(f"The retrieved text '{retrieved_text}' does not match the expected value.")
else:
    print("Text matches the expected value.")

# Check logos
logo_elements = driver.find_elements(By.XPATH, "//img[@alt='EPA logo']")  # Replace 'Logo' with the alt text of the logo

if len(logo_elements) > 0:
    print("Logo is present on the page.")
else:
    print("Logo is not present on the page.")

driver.quit()
