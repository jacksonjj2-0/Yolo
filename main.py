from datetime import datetime, timedelta, timezone
from helium import *
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver import ChromeOptions

# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--no-sandbox')
# chrome_options.add_argument('--headless')
# chrome_options.add_argument('--disable-gpu')
# chrome_options.add_argument('--disable-dev-shm-usage')
# chrome_options.add_argument("--window-size=1920,1080")
# driver = webdriver.Chrome(options=chrome_options)

# options = webdriver.ChromeOptions()
# options.add_argument("--incognito")
# options.add_argument("--headless")
options.binary_location = "/usr/bin/google-chrome" 

# driver = webdriver.Chrome(options=options)

options=ChromeOptions()
options.add_argument("--incognito")
options.add_argument("--headless")

start_chrome("https://www.fbil.org.in/#/home", options=options)

# Click random point on the page to scroll down

hey = print("hello")
# Scroll down to access table

    
