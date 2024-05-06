from flask import Flask, request, jsonify
from datetime import datetime, timedelta, timezone
from helium import *
import time
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver import ChromeOptions


options = webdriver.ChromeOptions()
options=ChromeOptions()
options.add_argument("--incognito")
options.add_argument("--headless")
# Assuming ChromeDriver is in the PATH or specified with webdriver.Chrome(executable_path=...)

# options = Options()
options.add_argument("--no-sandbox")  # Bypass OS security model
options.add_argument("--disable-dev-shm-usage")  # Overcome limited resource problems
options.add_argument("--disable-gpu")  #
options.add_argument("--no-sandbox")
# options.add_argument('--headless')
# options.add_argument('--disable-gpu')
# options.add_argument('--disable-dev-shm-usage')
# options.add_argument("--window-size=1920,1080")
# driver = webdriver.Chrome(options=options)


print("Execution Started")

app = Flask(__name__)

Holiday = "After 5 tries, the dates do not match. It might be a holiday."
# Define the variable curve_fail --- for instances where the date is not there
curve_fail = "Dates do not match. Please retry in 1 hour or it might be a holiday"

# Define function to log requests
def log_request(request):
    print("Received request:", request.json)
# Element to return when nothing is found and probable error
elementnoneError = ("Element not found at specified location")

def get_yesterday_date():
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days=1)

    # If yesterday was Sunday, return the date of three days ago
    if yesterday.weekday() == 6:  # Sunday
        three_days_ago = today - timedelta(days=3)
        return three_days_ago.strftime("%d-%m-%Y")
    else:
        return yesterday.strftime("%d-%m-%Y")


# Function to fetch EuroEstr rate
def fetch_euroestr_rate():
    retry_count = 0
    max_retries = 5
    estr_rate = None
    
    while retry_count < max_retries:
        start_chrome("https://www.ecb.europa.eu/stats/financial_markets_and_interest_rates/euro_short-term_rate/html/index.en.html", headless=True)

        if Text('Our website uses cookies').exists():
            click('I understand and I accept the use of cookies')

        click(Point(200, 300))
        press(PAGE_DOWN)

        date_element = find_all(S('//*[@id="main-wrapper"]/main/div[3]/div[2]/table/tbody/tr[2]/td'))

        if date_element:
            table_date = date_element[0].web_element.text.strip()
            yesterday_date = get_yesterday_date()
            print(yesterday_date)
            if table_date == yesterday_date:
                estr_rate_element = find_all(S('//*[@id="main-wrapper"]/main/div[3]/div[2]/table/tbody/tr[1]/td'))

                if estr_rate_element:
                    estr_rate_value = estr_rate_element[0].web_element.text.strip()
                    estr_rate = float(estr_rate_value)
                    kill_browser()
                    return estr_rate
                     
            else:
                print("Yesterday's EuroEstr date not found in the table. Retrying in one hour.")
                kill_browser()
                return curve_fail
                
                
        else:
            print("Element EuroEstr not found at the specified location.")
            print(elementnoneError)

    
#Function to Find Date for SOFR
def sofr_yesterday_date():
    today = datetime.now(timezone.utc)
    yesterday = today - timedelta(days=1)

    # If yesterday was Sunday, return the date of three days ago
    if yesterday.weekday() == 6:  # Sunday
        three_days_ago = today - timedelta(days=3)
        return three_days_ago.strftime("%m/%d")
    else:
        return yesterday.strftime("%m/%d")



# Function to fetch SOFR rate
def fetch_sofr_rate():
    retry_count = 0
    max_retries = 5
    sofr_rate = None
    
    while retry_count < max_retries:
        start_chrome("https://www.newyorkfed.org/markets/reference-rates/sofr", headless=True)
        click("Resources")
        press(PAGE_DOWN)
        click("DATE")

        date_element = find_all(S('//*[@id="pr_id_1-table"]/tbody/tr[1]/td[1]'))

        if date_element:
            table_date = date_element[0].web_element.text.strip()
            yesterday_date = sofr_yesterday_date()

            if table_date == yesterday_date:
                sof_rate_element = find_all(S('//*[@id="pr_id_1-table"]/tbody/tr[1]/td[2]'))

                if sof_rate_element:
                    sof_rate_value = sof_rate_element[0].web_element.text.strip()
                    sofr_rate = float(sof_rate_value)
                    kill_browser()
                    return sofr_rate
            else:
                print("Yesterday's SOFR date not found in the table.")
                kill_browser()
                return curve_fail
                
                
        else:
            print("Element Sofr not found at the specified location.")
            return(elementnoneError)

    
