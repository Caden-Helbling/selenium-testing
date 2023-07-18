import os
from selenium import webdriver
from selenium.webdriver.common.by import By

# Set browser driver
driver = webdriver.Chrome()

# Load webpage
driver.get("https://www.selenium.dev/")

# Search for link to downloads page & wait for it to be clickable before clicking
my_element = driver.find_element(By.XPATH, '//*[@id="main_navbar"]/ul/li[3]/a/span')
driver.implicitly_wait(3)
my_element.click()

# Select a line of text and print it
text = driver.find_element(By.XPATH, '/html/body/div/main/div[2]/div/div/p[1]')
words = text.text
print(words)
