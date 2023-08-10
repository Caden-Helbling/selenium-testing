import json
import statistics
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# PATH = "/Users/chelblin/Downloads/chromedriver-mac-arm64/chromedriver"
options = Options()
# options.add_argument('--headless')
options.add_argument('--window-size=1920x1080')  # Set window size
# options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)

# Navigate to analysis page
driver.get("https://deploy-preview-13--ghg-demo.netlify.app/analysis")
driver.implicitly_wait(5) # Waits for the page to load

print("UI_PASSWORD environment variable present. Entering password.")
password_input = driver.find_element(By.XPATH, '//input[@name="password"]')
password_input.send_keys("partnership")
password_input.send_keys(Keys.ENTER)

time.sleep(3)

with open("/Users/chelblin/repos/selenium-testing/page.html", "w", encoding='utf-8') as f:
    f.write(driver.page_source)
map_canvas = driver.find_element(By.XPATH, '//*[@class="mapboxgl-canvas"]')
# driver.execute_script("arguments[0].scrollIntoView();", map_canvas)

corner_coordinates = [
    (-20, 20),
    (60, 20),
    (60, 60),
    (-20, 60)
]

actions = ActionChains(driver)
for x, y in corner_coordinates:
    actions.move_to_element_with_offset(map_canvas, x, y).click().perform()

map_canvas.send_keys(Keys.ENTER)

action_button = driver.find_element(By.XPATH, '//span[contains(text(), "Actions")]/following::button[contains(@class, "StyledButton")]')
driver.execute_script("arguments[0].click();", action_button)


driver.find_element(By.XPATH, '//li//button[contains(text(), "Last 10 years")]').click()

try:
    check_box = driver.find_element(By.XPATH, '//*[contains(@class, "checkable__FormCheckableText")]')
    print("Check box element found on the webpage.")

except NoSuchElementException:
    print("Label element not found on the webpage.")

    