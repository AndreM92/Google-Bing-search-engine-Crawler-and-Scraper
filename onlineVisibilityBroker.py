from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC

from bs4 import BeautifulSoup
import lxml
import time
import pandas as pd

companys = [
    'ing'
    'comdirect'
    'sbroker'
]

keywords= [
    'Depotkonto eröffnen'
    'Wertpapiere'
    'Aktien'
]

driver = webdriver.Chrome('C:\\Users\\andre\Documents\Python\chromedriver.exe')
driver.get('https://www.google.de/?hl=de')
WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'QS5gu sy4vM')))

# Cookies
driver.find_element('xpath','//*[@id="W0wltc"]/div').click()

WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'gLFyf gsfi')))
searchxp = '/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input'
driver.find_element(('xpath',searchxp)).send_keys((keywords[1]).ENTER)


'Depotkonto eröffnen'