from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

options = Options()
options.add_argument('--headless')

# Set browser driver
driver = webdriver.Chrome(options=options)

# Load webpage
driver.get("https://deploy-preview-13--ghg-demo.netlify.app/")

# Enter password and hit enter to sign in
password_input = driver.find_element(By.XPATH, '/html/body/div/div/div[2]/form/input[2]')
password_input.send_keys("partnership")
password_input.send_keys(Keys.ENTER)

driver.implicitly_wait(5)

# Check first paragraph text
text = driver.find_element(By.XPATH, '//*[@id="app-container"]/div/div[2]/main/div[2]/div/p[1]')
retrieved_text = text.text
expected_text = "Welcome fake to the U.S. GHG Center, your one-stop destination for all things related to greenhouse gas emissions! Our website offers a vast collection of datasets that are designed to help researchers, policymakers, and concerned citizens understand and mitigate the effects of climate change. Our team of experts has curated and compiled the most up-to-date and comprehensive data on greenhouse gas emissions from various sources, such as industry, transportation, and agriculture."

# Check logos
# List of image src URLs to check
logo_src_list = [
    "https://deploy-preview-13--ghg-demo.netlify.app/epa.17d0873a.svg",
    "https://deploy-preview-13--ghg-demo.netlify.app/nasa.5cf6faef.png",
    "https://deploy-preview-13--ghg-demo.netlify.app/nist.13219e63.png",
    "https://deploy-preview-13--ghg-demo.netlify.app/noaa.df5d210a.png",
    # "https://deploy-preview-13--ghg-demo.netlify.app/fake.df5d210a.png"
    # Add more image URLs as needed
]

class PageValidationException(Exception):
    def __init__(self, missing_logos=None, text_mismatch=None):
        self.missing_logos = missing_logos
        self.text_mismatch = text_mismatch

    def __str__(self):
        message = "Page validation failed:\n"

        if self.missing_logos:
            message += "Missing logos:\n"
            for logo in self.missing_logos:
                message += f"  {logo}\n"

        if self.text_mismatch:
            message += "Text mismatch:\n"
            message += f"Retrieved text: {self.text_mismatch[0]}\n"
            message += f"Expected text: {self.text_mismatch[1]}\n"

        return message

missing_logos = []

# Check if each image is present on the page
for src in logo_src_list:
    image_element = driver.find_elements(By.XPATH, f"//img[@src='{src}']")
    if not image_element:
        missing_logos.append(src)

driver.quit()

# Raise exception if any validation fails
if retrieved_text != expected_text or missing_logos:
    raise PageValidationException(missing_logos=missing_logos, text_mismatch=None if retrieved_text == expected_text else (retrieved_text, expected_text))
else:
    print("Validation successful. All elements are present on the page.")
