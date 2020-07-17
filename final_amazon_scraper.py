#!/usr/bin/python3

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
import settings
import logging
import time

# Setting up logging options
if settings.DEBUG is True:
    logging_level = logging.DEBUG
else:
    logging_level = logging.INFO

logging_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(level = logging_level, format=logging_format)


def create_driver():
    """
    Creates a chrome web driver using settings from the settings.py file.
    """
    logging.debug("Creating web driver")
    options = Options()
    # Consistent window size means consistent page layouts and naming
    options.add_argument("--window-size=1920x1080")

    if settings.HEADLESS:
        options.add_argument("--headless")

    driver = webdriver.Chrome(options=options)
    logging.debug("Web driver created")
    return driver



def create_new_tab(driver, url):
    """
    Creates a new tab with an URL and switches focus to it.
    """
    logging.debug(f"Creating new tab for {url}")
    script = f"window.open('{url}','_blank');"
    driver.execute_script(script)
    time.sleep(settings.PAGE_LOAD_WAIT_SECONDS)
    driver.switch_to.window(driver.window_handles[-1]) # last window/tab
    logging.debug(f"Switched tabs to {url}")

def close_tab(driver):
    """
    Closes the currently focused tab.
    """
    logging.debug(f"Closing tab of {driver.current_url}")
    driver.close()
    driver.switch_to.window(driver.window_handles[0]) # first window/tab
    logging.debug(f"Tab closed")

def close_driver(driver):
    """
    Logs out, cleans up, and shuts down driver.
    """
    logging.debug(f"Closing driver")
    log_out_zen_arbitrage(driver)
    driver.quit()
    logging.debug(f"Driver closed")

def log_in_zen_arbitrage(driver):
    """
    Logs into Zen Arbitrage using the default log-in url with no callbacks.
    """
    logging.debug(f"Logging into Zen Arbitrage")
    login_url = "https://account.zenarbitrage.com/sign-in"
    driver.get(login_url)
    time.sleep(settings.PAGE_LOAD_WAIT_SECONDS)

    # Focusing on just the sign-in box, makes it more robust
    sign_in_box = driver.find_element_by_class_name("greet-box")
    email_field = sign_in_box.find_element_by_id("user_email")
    password_field = sign_in_box.find_element_by_id("user_password")
    sign_in_button = sign_in_box.find_element_by_class_name("btn-success")

    # Entering information and clicking log-in button
    email_field.send_keys(settings.ZEN_ARBITRAGE_EMAIL)
    password_field.send_keys(settings.ZEN_ARBITRAGE_PASSWORD)
    sign_in_button.click()
    time.sleep(settings.PAGE_LOAD_WAIT_SECONDS)

    # If the page didn't redirect after log-in, something went wrong
    if driver.current_url == login_url:
        error_message = sign_in_box.find_element_by_class_name("error-message")
        raise RuntimeError(f"Zen Arbitrage log-in unsuccessful, reason: {error_message.text}")
    logging.debug(f"Zen Arbitrage log-in successful")

def log_out_zen_arbitrage(driver):
    """
    Logs out of Zen Arbitrage.
    """

    logging.debug(f"Logging out of Zen Arbitrage")

    navbar = driver.find_element_by_class_name("navbar")
    username_box = navbar.find_element_by_class_name("dropdown")
    username_box.click()
    # This sleep can be much shorter since we're just waiting for a drop-down to show up
    time.sleep(1)
    logout_button = username_box.find_element_by_link_text("Sign Out")
    logout_button.click()

    logging.debug(f"Logged out of Zen Arbitrage")
    time.sleep(settings.PAGE_LOAD_WAIT_SECONDS)

def scrape_amazon_listing(driver):
    """
    Scrapes the price and condition from the amazon listing.
    """
    data = []
    olp_rows = driver.find_elements_by_class_name("olpOffer")
    logging.debug(f"Found {len(olp_rows)} entries for {driver.current_url}")

    for olp_row in olp_rows:
        # Determine if the row is FBA by finding Prime icon below the price
        prime_element = olp_row.find_elements_by_class_name("a-icon-prime")
        if len(prime_element) > 0: 
            price_element = olp_row.find_element_by_class_name("olpPriceColumn")
            # Example price element text: 
            # '$21.51\n+ $3.99 shipping'
            price = price_element.text.split('\n')[0].strip('$')

            condition_element = olp_row.find_element_by_class_name("olpConditionColumn")
            # Example condition element text: 
            # 'Used - Good\nOver 1 Million Amazon Orders Shipped - Buy with Confidence - Sati... » Read more'
            condition = condition_element.text.split('\n')[0]

            data.append({'price': price,
                         'condition': condition,
            })
            logging.debug(f"Current entry: Price: {price}, Condition: {condition}")

    return data

def get_condition_index(condition):
    """
    Given a condition from an Amazon listing, returns the index of the 
    condition in the Condition drop-down list on Zen Arbitrage.
    """

    mapping = {
            "New" : 0,
            "Used - Like New" : 1,
            "Used - Very Good" : 2,
            "Used - Good" : 3,
            "Used - Acceptable" : 4,
    }

    if condition in mapping:
        index = mapping[condition]
        logging.debug(f"Condition {condition} mapped to index {index}")
        return index
    else:
        raise ValueError((f"Condition not recognized. Is: {condition}, "
                          f"should be one of {list(mapping.keys())}"))

