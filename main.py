import csv
import os
import urllib.request

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import Keys


house = "https://www.ilga.gov/house/"
senate = "https://www.ilga.gov/senate/"

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

def get_data(url, side):
    driver.get(url)
    spans = driver.find_elements(By.XPATH, "//table//span")
    for span in spans:
        if f"Current {side} Members" in span.text:
            break
    table = span.find_elements(By.XPATH, "../../../..")[0]
    rows = table.find_elements(By.TAG_NAME, 'tr')
    data = []

    # this takes about 10-15 seconds
    for row in rows[2:]:  # skip first two
        name, bills, committees, district, party = row.find_elements(By.TAG_NAME, 'td')
        title = ''
        if len(driver.find_elements(By.XPATH, "//*[(text()='District')]/following-sibling::span")):
            title = driver.find_element(By.XPATH, "//*[(text()='District')]/following-sibling::span").text
        data.append({
            "side": side,
            "name": name.text,
            "page_link": name.find_element(By.TAG_NAME, 'a').get_attribute('href'),
            "bills": bills.find_element(By.TAG_NAME, 'a').get_attribute('href'),
            "committees": committees.find_element(By.TAG_NAME, 'a').get_attribute('href'),
            "district": district.text,
            "party": party.text,
            "title": title,
        })
    return data

house_data = get_data(house, "House")
senate_data = get_data(senate, "Senate")

os.makedirs("house", exist_ok=True)
for record in house_data:
    driver.get(record['page_link'])
    src = driver.find_element(By.CSS_SELECTOR, '[alt*="Photograph"]').get_attribute("src")
    fn = record.get('name').replace(' ', '-').replace('.', '').replace(',', '').lower()
    urllib.request.urlretrieve(src, f"house/{fn}.jpg")
    record['image_url'] = src
    record['saved_image'] = f"house/{fn}.jpg"

os.makedirs("senate", exist_ok=True)
for record in senate_data:
    driver.get(record['page_link'])
    src = driver.find_element(By.CSS_SELECTOR, '[alt*="Photograph"]').get_attribute("src")
    fn = record.get('name').replace(' ', '-').replace('.', '').replace(',', '').lower()
    urllib.request.urlretrieve(src, f"senate/{fn}.jpg")
    record['image_url'] = src
    record['saved_image'] = f"senate/{fn}.jpg"

# write the data
with open("output.csv", "w") as f:
    writer = csv.DictWriter(f, fieldnames=senate_data[0].keys())
    writer.writeheader()
    for row in senate_data:
        writer.writerow(row)
    for row in house_data:
        writer.writerow(row)
