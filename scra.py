# Terminal colors and functions
from colorama import Fore
import msvcrt
# Normalization for viz
from sklearn.preprocessing import MinMaxScaler
# Viz
import matplotlib.pyplot as plt
# Data wrangling
from collections import Counter
from math import isnan
import pandas as pd
import numpy as np
# Data scraping
import requests
import bs4
# Sys miscelaneeus
from os import system
import sys
#Date and time
from datetime import date
import datetime
import time


# Requests headers
hdrs = {
    "User agent": "Mozilla/5.0 (Windows NT 10.0Win64x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Safari/537.36"}
idDict = {
    'tab': 'my-lists-tab',
    'items': 'g-items',
    'load_more': 'sort-by-price-load-more-items-url',
    'end': 'endOfListMarker'}

# Miscelaneos
loading = ['/', '|', '\\']
today = date.today()

# Domains
ZARAURL = 'https://www.zara.com/mx/'
AMAZONURL = 'https://www.amazon.com.mx'

# Amazon whishlist
whishlists = {
    'coffee': '/hz/wishlist/ls/104R27JSNG9CF?ref_=wl_share',
    'books': '/hz/wishlist/ls/EB767EYMKQE5?ref_=wl_share',
    'blenders': '/hz/wishlist/ls/3UKQOJ9HIMD7M?ref_=wl_share',
    'baking': '/hz/wishlist/ls/3UKQOJ9HIMD7M?ref_=wl_share',
    'vacuum': '/hz/wishlist/ls/3UKQOJ9HIMD7M?ref_=wl_share'
}


def executedToday():
    return False
    global today
    lastExec = open(
        'C:/Users/asdf1/Documents/BookPriceTracker/lastExec.txt', 'rt')
    if(lastExec.read() == str(today)):
        return True
    lastExec.close()
    lastExec = open(
        'C:/Users/asdf1/Documents/BookPriceTracker/lastExec.txt', 'wt')
    lastExec.write(str(today))
    return False


def waitConnection():
    l = 0
    while(True):
        try:
            requests.get(AMAZONURL, headers=hdrs, timeout=.2)
        except:
            print(f' 接続待ち ... {loading[l]}', end='\r')
            l = (l+1) % 3
            time.sleep(1)
            continue
        break
    return


def menuPrint(options, prompt):
    menu = options
    print(prompt)
    while(True):
        print(f' {menu[0]}', end='\r')
        k = ord(msvcrt.getch())
        if k == 13 or k == 3 or k == 27:
            print('')
            return menu[0]
        elif k == 80:  # Down
            menu = menu[1:]+[menu[0]]
        elif k == 72:  # Up
            menu = [menu[-1]]+menu[:-1]


def updateData(data, path, delta=30):
    df = pd.read_csv(path, index_col='title')
    start_date = datetime.datetime.now() - datetime.timedelta(delta)
    # Drop oldest column
    if len(df.columns) > 30:
        df = df[df.columns[1:]]
    for title, price in data.items():
        df.loc[title, str(today)] = price
    df.to_csv(path)


def retrieveAmazonData(wl_url, path, delta=60):
    global AMAZONURL
    global today
    data = {}
    currBlock = wl_url
    finished = False
    i = 0
    while(not finished):
        # Retrieve wishlist
        try:
            page = requests.get(AMAZONURL+currBlock, headers=hdrs)
        except requests.ConnectionError:
            print('Could not connect. Try again when connected')
            sys.exit()
        # Parse and scrap data
        soup = bs4.BeautifulSoup(page.content, 'html.parser')
        whishlist = soup.find(id=idDict['items'])

        for child in whishlist.find_all("li"):
            priceData = child.find('span', {"class": "a-offscreen"})
            if priceData != None:
                title = child.find('h3').find('a')['title']
                price = priceData.contents[0][1:].replace(',', '')
                data[title] = price
                i += 1
        # Check for end of list
        if(soup.find(id=idDict['end'])):
            finished = True
            break
        else:
            currBlock = soup.find(id=idDict['load_more'])['value']
    # Save data
    updateData(data, path, delta)
    return i


