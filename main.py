import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# os.environ['PATH'] += r"/Users/chelblin/Drivers/Selenium/chromedriver_mac64/chromedriver"
driver = webdriver.Chrome()
driver.get("https://www.selenium.dev/")
my_element = driver.find_element(By.XPATH, '//*[@id="main_navbar"]/ul/li[3]/a/span')
# driver.implicitly_wait(3)
# my_element.click()
search_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//*[@id="docsearch"]/button/span[1]/span'))
)
search_button.click()

# Wait for the search box to become visible and interactable, then send 'Python'
search_box = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, '//*[@id="docsearch-input"]'))
)
search_box.send_keys('Python', Keys.ENTER)

input("Press Enter to close the script and the web page.")