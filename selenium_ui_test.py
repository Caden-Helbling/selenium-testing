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
# options.add_experimental_option("detach", True) # For testing. Keeps the browser window open
options.add_argument('--headless') # Run browser in headless mode inside the github runner
driver = webdriver.Chrome(options=options) # Set browser drive and pass options set above
driver.set_window_size(1920,1080)
driver.implicitly_wait(3) # Wait for element to load before throwing an error

# Load data from ui_data.json
with open('ui_data.json') as json_file:
    data = json.load(json_file)

class PageValidationException(Exception):
    def __init__(self, mad_message=None, missing_logos=None, missing_catalogs=None, missing_datasets=None, missing_map_datasets=None):
        self.mad_message = mad_message
        self.missing_logos = missing_logos
        self.missing_catalogs = missing_catalogs
        self.missing_datasets = missing_datasets
        self.missing_map_datasets = missing_map_datasets

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

        if self.missing_map_datasets:
            message += "Map datasets are not being generated properly.\n"

        return message

def password_input():
    try:
        # print("UI_PASSWORD environment variable present. Entering password.\n")
        password_input = driver.find_element(By.XPATH, '//input[@name="password"]')
        password_input.send_keys(ui_password)
        password_input.send_keys(Keys.ENTER)
    except NoSuchElementException as e:
        # print("No password needed on this attempt \n")
        pass

def save_page():
    # Get the current URL
    current_url = driver.current_url

    # Remove '.app' from the end of the URL if it's present
    if current_url.endswith('.app'):
        current_url = current_url[:-4]

    # Extract the directory name from the URL (e.g., example.com)
    directory_name = current_url.split("//")[1].split("/")[0]

    # Create the directory if it doesn't exist
    output_dir = os.environ["OUTPUT_DIR"]
    directory_path = os.path.join(output_dir, directory_name)
    os.makedirs(directory_path, exist_ok=True)

    # Save the HTML source to a file within the directory
    filename = "page.html"
    file_path = os.path.join(directory_path, filename)
    print("filepath is below:")
    print(file_path)
    html_source = driver.page_source
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(html_source)
    
    # html_source = driver.page_source
    # with open("page.html", "w", encoding="utf-8") as file:
    #     file.write(html_source)

def logo_validation(dashboard_base_url):
    # dashboard_base_url = dashboard_base_url.rstrip('/') # remove the tailing /
    driver.get(dashboard_base_url) # Load webpage "https://deploy-preview-13--ghg-demo.netlify.app/")

    # Check whether a ui_password has been provided and enter it if required
    if ui_password:
        password_input()

    # Check main page for logos containing source match in ui_data.json
    logo_src_list = data["logos"]
    missing_logos = []
    y_coordinates = []

    for src in logo_src_list:
        src = src.split("/")[-1].split(".")[0]
        image_elements = driver.find_elements(By.XPATH, f"//img[contains(@src, '{src}')]")
        if not image_elements:
            missing_logos.append(src)
            save_page()
            raise PageValidationException(missing_logos=missing_logos)
        else:
            for image_element in image_elements:
                image_element_y = image_element.location['y']
                y_coordinates.append(image_element_y)

    # Calculate the mean absolute deviation (MAD) of logo y positions
    mean_y = statistics.mean(y_coordinates)
    absolute_deviations = [abs(y - mean_y) for y in y_coordinates]
    mad = statistics.mean(absolute_deviations)
    if mad > 13:
        mad_message = True
        raise PageValidationException(mad_message=mad_message)

def catalog_verification(dashboard_base_url):
    # Check the catalog page for catalogs matching those in ui_test.json
    driver.get(f"{dashboard_base_url}/data-catalog")

    # Check whether a ui_password has been provided and enter it if required
    if ui_password:
        password_input()

    catalog_list = data["catalogs"]
    missing_catalogs = []

    for catalog in catalog_list:
        try:
            driver.find_element(By.XPATH, f'//h3[contains(text(), "{catalog}")]')
        except NoSuchElementException:
            missing_catalogs.append(catalog)
            raise PageValidationException(missing_catalogs=missing_catalogs)

def dataset_verification(dashboard_base_url):
    # Check the analysis page for datasets
    driver.get(f"{dashboard_base_url}/analysis")

    # Check whether a ui_password has been provided and enter it if required
    if ui_password:
        password_input()

    map_canvas = driver.find_element(By.XPATH, '//canvas[@class="mapboxgl-canvas"]')

    # Generate coordinates for corners of the rectangle to be drawn on the map
    corner_coordinates = [
        (-20, 20),
        (60, 20),
        (60, 60),
        (-20, 60)
    ]

    # Click to create the rectangle one the map
    time.sleep(3) # Give time for map to fully load and be clickable
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
    try:
        checkable_form = driver.find_element(By.XPATH, '//*[contains(@class, "checkable__FormCheckableText")]')
        driver.execute_script("arguments[0].scrollIntoView();", checkable_form)
        checkable_form.click()
    except NoSuchElementException:
        missing_datasets = True
        raise PageValidationException(missing_datasets=missing_datasets)

    # Generate data sets by clicking generate button
    time.sleep(3)
    driver.find_element(By.XPATH, '//a[contains(@class, "Button__StyledButton")]').click()

    # Check that dataset loads
    time.sleep(3)
    try:
        driver.find_element(By.XPATH, '//p[contains(text(), "failed")]')
        missing_map_datasets = True

        # Get the current HTML source code of the page and save to a file
        save_page() 

        raise PageValidationException(missing_map_datasets=missing_map_datasets)
    except NoSuchElementException:
        pass

# Retry loop
max_retries = 3
dashboard_base_url = os.getenv("DASHBOARD_BASE_URL").rstrip('/') # remove the tailing /
ui_password = os.getenv("PASSWORD")

for retry in range(max_retries):
    try:
        logo_validation(dashboard_base_url)
        catalog_verification(dashboard_base_url)
        dataset_verification(dashboard_base_url)
        break  # If validation is successful, break out of the loop
    except PageValidationException as e:
        if retry < max_retries - 1:
            continue
        else:
            raise e 

print("Validation successful! All elements found.")
driver.quit()
