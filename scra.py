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
import sys

def pltData(save=False):
    df = pd.read_csv('./priceData.csv') 
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
        priceDelta = titlesMap[key][0][-2] - \
            titlesMap[key][0][-1] if len(titlesMap[key][0]) > 2 else 0
        if priceDelta != 0:
            mostChange[key] = priceDelta

    deltas = [delta for title, delta in mostChange.most_common(30)]
    deltas = np.array(deltas).reshape(-1, 1)
    scaler = MinMaxScaler((0, 1))
    deltas = scaler.fit_transform(deltas)
    deltas = [x[0] if x[0] < 1 else 1 for x in deltas]
    i = 0
    for item in mostChange.most_common(30):
        title = item[0]
        prices = titlesMap[title][0]
        dates = titlesMap[title][1]
        priceDelta = (prices[-1] - prices[-2]) if len(prices) > 2 else 0
        dev = 10 * np.std(prices)/np.mean(prices)
        dev = 1 if dev > 1 else dev
        label = (('▲' if (priceDelta > 0) else '▼ ') + '{:.2f}'.format(priceDelta))
        label = f'{title[:15].ljust(16)}... : ${prices[-1]} {label.rjust(8)}'
        plt.plot(dates, prices, linestyle='-',
                alpha=deltas[i], marker='o', label=label)
        i += 1
    leg = plt.legend(loc='lower center', mode='expand',
                    ncol=3, shadow=True, fancybox=True)
    leg.get_frame().set_alpha(0.5)
    plt.show()
    if save:
        fig.savefig(
            'C:/Users/asdf1/Documents/AmazonBooksData/todaysPlot.png', transparent=True)

hdrs = {"User agent": "Mozilla/5.0 (Windows NT 10.0Win64x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}

# idDict = {
#     'tab': 'my-lists-tab',
#     'items': 'g-items',
#     'load_more': 'sort-by-price-load-more-items-url',
#     'end': 'endOfListMarker'}

# AMAZONURL = 'https://www.amazon.com.mx'
# currBlock = '/hz/wishlist/ls/EB767EYMKQE5?ref_=wl_share'
# finished = False

# ###Check for connection
# while(True):
#     try:
#         requests.get(AMAZONURL,headers = hdrs)
#     except:
#         input('Couldnt connect. Press any key to retry')
#         continue
#     break

# ###Only once a day
# today = str(date.today())
# lastExec = open('C:/Users/asdf1/Documents/AmazonBooksData/lastExec.txt', 'rt')
# if(lastExec.read() == today):
#     print('Already done for today')
#     pltData(False)
#     sys.exit()
# lastExec.close()
# lastExec = open('C:/Users/asdf1/Documents/AmazonBooksData/lastExec.txt', 'wt')
# lastExec.write(today)

# data = []
# while(not finished):
#     #Retrieve wishlist
#     try:
#         page = requests.get(AMAZONURL+currBlock,headers = hdrs)
#     except requests.ConnectionError:
#         print('Could not connect. Try again when connected')
#         sys.exit()
#     ##Parse and scrap data
#     soup = bs4.BeautifulSoup(page.content,'html.parser')
#     whishlist = soup.find(id=idDict['items'])
#     for child in whishlist.find_all("li"):
#         priceData = child.find('span',{"class":"a-offscreen"})
#         if priceData != None:
#             data.append([today,child.find('h3').find('a')['title'],priceData.contents[0][1:]]) 
#     ##Check for end of list
#     if(soup.find(id = idDict['end'])):
#         finished = True
#         break
#     else:
#         currBlock = soup.find(id = idDict['load_more'])['value']
# #Save data
# todaysDf = pd.DataFrame(data = data, columns=['date','title','price'])
# todaysDf.to_csv('C:/Users/asdf1/Documents/AmazonBooksData/priceData.csv',header=False, mode='a', index=False)
pltData(True)



