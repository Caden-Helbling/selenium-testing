import json
import os
import statistics
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains


options = Options()
options.add_argument('--headless')
options.add_argument('--window-size=1920x1080')  # Set window size

# Class to handle errors
class PageValidationException(Exception):
    def __init__(self, mad_message=None, missing_logos=None, missing_catalogs=None):
        self.mad_message = mad_message
        self.missing_logos = missing_logos
        self.missing_catalogs = missing_catalogs

    def __str__(self):
        message = "UI validation failed:\n"

        if self.missing_logos:
            message += "Missing logos:\n"
            for logo in self.missing_logos:
                message += f"  {logo}\n"

        if self.missing_catalogs:
            message += "Missing catalogs:\n"
            for catalog in self.missing_catalogs:
                message += f"  {catalog}\n"
        
        if self.mad_message:
            message += "Logos are out of alignment.\n"

        return message

# Function to perform the validation
def perform_validation(dashboard_base_url):
    # Set browser driver
    driver = webdriver.Chrome(options=options)
    # remove the tailing /
    dashboard_base_url = dashboard_base_url.rstrip('/')
    # Load webpage
    driver.get(dashboard_base_url) #"https://deploy-preview-13--ghg-demo.netlify.app/")
    driver.implicitly_wait(5) # Wait for page to load

    # Enter password and hit enter to sign in
    if password:
        print("UI_PASSWORD environment variable present. Entering password.")
        password_input = driver.find_element(By.XPATH, '/html/body/div/div/div[2]/form/input[2]')
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)

    
    driver.implicitly_wait(5) # Wait for page to load

    # Load data from .json
    with open('ui_data.json') as json_file:
        data = json.load(json_file)

    # Check for logos and their positions
    logo_src_list = data["logos"]

    missing_logos = []
    y_coordinates = []

    for src in logo_src_list:
        src = src.split("/")[-1].split(".")[0]
        image_elements = driver.find_elements(By.XPATH, f"//img[contains(@src, '{src}')]")
        if not image_elements:
            missing_logos.append(src)
        else:
            for image_element in image_elements:
                image_element_y = image_element.location['y']
                y_coordinates.append(image_element_y)

    print(y_coordinates)
    # Calculate the mean absolute deviation (MAD) of logo y positions
    mean_y = statistics.mean(y_coordinates)
    absolute_deviations = [abs(y - mean_y) for y in y_coordinates]
    mad = statistics.mean(absolute_deviations)
    mad_message = mad > 12 # Set mad_message if logos deviate too much out of alignment

    # Navigate to catalog page
    driver.get(f"{dashboard_base_url}/data-catalog")
    driver.implicitly_wait(5) # Wait for page to load

    # Check if catalogs are present
    catalog_list = data["catalogs"]
    missing_catalogs = []

    for catalog in catalog_list:
        try:
            title_element = driver.find_element(By.XPATH, f'//h3[contains(text(), "{catalog}")]')
        except NoSuchElementException:
            missing_catalogs.append(catalog)

    # Navigate to analysis page
    driver.get(f"{dashboard_base_url}/analysis")

    map_canvas = driver.find_element(By.XPATH, '//*[@id="mapbox-container"]/div/div[2]/canvas')
    driver.execute_script("arguments[0].scrollIntoView();", map_canvas)
    map_canvas_size = map_canvas.size
    map_canvas_location = map_canvas.location
    print(f'canvas size is {map_canvas_size}')
    print(f'canvas is located at {map_canvas_size}')

    corner_coordinates = [
    (map_canvas_location['x'] + 20, map_canvas_location['y'] + 20),
    (map_canvas_location['x'] + 80, map_canvas_location['y'] + 20),
    (map_canvas_location['x'] + 80, map_canvas_location['y'] + 80),
    (map_canvas_location['x'] + 20, map_canvas_location['y'] + 80)
    ]
    print(f'coordinates to click are {corner_coordinates}')

    # Perform the clicks
    actions = ActionChains(driver)

    # Simulate drawing the rectangle by performing mousedown, mousemove, and mouseup actions
    for x, y in corner_coordinates:
        actions.move_to_element_with_offset(map_canvas, x, y)
        actions.click_and_hold()
        actions.perform()
        actions.release()

    map_canvas.send_keys(Keys.ENTER)

    action_menu = driver.find_element(By.XPATH, '//*[@id="app-container"]/div/div[2]/main/div[3]/div/div[1]/div[2]/div/button')
    action_menu.click()

    action_menu_last10_year = driver.find_element(By.XPATH, '/html/body/div[10]/div/ul/li[4]/button')
    action_menu_last10_year.click()

    try:
        # Find the label element based on its attributes
        heading = driver.find_element(By.CLASS_NAME, 'Heading')
        check_boxes = driver.find_element(By.CLASS_NAME, 'checkable__FormCheckableText')
        print(heading)
        print(check_boxes)

        
        print("Check box element found on the webpage.")
    
    except NoSuchElementException:
        print("Label element not found on the webpage.")

    # Click on map
    # Click upload file button
    # Pass shapefile
    # Click date fields and set date range
    # Check for existence of dataset

    driver.quit()

    # Raise exception if any validation fails
    if missing_logos or missing_catalogs or mad_message:
        raise PageValidationException(mad_message=mad_message, missing_logos=missing_logos, missing_catalogs=missing_catalogs)
    else:
        print("Validation successful. All elements are present.")


# Retry loop
max_retries = 1
dashboard_base_url = os.getenv("DASHBOARD_BASE_URL")
password = os.getenv("PASSWORD")

for retry in range(max_retries):
    try:
        perform_validation(dashboard_base_url)
        break  # If validation is successful, break out of the loop
    except PageValidationException as e:
        if retry < max_retries - 1:
            print("Validation failed. Retrying...")
            continue
        else:
            # Max retries reached, raise the exception again
            raise e
