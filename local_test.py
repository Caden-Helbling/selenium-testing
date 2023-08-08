import json
import statistics
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# PATH = "/Users/chelblin/Downloads/chromedriver-mac-arm64/chromedriver"
options = Options()
options.add_argument('--window-size=1920x1080')  # Set window size
options.add_experimental_option("detach", True)

driver = webdriver.Chrome(options=options)

# Navigate to analysis page
driver.get("https://deploy-preview-13--ghg-demo.netlify.app/analysis")

print("UI_PASSWORD environment variable present. Entering password.")
password_input = driver.find_element(By.XPATH, '/html/body/div/div/div[2]/form/input[2]')
password_input.send_keys("partnership")
password_input.send_keys(Keys.ENTER)

    
driver.implicitly_wait(1) # Wait for page to load

map_canvas = driver.find_element(By.CLASS_NAME, 'mapboxgl-canvas')
driver.execute_script("arguments[0].scrollIntoView();", map_canvas)
map_canvas_size = map_canvas.size
map_canvas_location = map_canvas.location
print(f'canvas size is {map_canvas_size}')
print(f'canvas is located at {map_canvas_location}')

corner_coordinates = [
(map_canvas_location['x'] + 40, map_canvas_location['y'] + 40),
(map_canvas_location['x'] + 160, map_canvas_location['y'] + 40),
(map_canvas_location['x'] + 160, map_canvas_location['y'] + 160),
(map_canvas_location['x'] + 40, map_canvas_location['y'] + 160)
]
print(f'coordinates to click are {corner_coordinates} {map_canvas_location}')

# Perform the clicks
actions = ActionChains(driver)

# Simulate drawing the rectangle by performing mousedown, mousemove, and mouseup actions
for x, y in corner_coordinates:
    actions.move_to_element_with_offset(map_canvas, x, y).click().perform()

# map_canvas.send_keys(Keys.ENTER)

action_menu = driver.find_element(By.XPATH, '//*[@id="app-container"]/div/div[2]/main/div[3]/div/div[1]/div[2]/div/button')
action_menu.click()

action_menu_last10_year = driver.find_element(By.XPATH, '/html/body/div[10]/div/ul/li[4]/button')
action_menu_last10_year.click()

try:
    # Find the label element based on its attributes
    form_input = driver.find_element(By.XPATH, '//*[contains(@class, "input__FormInput")]')
    print(form_input)
    check_box = driver.find_element(By.XPATH, '//*[contains(@class, "checkable_FormCheckable")]')
    print(check_box)

    
    print("Check box element found on the webpage.")

except NoSuchElementException:
    print("Label element not found on the webpage.")