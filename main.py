import os
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/")
my_element = driver.find_element(By.XPATH, '//*[@id="main_navbar"]/ul/li[3]/a/span')
driver.implicitly_wait(3)
my_element.click()
text = driver.find_element(By.XPATH, '/html/body/div/main/div[2]/div/div/p[1]')
words = text.text
print(words)
