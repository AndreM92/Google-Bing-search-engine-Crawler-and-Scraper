# -*- coding: utf-8 -*-
"""
Created on Mon Dec 12 07:44:36 2022

@author: andre
"""

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC
from selenium.common.exceptions import *

from bs4 import BeautifulSoup
import lxml
import numpy as np
import pandas as pd
import time
import re

# Just in case a driver bug happens (Window closes unintended)
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Alternative setting options
def fixDriverbug():
    options = webdriver.ChromeOptions()
    options.add_experimental_option("detach", True)
    driver = webdriver.Chrome(options=options, service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.get('https://www.bing.com/?cc=de')
    time.sleep(2)
    try:
        driver.find_element('xpath','//*[@id="bnp_btn_reject"]').click()
        time.sleep(1)
    except:
        try:
            driver.find_element('xpath','/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input')
        except Exception as e:
            print(repr(e))
            print('There is something wrong with the page')
            time.sleep(1)
            driver.close()
            exit()

###############################################################################
# Setting the companies and keywords I'm searching for
# Import company names from their url
companies = [
    'bosch-thermotechnology',
    'buderus',
    'daikin',
    'dimplex',
    'mitsubishi-les',
    'nibe',
    'stiebel-eltron',
    'vaillant',
    'viessmann',
    'wolf'
]

keywords= [
    'Wärmepumpe',
    'Wärmepumpe Kosten',
    'Luftwärmepumpe',
    'Wasser Wärmepumpe',
    'Erdwärmepumpe'
]
        
###############################################################################
# Setting the driver and click through the cookie banner
driver = webdriver.Chrome('[yourpath]\chromedriver.exe')
driver.maximize_window()
driver.get('https://www.bing.com/?cc=de')
WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'bnp_container')))
driver.find_element('xpath','//*[@id="bnp_btn_reject"]').click()
try:
    time.sleep(2)
    driver.find_element('xpath','//*[@id="sb_form_q"]')
except:
    fixDriverbug()

###############################################################################
# The two classes Ads and Hits are collecting all the selected search results and save them in a list
class Ads():
    adList = []
    def appendAdList(self,keyword,company,rank,page,title,content,tags,link,fullcontent):
        self.adList.append([keyword,company,rank,page,title,content,tags,link,fullcontent])
    # optional
    def getList(self):
         return self.adList
        
class Hits():
    hitList = []
    def appendHitList(self,keyword,company,rank,page,title,content,tags,link,fullcontent):
        self.hitList.append([keyword,company,rank,page,title,content,tags,link,fullcontent])

# The class Crawler with its functions crawls through the bing search engine and scrapes all the relevant data  
class Crawler():
    def __init__(self):
        for k in keywords:
            print(k) # if you want to check the program while it runs
            #this should always be the startpage
            startpage = 'https://www.bing.com/?cc=de'
            if startpage != driver.current_url:
                driver.get(startpage)
                time.sleep(1)

            searchbox = driver.find_element('xpath','//*[@id="sb_form_q"]')
            searchbox.clear()
            searchbox.send_keys(k)
            searchbox.send_keys(Keys.ENTER)
            time.sleep(1)
            
            self.rankads = 0
            self.rankhits = 0
            self.page = 1   
            
            while self.page <= 10:
                soup = BeautifulSoup(driver.page_source,'lxml')
                print('page: ' + str(self.page))  # if you want to check the program while it runs
                
                # Code block for the collection of google ads
                adsupper = soup.find_all('div',class_='sb_add sb_adTA')
                adslower = soup.find_all('div',class_='sb_add sb_adTA b_adscv')
                ads = adsupper + adslower
                if ads == '':
                    continue
                for a in ads:
                    self.rankads = self.rankads +1
                    self.scrapeAds(k,self.rankads,self.page,a)

                # Code block for the collection of generic search results
                hits = soup.find_all('li',class_='b_algo')
                if hits == '':
                    continue
                for h in hits:                    
                    self.rankhits = self.rankhits +1
                    self.scrapeHits(k,self.rankhits,self.page,h)
                
                # Go to the next page after the scraping process is finished
                self.page = self.newpage(self.page)
            
    def scrapeAds(self,keyword,rank,page,a):
        # resetting the variables
        link,title,content,tags,fullcontent = ['' for i in range(0,5)]
        link = a.find('div',class_='b_adurl').text
        for c in companies:
#            print(c)  # if you want to check the program while it runs
            if c + '.de' in link or c + '.com' in link or c + '.eu' in link or 'de.' + c in link:
                fullcontent_raw = a.text
                fullcontent = re.sub(r'([a-z](?=[A-Z])|[A-Z](?=[A-Z][a-z]))', r'\1 ', fullcontent_raw)
                try:
                    title = a.find('a').text
                    content = ' '.join([x.text for x in a.find('p')][1:])
                    tags = '; '.join([t.text for t in a.find_all('a') if t.text != ''][3:])   
                except:
                    pass
                
                Ads().appendAdList(keyword,c,rank,page,title,content,tags,link,fullcontent)
                
    def scrapeHits(self,keyword,rank,page,h):
        # resetting the variables
        link,title,content,tags,fullcontent = ['' for i in range(0,5)]
        link = h.find('div',class_='b_attribution').text       
        for c in companies:
            if c + '.de' in link or c + '.com' in link or c + '.eu' in link or 'de.' + c in link:
                fullcontent_raw = h.text
                fullcontent = re.sub(r'([a-z](?=[A-Z])|[A-Z](?=[A-Z][a-z]))', r'\1 ', fullcontent_raw)
                try:
                    title = h.find('a').text
                    content = ' '.join([c.text for c in h.find('p')]).replace('Web ','')
                    tags = '; '.join([t.text for t in h.find_all('a') if t.text != ''][3:])
                except:
                    pass   
                
                Hits().appendHitList(keyword,c,rank,page,title,content,tags,link,fullcontent)
                
    def newpage(self,page):
        page += 1
        if page > 10:
             return page
        # click on the 'next' button to scrape the next page
        # find element by xpath doesn't work with Bing, because it changes from page to page
        try:
            driver.find_element(By.CSS_SELECTOR,"[title^='Nächste Seite']").click()
            time.sleep(1)
        except ElementClickInterceptedException:
            try:
                button = driver.find_element(By.CSS_SELECTOR,"[title^='Nächste Seite']")
                driver.execute_script("arguments[0].click();", button)
            except Exception as e:
                print(repr(e))
                find_button = BeautifulSoup(driver.page_source,'lxml')
                url = find_button.find('a',class_='sb_pagN sb_pagN_bp b_widePag sb_bp ')['href']
                nextpage = 'https://www.bing.com' + url
                driver.get(nextpage)
        return page 
            
# run the crawler    
Crawler()


# The cleaned up data can be saved in dataframes
headerAds = ['keyword','company','rank','page','title','content','tags','link','fullcontent']
dfAds = pd.DataFrame(Ads().adList,columns=headerAds)

headerHits = ['keyword','company','rank','page','title','content','tags','link','fullcontent']
dfHits = pd.DataFrame(Hits().hitList,columns=headerHits)

# I'm exporting the data into one excel-file and save the dataframes in different sheets
path = "C:\\Users\\andre\\OneDrive\Desktop\BingSearchResults.xlsx"
with pd.ExcelWriter(path, engine='openpyxl') as writer:
    dfAds.to_excel(writer,sheet_name='Advertisements')
    dfHits.to_excel(writer,sheet_name='Search_Results')   