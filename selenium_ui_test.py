import json
import os
import statistics
# import chromedriver_autoinstaller
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.action_chains import ActionChains

# chromedriver_autoinstaller.install()

options = Options()
options.add_argument('--headless') # Run browser in headless mode inside the github runner
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
    driver.implicitly_wait(5) # Waits for the page to load

    # Check whether a password has been provided and enter it if required
    if password:
        print("UI_PASSWORD environment variable present. Entering password.")
        password_input = driver.find_element(By.XPATH, '/html/body/div/div/div[2]/form/input[2]')
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)

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

    # Calculate the mean absolute deviation (MAD) of logo y positions
    mean_y = statistics.mean(y_coordinates)
    absolute_deviations = [abs(y - mean_y) for y in y_coordinates]
    mad = statistics.mean(absolute_deviations)
    mad_message = mad > 13 # Set mad_message if logos deviate too much out of alignment

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

    # Navigate to catalog page
    driver.get(f"{dashboard_base_url}/analysis")
    driver.implicitly_wait(5) # Wait for page to load

    map_canvas = driver.find_element(By.XPATH, '//*[@class="mapboxgl-canvas"]')

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
        driver.find_element(By.XPATH, '//*[contains(@class, "checkable__FormCheckableText")]')

    except NoSuchElementException:
        missing_datasets = True


    # Close the browser
    driver.quit()

    # Raise exception if any validation fails
    if missing_logos or missing_catalogs or mad_message or missing_datasets:
        raise PageValidationException(missing_logos=missing_logos, missing_catalogs=missing_catalogs, mad_message=mad_message, missing_datasets=missing_datasets)
    else:
        print("Validation successful. All elements are present.")

    
# Retry loop
max_retries = 3
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
