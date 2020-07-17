#!/usr/bin/python3

import amazon_scraper
import settings
import time
import random

# Setting up logging options
import logging 

if settings.DEBUG is True:
    logging_level = logging.DEBUG
else:
    logging_level = logging.INFO

logging_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'

logging.basicConfig(level = logging_level, format=logging_format)

if __name__ == "__main__":
    """
    Schedules the Amazon Scraper to run based on values in the settings.py file.
    """
    min_update_interval = settings.MINIMUM_UPDATE_INTERVAL_MINUTES
    max_update_interval = settings.MAXIMUM_UPDATE_INTERVAL_MINUTES   

    logging.info(f"Starting scheduler")

    while True:
        amazon_scraper.main()
        sleep_time_seconds = random.randrange(min_update_interval, max_update_interval) * 60
        logging.info(f"Completed update, next update in {sleep_time_seconds / 60} minutes")
        time.sleep(sleep_time_seconds)