def navigate_to_zen_arbitrage_listing_page(driver, page_name):
    pagination = driver.find_elements_by_class_name("pagination")
    page = pagination.find_elements_by_class_name(page_name)
    page_url = last_page.get_attribute("href")
    driver.get(last_page_url)
    time.sleep(settings.PAGE_LOAD_WAIT_SECONDS)

def update_zen_arbitrage_listing_page(driver):
    """
    Works backwards from a Zen Arbitrage listing page from the last entry to the first.
    """
    listings_table_rows = driver.find_elements_by_css_selector("#products-table tr")
    # First row is the header so we can disregard that
    # Start at the last row and work backwards up the table
    for table_row in listings_table_rows[-1:0:-1]:
        # Navigate to amazon link
        ISBN = table_row.find_element_by_class_name("an-amazon-link")
        amazon_link = ISBN.get_attribute("href")
        create_new_tab(driver, amazon_link)

        # Check that we navigated to the right page, otherwise throw error
        # We might be redirected to a 404 page or Captcha page which 
        # we shouldn't try to parse.
        if driver.current_url != amazon_link:
            raise RuntimeError(("Navigation to Amazon listing page failed,\n"
                               f"requested_page: {amazon_link},\n"
                               f"actual url: {driver.current_url}"))
        
        # Grab the applicable data and navigate back to Zen Arbitrage
        data = scrape_amazon_listing(driver)
        close_tab(driver)
        
        # Edit the row and enter the information scraped from amazon
        edit_button = table_row.find_element_by_class_name("edit_save_btn")
        edit_button.click()
        
        # First entry from Amazon is used for the FBA_Price and Condition, if it exists
        if len(data) > 0:
            new_FBA_price = data[0]['price']
            new_condition = data[0]['condition']
            new_condition_index = get_condition_index(new_condition)
        else:
            new_FBA_price = ''
            new_condition_index = 4 # The condition doesn't matter if there isn't an entry

        FBA_price_field = table_row.find_element_by_css_selector("[data-field=fba_price]")
        FBA_price_input = FBA_price_field.find_element_by_tag_name("input")
        FBA_price_input.clear()
        FBA_price_input.send_keys(new_FBA_price)

        condition_dropdown = table_row.find_element_by_css_selector("[data-field=condition]")
        condition_select = Select(condition_dropdown.find_element_by_tag_name("select"))
        condition_select.select_by_index(new_condition_index)

        # Second entry from Amazon is the 2nd Lowest FBA Price, if it exists
        if len(data) > 1:
            new_second_FBA_price = data[1]['price'] 
        else:
            new_second_FBA_price = ''
        second_FBA_price_field = table_row.find_element_by_css_selector("[data-field=secondary_fba_price]")
        second_FBA_price_input = second_FBA_price_field.find_element_by_tag_name("input")
        second_FBA_price_input.clear()
        second_FBA_price_input.send_keys(new_second_FBA_price)

        # Saving updates
        edit_button.click()


def main():
    """
    Main function when script is executed. Logs into Zen Arbitrage, navigates to 
    the account listings, and updates data in each listing from Amazon.
    Then logs out of Zen Arbitrage and closes the browser session.
    """


    # Initializing and navigating to the listing page
    driver = create_driver()
    log_in_zen_arbitrage(driver)
    listing_url = "https://marketplace.zenarbitrage.com/listings"
    # For whatever reason, the first time this page is 'get'ed, it goes 
    # to the more generic marketplace page. Only after a 2nd 'get'
    # will it go to the actual listings page
    driver.get(listing_url)
    time.sleep(settings.PAGE_LOAD_WAIT_SECONDS)
    driver.get(listing_url)
    time.sleep(settings.PAGE_LOAD_WAIT_SECONDS)

    # Updating all listings
    logging.debug(f"Beginning Zen Arbitrage table update")

    # Determining if there are multiple pages on the listing page
    pagination = driver.find_elements_by_class_name("pagination")
    if len(pagination) > 0: # If there is more than one page
        # Navigating to last page
        logging.debug(f"Multiple listing pages found, starting at the last page.")
        last_page = pagination[0].find_element_by_class_name("last")
        last_page_url = last_page.find_element_by_tag_name("a").get_attribute("href")
        driver.get(last_page_url)
        time.sleep(settings.PAGE_LOAD_WAIT_SECONDS)
        update_zen_arbitrage_listing_page(driver)
        
        # Working backwards from the last page to the first
        while True:
            pagination = driver.find_element_by_class_name("pagination")
            prev_page = pagination.find_elements_by_class_name("prev")
            if len(prev_page) == 0: # If we've reached the first page
                logging.debug(f"Reached first page")
                break
            prev_page_url = prev_page[0].find_element_by_tag_name("a").get_attribute("href")
            logging.debug(f"Navigating to previous page {prev_page_url}")
            driver.get(prev_page_url)
            time.sleep(settings.PAGE_LOAD_WAIT_SECONDS)
            update_zen_arbitrage_listing_page(driver)

    else: # If there's only one page of listings
        logging.debug(f"One listing page found.")
        update_zen_arbitrage_listing_page(driver)


    # Logging out and cleaning up  
    close_driver(driver)


if __name__ == "__main__":
    main()
