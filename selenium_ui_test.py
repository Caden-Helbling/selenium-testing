import json
import os
import statistics
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

options = Options()
options.add_argument('--headless')

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

    # Enter password and hit enter to sign in
    if password:
        print("UI_PASSWORD environment variable present. Entering password.")
        password_input = driver.find_element(By.XPATH, '/html/body/div/div/div[2]/form/input[2]')
        password_input.send_keys(password)
        password_input.send_keys(Keys.ENTER)

    # Wait for page to load
    driver.implicitly_wait(5)

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

    # Calculate the mean of y-coordinates
    mean_y = statistics.mean(y_coordinates)

    # Calculate the absolute deviation of each y value from the mean
    absolute_deviations = [abs(y - mean_y) for y in y_coordinates]

    # Calculate the mean absolute deviation (MAD)
    mad = statistics.mean(absolute_deviations)

    print("Y-coordinates:", y_coordinates)
    print("Mean Absolute Deviation (MAD):", mad)

    if mad > -1:
        mad_message = "Out of alignment"

    # Navigate to catalog page
    driver.get(f"{dashboard_base_url}/data-catalog")

    # Check if catalogs are present
    catalog_list = data["catalogs"]
    missing_catalogs = []

    for catalog in catalog_list:
        try:
            title_element = driver.find_element(By.XPATH, f'//h3[contains(text(), "{catalog}")]')
        except NoSuchElementException:
            missing_catalogs.append(catalog)

    driver.quit()

    # Raise exception if any validation fails
    if missing_logos or missing_catalogs or mad_message:
        raise PageValidationException(mad_message=mad_message, missing_logos=missing_logos, missing_catalogs=missing_catalogs)
    else:
        print("Validation successful. All elements are present.")


# Number of retries
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