#Function to find Date For MIBOR
def mibor_yesterday_date():
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    # If yesterday was Sunday, return the date of ten days ago
    if yesterday.weekday() == 6:  # Sunday
        ten_days_ago = today - timedelta(days=10)
        return ten_days_ago.strftime("%d %b %Y")
    else:
        return yesterday.strftime("%d %b %Y")
# options = webdriver.ChromeOptions()
# options.add_argument("--incognito")
# options.add_argument("--headless")

# driver = webdriver.Chrome(options=options)




# Main function to check yesterday's rate
def fetch_mibor_rate():
    
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        # Start chrome and open URL
        # start_chrome("https://www.fbil.org.in/#/home", headless=True)
        start_chrome("https://www.fbil.org.in/#/home", options=options)
        print("done")
        # Click random point on the page to scroll down
        click('MONEY MARKET/INTEREST RATES')
       

        # Find the element at the specified XPath location for date
        date_element = find_all(S('//*[@id="MIBOR"]/tbody/tr[1]/td[1]/div'))

        # If the date element is found
        if date_element:
            # Get the text value of the element
            table_date = date_element[0].web_element.text.strip()
           
            # Get yesterday's date
            yesterday_date = mibor_yesterday_date()
          
            # Compare the dates
            if table_date == yesterday_date:
                # Find the element at the specified XPath location for EstR rate
                estr_rate_element = find_all(S('//*[@id="MIBOR"]/tbody/tr[1]/td[4]'))
                # If the Estr rate element is found
                if estr_rate_element:
                    # Extract the Estr rate value
                    estr_rate_value = estr_rate_element[0].web_element.text.strip()
                    mibor_rate = float(estr_rate_value)
                    kill_browser()
                    return mibor_rate
            else:
                # If dates don't match, wait for one hour before retrying
                print("Yesterday's Mibor date not found in the table.")
                kill_browser()
                return curve_fail
                
        else:
            print("Element Mibor not found at the specified location.")
            return(elementnoneError)


# USDINR Spot Code Part

# Main function to check yesterday's rate
def fetch_USDINR_Spot():
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        # Start chrome and open URL
        start_chrome("https://www.fbil.org.in/#/home", options=options)

        if Text('Our website uses cookies').exists():
          click('I understand and I accept the use of cookies')

        # Click random point on the page to scroll down
        click('DERIVATIVES')
       
        press(PAGE_DOWN)

        # Find the element at the specified XPath location for date
        date_element = find_all(S('//*[@id="Premia"]/tbody/tr[16]/td[1]/div'))

        # If the date element is found
        if date_element:
            # Get the text value of the element
            table_date = date_element[0].web_element.text.strip()
           
            # Get yesterday's date
            yesterday_date = mibor_yesterday_date()
          
            # Compare the dates
            if table_date == yesterday_date:
                # Find the element at the specified XPath location for EstR rate
                estr_rate_element = find_all(S('//*[@id="Premia"]/tbody/tr[16]/td[6]'))
                # If the Estr rate element is found
                if estr_rate_element:
                    # Extract the Estr rate value
                    estr_rate_value = estr_rate_element[0].web_element.text.strip()
                    spot_rate = float(estr_rate_value)
                    kill_browser()
                    return spot_rate
            else:
                # If dates don't match, wait for one hour before retrying
                print("Yesterday's USDINR SPOT date not found in the table.")
                kill_browser()
                return curve_fail
                
        else:
            print("Element USDINR SPOT not found at the specified location.")
            return(elementnoneError)
            

# USDINR 6M Code

