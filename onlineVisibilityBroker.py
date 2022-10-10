# -*- coding: utf-8 -*-
"""
Created on Wed Sep 28 07:04:48 2022

@author: andre
"""
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
import selenium.webdriver.support.expected_conditions as EC

from bs4 import BeautifulSoup
import lxml
import time
import pandas as pd

companies = [
    'agora-direct',
    'banxbroker',
    'comdirect',
    'consorsbank',
    'etoro',
    'finanzen',
    'flatex',
    'ing',
    'justtrade',
    'onvista',
    'sbroker',
    'smartbroker',
    'scalable.capital',
    'traderepublic',
    'union-investment'
]

keywords= [
    'Aktien',
    'Börse',
    'Depot',
    'ETF',
    'Wertpapiere'
]

# I'm setting the driver for Selenium
driver = webdriver.Chrome('C:\\Users\\andre\Documents\Python\chromedriver.exe')

# Click through cookie-banners
driver.get('https://www.google.de/?hl=de')
WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'jw8mI')))
driver.find_element('xpath','//*[@id="W0wltc"]/div').click()


# This function crawls through the google search engine and scrapes all the relevant data
def crawlScrape():
    dataAds = []   
    dataHits = []
    
    # Searching for all keywords with a loop
    for k in keywords:
        print('Searching for: ' + k)
        #this should always be the startpage
        driver.get('https://www.google.de/?hl=de')
        WebDriverWait(driver,5).until(EC.presence_of_element_located((By.CLASS_NAME,'lnXdpd')))        
       
        searchbox = driver.find_element('xpath','/html/body/div[1]/div[3]/form/div[1]/div[1]/div[1]/div/div[2]/input')
        searchbox.clear()
        searchbox.send_keys(k)
        searchbox.send_keys(Keys.ENTER)
    
        rankAds = 0
        rankHits = 0
        page = 1
        while page <= 5:
            print('page: ' + str(page))
            soup = BeautifulSoup(driver.page_source,'lxml')
            
            # Code block for the collection of google ads
            ads = soup.find_all('div',class_='uEierd')           
            for ad in ads:
                rankAds += 1
                link = ad.find('span',class_='x2VHCd OSrXXb nMdasd qzEoUe').text
                for c in companies:
                    if c + '.de' in link or c + '.com' in link or c + '.net' in link or 'de.' + c in link:
                        try:
                            title = ad.find('div',class_='CCgQ5 vCa9Yd QfkTvb MUxGbd v0nnCb').text
                        except:
                            title = str(ad.find('div',class_='CCgQ5 vCa9Yd QfkTvb MUxGbd v0nnCb'))
                        try:
                            content = ad.find('div',class_='MUxGbd yDYNvb lyLwlc').text
                        except:
                            content = ''
                        try:
                            tags = ad.find('div',class_='XUpIGb MUxGbd lyLwlc aLF0Z OSrXXb').text
                        except:
                            tags = ''
                        fullcontent = ad.text.split('Anzeige·')[-1]
                            
                        dataAds.append([c,k,rankAds,page,title,content,tags,fullcontent,link])
                        
            # Code block for the collection of generic search results
            hits = soup.find_all('div',class_='MjjYud')
            for h in hits:
                rankHits += 1
                link = h.find('a')['href']
                for c in companies:
                    if c + '.de' in link or c + '.com' in link or c + '.net' in link or 'de.' + c in link:
                        title = h.find('h3',class_='LC20lb MBeuO DKV0Md').text
                        try:
                            content = h.find('div',class_='VwiC3b yXK7lf MUxGbd yDYNvb lyLwlc lEBKkf').text
                        except:
                            content = ''
                        fullcontent = h.text
                        
                        dataHits.append([c,k,rankHits,page,title,content,fullcontent,link])
    
            page += 1
            # click on the 'next' button to scrape the next page
            driver.find_element('xpath','//*[@id="pnnext"]/span[2]').click()
            time.sleep(1)

    return [dataAds,dataHits]

data = crawlScrape()    


# The cleaned up data can be shown in a dataframe
dfAds = pd.DataFrame(data[0],columns=['company','keyword','rank','page','title','content','tags','fullcontent','link'])
dfHits = pd.DataFrame(data[1],columns=['company','keyword','rank','page','title','content','fullcontent','link'])
  
# I'm exporting the data into one excel-file and save the dataframes in different sheets
path = "C:\\Users\\andre\\OneDrive\Desktop\googleSearchResults.xlsx"
with pd.ExcelWriter(path, engine='openpyxl') as writer:
    dfAds.to_excel(writer,sheet_name='Advertisements')
    dfHits.to_excel(writer,sheet_name='Search_Results')            

    


    
    



