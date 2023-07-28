import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

options = Options()
options.add_argument('--headless')

# Class to handle errors
class PageValidationException(Exception):
    def __init__(self, missing_logos=None, missing_catalogs=None, text_mismatch=None):
        self.missing_logos = missing_logos
        self.missing_catalogs = missing_catalogs
        self.text_mismatch = text_mismatch

    def __str__(self):
        message = "Page validation failed:\n"

        if self.missing_logos:
            message += "Missing logos:\n"
            for logo in self.missing_logos:
                message += f"  {logo}\n"

        if self.missing_catalogs:
            message += "Missing catalogs:\n"
            for catalog in self.missing_catalogs:
                message += f"  {catalog}\n"

        if self.text_mismatch:
            message += "Text mismatch:\n"
            message += f"Retrieved text: {self.text_mismatch[0]}\n"
            message += f"Expected text: {self.text_mismatch[1]}\n"

        return message
    
# Set browser driver
driver = webdriver.Chrome(options=options)

# Load webpage
driver.get("https://deploy-preview-13--ghg-demo.netlify.app/")

# Enter password and hit enter to sign in
password_input = driver.find_element(By.XPATH, '/html/body/div/div/div[2]/form/input[2]')
password_input.send_keys("partnership")
password_input.send_keys(Keys.ENTER)

# Wait for page to load
driver.implicitly_wait(5)

# Load data from .json
with open('ui_data.json') as json_file:
    data = json.load(json_file)

# Check first paragraph text
text = driver.find_element(By.XPATH, '//*[@id="app-container"]/div/div[2]/main/div[2]/div/p[1]')
retrieved_text = text.text
expected_text = data["text"]

# Check logos
# List of image src URLs to check
logo_src_list = data["logos"]

missing_logos = []

# Check if each image is present on the page
for src in logo_src_list:
    image_element = driver.find_elements(By.XPATH, f"//img[@src='{src}']")
    if not image_element:
        missing_logos.append(src)

driver.get("https://deploy-preview-13--ghg-demo.netlify.app/data-catalog")

catalog_list = data["catalogs"]
missing_catalogs = []

for catalog in catalog_list:
    try:
        title_element = driver.find_element(By.XPATH, f'//h3[contains(text(), "{catalog}")]')
    except NoSuchElementException:
        missing_catalogs.append(catalog)

driver.quit()

# Raise exception if any validation fails
if retrieved_text != expected_text or missing_logos or missing_catalogs:
    raise PageValidationException(missing_logos=missing_logos, missing_catalogs=missing_catalogs, text_mismatch=None if retrieved_text == expected_text else (retrieved_text, expected_text))
else:
    print("Validation successful. All elements are present on the page.")