# Main function to check yesterday's rate
def fetch_6M():
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        # Start chrome and open URL
        start_chrome("https://www.fbil.org.in/#/home", options=options)

        if Text('Our website uses cookies').exists():
          click('I understand and I accept the use of cookies')

        # Click random point on the page to scroll down
        click('DERIVATIVES')
       
        press(PAGE_DOWN)

        # Find the element at the specified XPath location for date
        date_element = find_all(S('//*[@id="Premia"]/tbody/tr[7]/td[1]/div'))

        # If the date element is found
        if date_element:
            # Get the text value of the element
            table_date = date_element[0].web_element.text.strip()
           
            # Get yesterday's date
            yesterday_date = mibor_yesterday_date()
          
            # Compare the dates
            if table_date == yesterday_date:
                # Find the element at the specified XPath location for EstR rate
                estr_rate_element = find_all(S('//*[@id="Premia"]/tbody/tr[7]/td[5]'))
                # If the Estr rate element is found
                if estr_rate_element:
                    # Extract the Estr rate value
                    estr_rate_value = estr_rate_element[0].web_element.text.strip()
                    SixM_rate = float(estr_rate_value)
                    kill_browser()
                    return SixM_rate
            else:
                # If dates don't match, wait for one hour before retrying
                print("Yesterday's USDINR 6M date not found in the table.")
                kill_browser()
                return curve_fail
                
        else:
            print("Element USDINR 6M not found at the specified location.")
            return (elementnoneError)

# ModMifor Code PArt

# Main function to check yesterday's rate
def fetch_mifor():
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        # Start chrome and open URL
        start_chrome("https://www.fbil.org.in/#/home", options=options)

        if Text('Our website uses cookies').exists():
          click('I understand and I accept the use of cookies')

        # Click random point on the page to scroll down
        click('DERIVATIVES')
        click('MODIFIED MIFOR')
        time.sleep(1)
        

        # Find the element at the specified XPath location for date
        date_element = find_all(S('//*[@id="MODIFIEDMIFOR"]/tbody/tr[5]/td[1]/div'))

        # If the date element is found
        if date_element:
            # Get the text value of the element
            table_date = date_element[0].web_element.text.strip()
           
            # Get yesterday's date
            yesterday_date = mibor_yesterday_date()
          
            # Compare the dates
            if table_date == yesterday_date:
                # Find the element at the specified XPath location for EstR rate
                estr_rate_element = find_all(S('//*[@id="MODIFIEDMIFOR"]/tbody/tr[5]/td[6]/div'))
                # If the Estr rate element is found
                if estr_rate_element:
                    # Extract the Estr rate value
                    estr_rate_value = estr_rate_element[0].web_element.text.strip()
                    mifor_rate = float(estr_rate_value)
                    kill_browser()
                    return mifor_rate
            else:
                # If dates don't match, wait for one hour before retrying
                print("Yesterday's MIFOR date not found in the table.")
                kill_browser()
                return curve_fail
                
        else:
            print("Element MIFOR not found at the specified location.")
            return(elementnoneError)

def tonar_yesterday_date():
    today = datetime.now()
    yesterday = today - timedelta(days=1)

    # If yesterday was Sunday, return the date of three days ago
    if yesterday.weekday() == 6:  # Sunday
        three_days_ago = today - timedelta(days=3)
        return three_days_ago.strftime("%a, %d %b %Y")
    else:
        return yesterday.strftime("%a, %d %b %Y")


# Main function to check yesterday's rate
def fetch_tonar_rate():
    retry_count = 0
    max_retries = 5
    while retry_count < max_retries:
        # Start chrome and open URL
        start_chrome("https://www.realisedrate.com/TONAR", headless=True)

        if Text('We care about your privacy').exists():
          click('Allow All Cookies')
        time.sleep(6)

        # Find the element at the specified XPath location for date
        date_element = find_all(S('//*[@id="react-tabs-7"]/div/div/div[2]/table/tbody/tr[1]/td[2]/div/div/div'))

        # If the date element is found
        if date_element:
            # Get the text value of the element
            table_date = date_element[0].web_element.text.strip()
            
            # Get yesterday's date
            yesterday_date = tonar_yesterday_date()
            print(yesterday_date)
            # Compare the dates
            if table_date == yesterday_date:
                # Find the element at the specified XPath location for EstR rate
                estr_rate_element = find_all(S('//*[@id="react-tabs-7"]/div/div/div[2]/table/tbody/tr[1]/td[4]/div/div[1]'))
                # If the Estr rate element is found
                if estr_rate_element:
                    # Extract the Estr rate value
                    estr_rate_value = estr_rate_element[0].web_element.text.strip()
                    tonar_rate = float(estr_rate_value)
                    kill_browser()
                    return tonar_rate
                    
            else:
                # If dates don't match, wait for one hour before retrying
                print("Yesterday's TONAR date not found in the table. ")
                kill_browser()
                return curve_fail
        else:
            print("Element TONAR not found at the specified location.")
            return(elementnoneError)
    

