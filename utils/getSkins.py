import requests, lxml, re
from bs4 import BeautifulSoup


def getPrice():
    """HANDLES THE PRICE OF ALL THE SKINS IN VP"""
    
    # THANKS TO VALORANT FANDOM FOR THE VP DATA <3
    vp_url = "https://valorant.fandom.com/wiki/Weapon_Skins"
    vp_html = requests.get(vp_url).text
    vp_soup = BeautifulSoup(vp_html, "lxml")

    # Find the tables with class wikitable and extract the prices from the 6th column of each row
    vp_rows = vp_soup.select("table.wikitable")[1].find_all("tr")[1:]
    vp_prices = [re.sub("[\xa0\n,]", "", row.find_all("td")[4].text.strip()) for row in vp_rows]
    vp_prices = [int(price) for price in vp_prices]

    # Legacy items are those not returning to back to store eg. "Champions Bundle"
    # Find the table with class sortable and extract the prices from the Notes column
    legacy_rows = vp_soup.select("table.sortable")[4].find_all("tr")[1:]
    legacy_prices = [int(re.findall("\d{4}$", row.find_all("td")[3].text.strip())[0]) for row in legacy_rows if re.findall("\d{4}$", row.find_all("td")[3].text.strip())]
    legacy_prices = [int(price) for price in legacy_prices]
    
    
    
    return (sum(legacy_prices + vp_prices))


    
    
        
