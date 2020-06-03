#Normalization for viz
from sklearn.preprocessing import MinMaxScaler
#Viz
import matplotlib.pyplot as plt
#Data wrangling
from collections import Counter
import pandas as pd
import numpy as np
#Data scraping
import requests
import bs4
#Miscelaneeus
from datetime import date
from os import system
import sys
import time


#Requests headers 
hdrs = {"User agent": "Mozilla/5.0 (Windows NT 10.0Win64x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}
idDict = {
    'tab': 'my-lists-tab',
    'items': 'g-items',
    'load_more': 'sort-by-price-load-more-items-url',
    'end': 'endOfListMarker'}

#Miscelaneos    
loading = ['/','|','\\']
today = date.today()

#Domains
ZARAURL = 'https://www.zara.com/mx/'
AMAZONURL = 'https://www.amazon.com.mx'

#Amazon whishlist
whishlists = {
    'coffe':'/hz/wishlist/ls/104R27JSNG9CF?ref_=wl_share',
    'books':'/hz/wishlist/ls/EB767EYMKQE5?ref_=wl_share'
}

def executedToday():
    global today
    lastExec = open('C:/Users/asdf1/Documents/BookPriceTracker/lastExec.txt', 'rt')
    if(lastExec.read() == str(today)):
        return True
    lastExec.close()
    lastExec = open('C:/Users/asdf1/Documents/BookPriceTracker/lastExec.txt', 'wt')
    lastExec.write(today)
    return False


def chckConnection():
    l = 0
    while(True):
        try:
            requests.get(AMAZONURL,headers = hdrs,timeout=.2)
        except:
            print(f' 接続待ち ... {loading[l]}',end = '\r')
            l = (l+1)%3
            time.sleep(1)
            continue
        break

def retrieveAmazonData(wl_url,path):
    global AMAZONURL
    data = []
    currBlock = wl_url
    finished = False
    i = 0
    while(not finished):
        #Retrieve wishlist
        try:
            page = requests.get(AMAZONURL+currBlock,headers = hdrs)
        except requests.ConnectionError:
            print('Could not connect. Try again when connected')
            sys.exit()
        ##Parse and scrap data
        soup = bs4.BeautifulSoup(page.content,'html.parser')
        whishlist = soup.find(id=idDict['items'])
        for child in whishlist.find_all("li"):
            priceData = child.find('span',{"class":"a-offscreen"})
            if priceData != None:
                data.append([today,child.find('h3').find('a')['title'],priceData.contents[0][1:].replace(',','')]) 
                i+=1
        ##Check for end of list
        if(soup.find(id = idDict['end'])):
            finished = True
            break
        else:
            currBlock = soup.find(id = idDict['load_more'])['value']
    #Save data
    todaysDf = pd.DataFrame(data = data, columns=['date','title','price'])
    todaysDf.to_csv(path,header=False, mode='a', index=False)
    return i

def pltData(path,save=False):
    df = pd.read_csv(path)
    fig = plt.figure(figsize=(20, 10))
    plt.ylim((0, 1000))
    plt.yticks(range(0, 1000, 100))
    plt.grid(True)

    titlesMap = {title: [[], []] for title in df['title'].unique()}
    for row in df.iterrows():
        title = row[1]['title']
        titlesMap[title][0].append(row[1]['price'])
        titlesMap[title][1].append(row[1]['date'])

    mostChange = Counter()
    for key, val in titlesMap.items():
        priceDelta = titlesMap[key][0][-2] - titlesMap[key][0][-1] if len(titlesMap[key][0]) > 2 else 0
        if priceDelta != 0:
            mostChange[key] = priceDelta

    deltas = [delta for title, delta in mostChange.most_common(30)]
    deltas = np.array(deltas).reshape(-1, 1)
    scaler = MinMaxScaler((0, 1))
    deltas = scaler.fit_transform(deltas)
    deltas = [x[0] if x[0] < 1 else 1 for x in deltas]
    i = 0
    dateSet = set()
    for item in mostChange.most_common(30):
        title = item[0]
        prices = titlesMap[title][0]
        dates = titlesMap[title][1]
        dates = [x[5:] for x in dates]
        priceDelta = (prices[-1] - prices[-2]) if len(prices) > 2 else 0
        dev = 10 * np.std(prices)/np.mean(prices)
        dev = 1 if dev > 1 else dev
        label = (('▲' if (priceDelta > 0) else '▼ ') + '{:.2f}'.format(priceDelta))
        label = f'{title[:15].ljust(16)}... : ${prices[-1]} {label.rjust(8)}'
        plt.plot(dates, prices, linestyle='-',alpha=min(1,deltas[i]+.3), marker='o', label=label)
        dateSet.update(dates)
        i += 1
    dateSet = list(dateSet)
    plt.xticks(dateSet,rotation='vertical')
    leg = plt.legend(loc='lower center', mode='expand',
                    ncol=3, shadow=True, fancybox=True)
    leg.get_frame().set_alpha(0.5)
    plt.show()
    if save:
        fig.savefig(
            'C:/Users/asdf1/Documents/BookPriceTracker/todaysPlot.png', transparent=True)


system('cls')
print(f"今日は {today.year}年{today.month}月{today.day}日 です！\n")
###Only once a day
if executedToday():
    print('行われた!')
else:
    ###Check for connection
    chckConnection()
    ### Start scrapping
    print(f"Amazon を 待っている　\n")
    newBooks = retrieveAmazonData(whishlists['books'],'C:/Users/asdf1/Documents/BookPriceTracker/books.csv')
    print(f'{newBooks} 新しい本の価格！')
    print(f"ZARA を 待っている　\n")
    

if 'y' == input('Would you like to plot the data?'):
    pltData('C:/Users/asdf1/Documents/BookPriceTracker/books.csv',True)


for i in range(1,4):
    print(f' さよなら{"!"*i}',end='\r')
    time.sleep(1.5)
sys.exit(0)






