#!/usr/bin/env python3

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.options import Keys

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

text = driver.find_element(By.XPATH, '//*[@id="app-container"]/div/div[2]/main/div[1]/div/div[2]/p')
words = text.text
print("Returned text: " + words)

# # Search for link to downloads page & wait for it to be clickable before clicking
# my_element = driver.find_element(By.XPATH, '//*[@id="main_navbar"]/ul/li[3]/a/span')
# driver.implicitly_wait(3)
# my_element.click()

# # Select a line of text and print it
# text = driver.find_element(By.XPATH, '/html/body/div/main/div[1]/section/div/div/div/p[1]')
# words = text.text
# print("Returned text: " + words)
