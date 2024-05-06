from datetime import datetime, timedelta, timezone
from helium import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ChromeOptions


chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--headless')
chrome_options.add_argument('--disable-gpu')
chrome_options.add_argument('--disable-dev-shm-usage')
chrome_options.add_argument("--window-size=1920,1080")
# driver = webdriver.Chrome(options=chrome_options)

# options = webdriver.ChromeOptions()
# options.add_argument("--incognito")
# options.add_argument("--headless")

# driver = webdriver.Chrome(options=options)

options=ChromeOptions()
options.add_argument("--incognito")
options.add_argument("--headless")

start_chrome("https://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/euro_short-term_rate/html/index.en.html", headless=True)


# Click random point on the page to scroll down

hey = print("hello")
# Scroll down to access table
