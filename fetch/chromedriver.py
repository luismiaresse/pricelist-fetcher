import logging
import os
import undetected_chromedriver as uc


def detect_installed_chrome_version():

    chrome_ver_path = None
    # Detect OS
    if os.name == 'nt':          # Windows
        # TODO Detect from executable
        # Read "Last Version" from $LOCALAPPDATA\Google\Chrome\User Data\Last Version
        chrome_ver_path = os.path.join(os.environ['LOCALAPPDATA'], 'Google', 'Chrome', 'User Data', 'Last Version')
    elif os.name == 'posix':     # Linux
        # Read version from executable
        if os.system('which google-chrome-stable >/dev/null 2>&1') == 0:
            chrome_full_ver = os.popen('google-chrome-stable --version').read().split(" ")[-2]   # Last is \n
            chrome_main_ver = chrome_full_ver.split('.')[0]
            return chrome_main_ver
        # If it is Chromium
        elif os.system('which chromium-browser >/dev/null 2>&1') == 0:
            chrome_full_ver = os.popen('chromium-browser --version').read().split(" ")[-2]
            chrome_main_ver = chrome_full_ver.split('.')[0]
            return chrome_main_ver
        else:
            # Read "Last Version" from $HOME/.config/google-chrome/Last Version
            chrome_ver_path = os.path.join(os.environ['HOME'], '.config', 'google-chrome', 'Last Version')
    else:
        logging.error("OS not recognized or not supported")
        exit(1)

    try:
        with open(chrome_ver_path, 'r') as f:
            chrome_full_ver = f.read()
    except Exception as e:
        logging.error(f"Could not detect installed Chrome version: {e}")
        exit(1)
    chrome_main_ver = chrome_full_ver.split('.')[0]
    return chrome_main_ver


def webdriver_init():
    chrome_options = uc.ChromeOptions()
    chrome_options.headless = True
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--log-level=3')
    chrome_options.add_argument('--disable-extensions')
    chrome_options.add_argument('--disable-dev-shm-usage')      # Prevents crash in Docker
    # chrome_options.add_experimental_option("prefs", {'profile.managed_default_content_settings.javascript': 2})   # Disable JavaScript
    # chrome_options.add_argument('--user-agent= Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:70.0) Gecko/20100101 Firefox/70.0')
    chrome_main_ver = detect_installed_chrome_version()
    driver = uc.Chrome(options=chrome_options, version_main=chrome_main_ver)
    driver.set_page_load_timeout(20)
    driver.maximize_window()
    return driver
