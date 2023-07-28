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

text = driver.find_element(By.XPATH, '//*[@id="app-container"]/div/div[2]/main/div[2]/div/p[1]')
retrieved_text = text.text
expected_text = "Returned text: Welcome to the U.S. GHG Center, your one-stop destination for all things related to greenhouse gas emissions! Our website offers a vast collection of datasets that are designed to help researchers, policymakers, and concerned citizens understand and mitigate the effects of climate change. Our team of experts has curated and compiled the most up-to-date and comprehensive data on greenhouse gas emissions from various sources, such as industry, transportation, and agriculture."

print("Returned text: " + retrieved_text)

if retrieved_text != expected_text:
    driver.quit()
    raise ValueError(f"The retrieved text '{retrieved_text}' does not match the expected value.")
else:
    print("Text matches the expected value.")

driver.quit()

# # Search for link to downloads page & wait for it to be clickable before clicking
# my_element = driver.find_element(By.XPATH, '//*[@id="main_navbar"]/ul/li[3]/a/span')
# driver.implicitly_wait(3)
# my_element.click()

# # Select a line of text and print it
# text = driver.find_element(By.XPATH, '/html/body/div/main/div[1]/section/div/div/div/p[1]')
# words = text.text
# print("Returned text: " + words)
