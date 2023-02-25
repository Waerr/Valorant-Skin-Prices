import requests, lxml, re
from bs4 import BeautifulSoup
import pandas as pd


def getPrice():
    """HANDLES THE PRICE OF ALL THE SKINS IN VP"""
    
    # THANKS FOR VALORANT FANDOM FOR THE VP DATA <3
    url = "https://valorant.fandom.com/wiki/Weapon_Skins"
    html = requests.get(url).text

    soup = BeautifulSoup(html, "lxml")

    price = soup.find_all("table", attrs={"class": "wikitable"})

    ptable = price[1]
    body = ptable.find_all("tr")
    head = body[0]
    body_rows = body[1:]
    headings = []

    for item in head.find_all("th"):

        item = (item.text).rstrip("\n")

        headings.append(item)

    all_rows = []

    for row_num in range(len(body_rows)):
        row = []

        for row_item in body_rows[row_num].find_all("td"):

            aa = re.sub("(\xa0)|(\n)|,","",row_item.text)

            row.append(aa)

        all_rows.append(row)

    # CONVERTS THE FORMATTED SCRAPED DATA INTO A DATAFRAME 
    df = pd.DataFrame(data=all_rows[1:], columns=headings)

    # DATAFRAME IS CONVERTED TO CSV
    df.to_csv('Prices.csv', index=None)
    
    # WE READ THE CSV TO CALCULATE THE TOTAL WHICH IS RETURNED
    pricedf = pd.read_csv('Prices.csv', sep=',')
    amount = pricedf[['Price']].sum()
    return amount