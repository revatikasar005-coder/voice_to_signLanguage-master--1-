import os
from conf import DRIVER_DIR
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, WebDriverException, SessionNotCreatedException
import time
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait  # for implicit and explict waits
from selenium.webdriver.chrome.options import Options  # for suppressing the browser
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
# !Make sure you use same VERSION OF CHROME AND DRIVER

def getLink(word):
    # print("recives word is " + word + "\n")
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--allow-running-insecure-content')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--ignore-certificate-errors')

    try:
        service = Service(DRIVER_DIR)
        driver = webdriver.Chrome(service=service, options=options)
    except (WebDriverException, SessionNotCreatedException):
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
    # link to get videoptions=option

    try:
        driver.get("https://www.talkinghands.co.in/video/" + word + "mp4")
        time.sleep(0.5)
        try:
            value_xpath = driver.find_element(By.XPATH, '/html/body/div[3]/div/div[2]/div/div[1]/div/div/div/video/source')
            link = value_xpath.get_attribute('src')
            if link:
                return link
        except NoSuchElementException:
            pass

        driver.get("http://indiansignlanguage.org/" + word + "/")
        time.sleep(0.5)
        try:
            value_xpath = driver.find_element(By.XPATH, "/html/body/div/div[2]/div/div/div[1]/main/article/div/div/div/iframe")
            link = value_xpath.get_attribute('src')
            if link:
                return link
        except NoSuchElementException:
            pass

        return 0
    finally:
        try:
            driver.quit()
        except Exception:
            pass