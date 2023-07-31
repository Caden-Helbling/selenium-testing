# Selenium UI Testing

This workflow is for UI testing the GHGC website using selenium.

# Usage

To use this workflow as part of a larger workflow, first update the ui_data.json file to include the following:

- A list of src links for logos you would like to check exist on the main page
- A list of catalog titles you would like to check exist on the catalogs page (Partial titles are OK)

# Output

UI testing passes with a "Validation successful. All elements are present." message if all elements provided in the ui_data.json file are located.
If the test fails a list of missing elements will be provided.