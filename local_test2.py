import json
import os
import statistics
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

options = Options()
# options.add_argument('--headless') # Run browser in headless mode inside the github runner
options.add_argument('--window-size=1920x1080')  # Set window size

class PageValidationException(Exception):
    def __init__(self, mad_message=None, missing_logos=None, missing_catalogs=None, missing_datasets=None):
        self.mad_message = mad_message
        self.missing_logos = missing_logos
        self.missing_catalogs = missing_catalogs
        self.missing_datasets = missing_datasets

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

        if self.missing_datasets:
            message += "Datasets are not appearing on analysis page.\n"

        return message

def perform_validation(dashboard_base_url):
    driver = webdriver.Chrome(options=options) # Set browser drive and pass options set above
    dashboard_base_url = dashboard_base_url.rstrip('/') # remove the tailing /
    driver.get(dashboard_base_url) # Load webpage "https://deploy-preview-13--ghg-demo.netlify.app/")
    driver.implicitly_wait(3) # Wait for element to load before throwing an error

    # Check whether a password has been provided and enter it if required
    if password:
        print("UI_PASSWORD environment variable present. Entering password.")
        password_input = driver.find_element(By.XPATH, '//input[@name="password"]')
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)

    # Load data from ui_data.json
    with open('ui_data.json') as json_file:
        data = json.load(json_file)

    # Check main page for logos containing source match in ui_data.json
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
    mad_message = mad > 13 # Set mad_message if logos deviate too much out of alignment

    # Check the catalog page for catalogs matching those in ui_test.json
    driver.get(f"{dashboard_base_url}/data-catalog")

    catalog_list = data["catalogs"]
    missing_catalogs = []

    for catalog in catalog_list:
        try:
            title_element = driver.find_element(By.XPATH, f'//h3[contains(text(), "{catalog}")]')
        except NoSuchElementException:
            missing_catalogs.append(catalog)

    # Check the analysis page for datasets
    driver.get(f"{dashboard_base_url}/analysis")
    time.sleep(3) # Give time for map to fully load and be clickable
    map_canvas = driver.find_element(By.XPATH, '//*[@class="mapboxgl-canvas"]')

    # Generate coordinates for corners of the rectangle to be drawn on the map
    corner_coordinates = [
        (-20, 20),
        (60, 20),
        (60, 60),
        (-20, 60)
    ]

    # Click to create the rectangle one the map
    actions = ActionChains(driver)
    for x, y in corner_coordinates:
        actions.move_to_element_with_offset(map_canvas, x, y).click().perform()

    # Press enter after drawing map to signal completion of polygon
    map_canvas.send_keys(Keys.ENTER)

    # Expand the actions drop down and select 10 years
    action_button = driver.find_element(By.XPATH, '//span[contains(text(), "Actions")]/following::button[contains(@class, "StyledButton")]')
    driver.execute_script("arguments[0].click();", action_button)
    driver.find_element(By.XPATH, '//li//button[contains(text(), "Last 10 years")]').click()

    # Check that datasets exist
    missing_datasets = False
    try:
        driver.find_element(By.XPATH, '//*[contains(@class, "checkable__FormCheckableText")]')
    except NoSuchElementException:
        missing_datasets = True

    # Raise exception if any validation fails
    if missing_logos or missing_catalogs or mad_message or missing_datasets:
        raise PageValidationException(missing_logos=missing_logos, missing_catalogs=missing_catalogs, mad_message=mad_message, missing_datasets=missing_datasets)
    else:
        print("Validation successful. All elements are present.")

    # Close the browser
    driver.quit()

# Retry loop
max_retries = 3
dashboard_base_url = "https://deploy-preview-13--ghg-demo.netlify.app/"
password = "partnership"

for retry in range(max_retries):
    try:
        perform_validation(dashboard_base_url)
        break  # If validation is successful, break out of the loop
    except PageValidationException as e:
        if retry < max_retries - 1:
            print(e)
            print("Validation failed. Retrying...\n")
            continue
        else:
            # Max retries reached, raise the exception again
            raise e