def dataInfo(path, save=False):
    prcsDWN = 0
    prcsUP = 0
    prcsEQ = 0
    mean = 0
    # Setting the plot props
    df = pd.read_csv(path, index_col='title')
    fig = plt.figure(figsize=(20, 10))
    plt.ylim((0, 1200))
    plt.yticks(range(0, 1200, 50))
    plt.grid(True)
    # Data about the data (is this meta ?)
    dates = [x[5:] for x in df.columns]
    for title, prices in df.iterrows():
        lbl, linStyle = '', ''
        # Check if available again
        if not isnan(prices[-1]):
            if isnan(prices[-2]):
                print(f"\t{title} 購入可能! {prices[-1]}")
            # Calculate change in price
            else:
                priceDelta = prices[-2] - prices[-1]
                if priceDelta != 0:
                    print('\t', end='')
                    if priceDelta > 0:
                        print(f"{Fore.GREEN}", end='')
                    else:
                        print(f"{Fore.RED}", end='')
                lbl = (('▲' if (priceDelta < 0) else '▼ ') +
                       '{:.2f}'.format(priceDelta))
                lbl = f'{title[:15].ljust(16)}... : ${prices[-1]} {lbl.rjust(8)}'
                if priceDelta != 0:
                    mean = np.mean(prices)
                    extra_info = ''
                    if prices[-1] < mean:
                        extra_info = f"\t(BELOW MEAN by {'{:.2f}'.format(mean - prices[-1])})"
                    print(f"{lbl}{extra_info}{Fore.RESET}")

                if priceDelta != 0:
                    if priceDelta > 0:
                        linStyle = '-'
                        prcsDWN += 1
                    else:
                        linStyle = ':'
                        prcsUP += 1
                    plt.plot(dates, prices, label=lbl, linestyle='-')
                else:
                    prcsEQ += 1
    if prcsUP == 0 and prcsDWN == 0:
        print('\tNo changes, no plot :c')
        return
    leg = plt.legend(loc='lower center', mode='expand',
                     ncol=3, shadow=True, fancybox=True)
    leg.get_frame().set_alpha(0.5)
    plt.xticks(dates, rotation='vertical')
    if menuPrint(['はい！', 'いええ'], 'プロットを描く?') == 'はい！':
        print('描いている...')
        plt.show()
    if save:
        pass
        fig.savefig(
            'C:/Users/asdf1/Documents/BookPriceTracker/todaysPlot.png', transparent=True)


system('cls')
print(f"今日は {today.year}年{today.month}月{today.day}日 です！")
# Only once a day
if not executedToday():
    # Check for connection
    waitConnection()
    # Start scrapping
    print(f"Amazon を 待っている　\n")
    for wl in whishlists:
        print
    newBooks = retrieveAmazonData(
        whishlists['books'], 'C:/Users/asdf1/Documents/BookPriceTracker/books.csv')
    print(f'{newBooks} 新しい本の価格！')
    # coffeeItems = retrieveAmazonData(
    #     whishlists['coffee'], 'C:/Users/asdf1/Documents/BookPriceTracker/coffee.csv')
    # print(f'{coffeeItems} 新しいコーヒーの価格！')
    homeItems = retrieveAmazonData(
        whishlists['vacuum'], 'C:/Users/asdf1/Documents/BookPriceTracker/home.csv', 180)
    print(f'{homeItems} 新しいコーヒーの価格！')
# Analytics
print(f'{Fore.CYAN}本の価格{Fore.RESET}')
dataInfo('C:/Users/asdf1/Documents/BookPriceTracker/books.csv', False)
print(f'{Fore.CYAN}コーヒーの価格{Fore.RESET}')
dataInfo('C:/Users/asdf1/Documents/BookPriceTracker/coffee.csv', False)
print(f'{Fore.CYAN}家の価格{Fore.RESET}')
dataInfo('C:/Users/asdf1/Documents/BookPriceTracker/home.csv', False)
# Good Bye
print('行われた!')
for i in range(1, 4):
    print(f' さよなら{"!"*i}', end='\r')
    time.sleep(.5)
