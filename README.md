# Amazon Scraper

A script to scrape Amazon listings and update information in Zen Arbitrage.

## Installing Dependencies Locally

Use `pip` to install dependencies using the `requirements.txt` file. 

```
$ pip install requirements.txt
```

It's recommended to use a virtual environment when installing dependencies like this. Several tools exist for this purpose, I can recommend `pipenv`.

This script expects Chrome to be installed on the host system for use as a driver.

## Running Locally

To run the update script a single time, you can run the `amazon_scraper.py` file by itself.

```
# If there is no virtual env in use
python amazon_scraper.py

# If pipenv is being used
pipenv run python amazon_scraper.py
```

To run the script forever, with updates at a random interval between the minimum and maximum value 
found in the `settings.py` file, run the `scheduler.py` file.

```
# If there is no virtual env in use
python scheduler.py

# If pipenv is being used
pipenv run python scheduler.py
```

## Deploying to a Cloud Instance

In order to deploy the code to a cloud instance, you must have SSH access with root or `sudo` capabilities.
I would recommend creating a folder in the `/opt/` folder for the application. 
Cloning from git will do that automatically.

```
# Updating and installing necessary packages
sudo apt update
sudo apt install chromium-driver python-pip tmux

# If you are cloning this from a git repository
cd /opt/
git clone [github/gitlab/local git URL]

# If you are transferring the files from a local folder or zip archive you can use one of 
# the following techniques
# https://cloud.google.com/compute/docs/instances/transfer-files

# Once the files are in an 'amazon-scraper' folder in /opt/
# Navigate into it and add the right permissions to the python files
cd amazon-scraper
sudo pip3 install requirements.txt
```

## Running in the Cloud Instance

Tmux is used to keep the process running even after closing your SSH connection to the cloud instance.
Normally a built-in command like `nohup` would work but Selenium seems to have problems with it.
Tmux is more complicated to use but keeps Selenium and the chrome driver alive even after the terminal is closed.

```
# Start a new tmux session with a given name and run the scheduler file
tmux new -s amazon-scraper

# Navigate to the amazon-scraper folder used earlier
cd /opt/amazon-scraper/

# Start the scheduler
python3 scheduler.py
```

Detach from the running process and leave it running in the background by pressing `Ctrl + b` followed by `d`.
You can now close your SSH connection and tmux will keep the scheduler running continously.

## Reconnecting to the Cloud Instance

When reconnecting to the cloud instance using SSH, you can reconnect to Tmux at any point to check on the running process.

```
# Use the name from the tmux new command
tmux a -t amazon-scraper
```

If you don't remember the name of the session you previously created, you can use the command `tmux ls` to list all running sessions.

[Here's](https://gist.github.com/henrik/1967800) a cheatsheet on tmux for reference.

## Settings

There are several settings that can be changed in `settings.py`. This file must be kept with `amazon_scraper.py` for the scraper to work properly.

 - DEBUG: Debugging output from the script and selenium are printed to the terminal
 - HEADLESS: Run the browser in the background, invisible to the user.
 - UPDATE_INTERVAL_MINUTES: Minutes between completely updating the Zen Arbitrage table. The script will select a random value between the MINIMUM and MAXIMUM values each time it updates.
 - PAGE_LOAD_WAIT_SECONDS: Time in seconds to wait for a page to fully load. 10 seconds is an arbitrary but safe default.
 
##### Further Questions
 Author: scott@hutchinson.engineering