# Endpoint to fetch rates for specific assets
@app.route('/fetch_rates', methods=['POST'])
def fetch_rates():
    # Log the request
    log_request(request)
    # Get the requested assets from the request body
    data = request.get_json()
    assets = data.get('assets')

    if assets is None:
        return jsonify({"error": "No assets provided"}), 500

    # Split the assets by comma
    asset_list = assets.split(',')

    # Fetch rates for the requested assets
    response = {"data": {}}
    for asset in asset_list:
        if asset == 'EUR ESTR':
            euroestr_rate = fetch_euroestr_rate()
            if euroestr_rate is not None:
                response["data"]["EUR ESTR"] = {"tenor": "O/N", "date": get_yesterday_date(), "value": str(euroestr_rate)}
            else:
                response["data"]["EUR ESTR"] = {"tenor": "O/N", "date": get_yesterday_date(), "value": curve_fail}
                # Schedule retry after one hour
                
        elif asset == 'USD SOFR':
            sofr_rate = fetch_sofr_rate()
            if sofr_rate is not None:
                response["data"]["USD SOFR"] = {"tenor": "O/N", "date": get_yesterday_date(), "value": str(sofr_rate)}
            else:
                response["data"]["USD SOFR"] = {"tenor": "O/N", "date": get_yesterday_date(), "value": curve_fail}
                # Schedule retry after one hour
                
        elif asset == 'MIBOR':
            mibor_rate = fetch_mibor_rate()
            if mibor_rate is not None:
                response["data"]["MIBOR"] = {"tenor": "O/N", "date": get_yesterday_date(), "value": str(mibor_rate)}
            else:
                response["data"]["MIBOR"] = {"tenor": "O/N", "date": get_yesterday_date(), "value": curve_fail}
                # Schedule retry after one hour
                
        elif asset == 'USDINR':
            spot_rate = fetch_USDINR_Spot()
            SixM_rate = fetch_6M()
            if spot_rate is not None and SixM_rate is not None:
                usd_inr_data = [
                    {"tenor": "SPOT", "date": get_yesterday_date(), "value": str(spot_rate)},
                    {"tenor": "6M", "date": get_yesterday_date(), "value": str(SixM_rate)}
                ]
                response["data"]["USDINR"] = usd_inr_data
            else:
                response["data"]["USDINR"] = {"date": get_yesterday_date(), "value": curve_fail}
                # Schedule retry after one hour
                
        elif asset == 'MOD MIFOR':
            mifor_rate = fetch_mifor()
            if mifor_rate is not None:
                response["data"]["MOD MIFOR"] = {"tenor": "6M", "date": get_yesterday_date(), "value": str(mifor_rate)}
            else:
                response["data"]["MOD MIFOR"] = {"tenor": "6M", "date": get_yesterday_date(), "value": curve_fail}
                # Schedule retry after one hour
               
        elif asset == 'JPY TONAR':
            tonar_rate = fetch_tonar_rate()
            if tonar_rate is not None:
                response["data"]["JPY TONAR"] = {"tenor": "O/N", "date": get_yesterday_date(), "value": str(tonar_rate)}
            else:
                response["data"]["JPY TONAR"] = {"tenor": "O/N", "date": get_yesterday_date(), "value": curve_fail}
                # Schedule retry after one hour
               
        else:
            response["data"][asset.upper()] = {"tenor": "Unkown", "date": get_yesterday_date(), "value": f"Error: Unknown asset '{asset}'"}
    
    return jsonify(response)

