# -*- coding: utf-8 -*-
"""
Created on Sun Dec 11 15:42:21 2022

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
    driver.get('https://www.google.de/?hl=de')
    WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'jw8mI')))
    try:
        driver.find_element('xpath','//*[@id="W0wltc"]/div').click()
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
driver = webdriver.Chrome('[path to your driver]\chromedriver.exe')
driver.maximize_window()
driver.get('https://www.google.de/?hl=de')
WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'jw8mI')))
driver.find_element('xpath','//*[@id="W0wltc"]/div').click()
try:
    time.sleep(2)
    driver.find_element('xpath','/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input')
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

# This function crawls through the google search engine and scrapes all the relevant data
class Crawler():
    def __init__(self):
        for k in keywords:
            print(k) # if you want to check the program while it runs
            #this should always be the startpage
            driver.get('https://www.google.de/?hl=de')
            time.sleep(1)

            searchbox = driver.find_element('xpath','/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input')
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
                ads = soup.find_all('div',class_='uEierd')
                if ads == '':
                    continue
                for a in ads:
                    self.rankads = self.rankads +1
                    self.scrapeAds(k,self.rankads,self.page,a)

                # Code block for the collection of generic search results
                hits = soup.find_all('div',class_='MjjYud')
                if hits == '':
                    continue
                for h in hits:                    
                    self.rankhits = self.rankhits +1
                    self.scrapeHits(k,self.rankhits,self.page,h)
                
                # Go to the next page after the scraping process is finished
                self.page = self.newpage(self.page)
            
    def scrapeAds(self,keyword,rank,page,a):
        # resetting the variables
        link,title,content,tags,fullcontent = np.array(['' for i in range(0,5)])
        link = a.find('span',class_='x2VHCd OSrXXb nMdasd qzEoUe').text
        for c in companies:
#            print(c)  # if you want to check the program while it runs
            if c + '.de' in link or c + '.com' in link or c + '.eu' in link or 'de.' + c in link:
                fullcontent_raw = a.text
                fullcontent = re.sub(r'([a-z](?=[A-Z])|[A-Z](?=[A-Z][a-z]))', r'\1 ', fullcontent_raw)
                try:
                    title = a.find('span').text
                    content = a.find('div',class_='MUxGbd yDYNvb lyLwlc').text
                    tags = a.find('div',class_='dcuivd MUxGbd lyLwlc aLF0Z OSrXXb')
                    if len(tags) > 1:
                        try:
                            tags = [re.sub(r'([a-z](?=[A-Z])|[A-Z](?=[A-Z][a-z]))', r'\1 ',t.text) for t in tags]
                        except:
                            pass    
                except:
                    pass
                
                Ads().appendAdList(keyword,c,rank,page,title,content,tags,link,fullcontent)
                
    def scrapeHits(self,keyword,rank,page,h):
        # resetting the variables
        link,title,content,tags,fullcontent = np.array(['' for i in range(0,5)])
        link = h.find('a')['href']        
        for c in companies:
            if c + '.de' in link or c + '.com' in link or c + '.eu' in link or 'de.' + c in link:
                fullcontent_raw = h.text
                fullcontent = re.sub(r'([a-z](?=[A-Z])|[A-Z](?=[A-Z][a-z]))', r'\1 ', fullcontent_raw)
                try:
                    title = h.find('h3',class_='LC20lb MBeuO DKV0Md').text
                except:
                       str(h.find('h3',class_='LC20lb MBeuO DKV0Md')) 
                try:
                    content = h.find('div',class_='VwiC3b yXK7lf MUxGbd yDYNvb lyLwlc lEBKkf').text
                    tags = h.find('div',class_='HiHjCd')
                    if len(tags) > 1:
                        try:
                            tags = [re.sub(r'([a-z](?=[A-Z])|[A-Z](?=[A-Z][a-z]))', r'\1 ',t.text) for t in tags]
                        except:
                            pass
                except:
                    pass   
                
                Hits().appendHitList(keyword,c,rank,page,title,content,tags,link,fullcontent)
                
    def newpage(self,page):
        page += 1
        if page > 10:
             return page
        # click on the 'next' button to scrape the next page
        driver.find_element('xpath','//*[@id="pnnext"]/span[2]').click()
        time.sleep(1)
        return page
            
# run the crawler    
Crawler()

# direct output
#print(Ads().adList)
#print(Hits().hitList)
#print(Ads().getList())

###############################################################################
# The cleaned up data can be saved in dataframes
headerAds = ['keyword','company','rank','page','title','content','tags','link','fullcontent']
dfAds = pd.DataFrame(Ads().adList,columns=headerAds)

headerHits = ['keyword','company','rank','page','title','content','tags','link','fullcontent']
dfHits = pd.DataFrame(Hits().hitList,columns=headerHits)

# I'm exporting the data into one excel-file and save the dataframes in different sheets
path = "googleSearchResults.xlsx"
with pd.ExcelWriter(path, engine='openpyxl') as writer:
    dfAds.to_excel(writer,sheet_name='Advertisements')
    dfHits.to_excel(writer,sheet_name='Search_Results')