# Counter to keep track of retry attempts
retry_counter = 0
def retry_euroestr_fetch():
    global retry_counter
    retry_counter += 1
    print(f"Retry attempt {retry_counter} for EuroEstr rate fetch.")
    if retry_counter <= 5:
        euroestr_rate = fetch_euroestr_rate()
        if euroestr_rate is not None:
            print("EuroEstr rate fetched successfully after retry.")
            return euroestr_rate
        else:
            print("Failed to fetch EuroEstr rate after retry. Please check.")
            return curve_fail
    else:
        print("Fetching has been tried 5 times and the dates still do not match. It might be a holiday")
        return Holiday
    

def retry_sofr_fetch():
    global retry_counter
    retry_counter += 1
    print(f"Retry attempt {retry_counter} for Sofr rate fetch.")
    if retry_counter <= 5:
        sofr_rate = fetch_sofr_rate()
        if sofr_rate is not None:
            print("Sofr rate fetched successfully after retry.")
            return sofr_rate
        else:
            print("Failed to fetch Sofr rate after retry. Please check.")
            return curve_fail
    else:
        print("Fetching has been tried 5 times and the dates still do not match. It might be a holiday")
        return Holiday

def retry_mibor_fetch():
    global retry_counter
    retry_counter += 1
    print(f"Retry attempt {retry_counter} for Mibor rate fetch.")
    if retry_counter <= 5:
        mibor_rate = fetch_mibor_rate()
        if mibor_rate is not None:
            print("Mibor rate fetched successfully after retry.")
            return mibor_rate
        else:
            print("Failed to fetch Mibor rate after retry. Please check.")
            return curve_fail
    else:
        print("Fetching has been tried 5 times and the dates still do not match. It might be a holiday")
        return Holiday

def retry_spot_fetch():
    global retry_counter
    retry_counter += 1
    print(f"Retry attempt {retry_counter} for Spot rate fetch.")
    if retry_counter <= 5:
        spot_rate = fetch_USDINR_Spot()
        if spot_rate is not None:
            print("Spot rate fetched successfully after retry.")
            return spot_rate
        else:
            print("Failed to fetch Spot rate after retry. Please check.")
            return curve_fail
    else:
        print("Fetching has been tried 5 times and the dates still do not match. It might be a holiday")
        return Holiday

def retry_SixM_fetch():
    global retry_counter
    retry_counter += 1
    print(f"Retry attempt {retry_counter} for 6M rate fetch.")
    if retry_counter <= 5:
        SixM_rate = fetch_6M()
        if SixM_rate is not None:
            print("6M rate fetched successfully after retry.")
            return SixM_rate
        else:
            print("Failed to fetch 6M rate after retry. Please check.")
            return curve_fail
    else:
        print("Fetching has been tried 5 times and the dates still do not match. It might be a holiday")
        return Holiday
    
def retry_mifor_fetch():
    global retry_counter
    retry_counter += 1
    print(f"Retry attempt {retry_counter} for Mifor rate fetch.")
    if retry_counter <= 5:
        mifor_rate = fetch_mifor()
        if mifor_rate is not None:
            print("Mifor rate fetched successfully after retry.")
            return mifor_rate
        else:
            print("Failed to fetch Mifor rate after retry. Please check.")
            return curve_fail
    else:
        print("Fetching has been tried 5 times and the dates still do not match. It might be a holiday")
        return Holiday

def retry_tonar_fetch():
    global retry_counter
    retry_counter += 1
    print(f"Retry attempt {retry_counter} for Tonar rate fetch.")
    if retry_counter <= 5:
        tonar_rate = fetch_tonar_rate()
        if tonar_rate is not None:
            print("Tonar rate fetched successfully after retry.")
            return tonar_rate
        else:
            print("Failed to fetch Tonar rate after retry. Please check.")
            return curve_fail
    else:
        print("Fetching has been tried 5 times and the dates still do not match. It might be a holiday")
        return Holiday




if __name__ == '__main__':
    app.run(debug=True)

