import requests, lxml, re
from bs4 import BeautifulSoup

def getPrice():
    """HANDLES THE PRICE OF ALL THE SKINS IN VP"""
    
    # THANKS TO VALORANT FANDOM FOR THE VP DATA <3
    vp_url = "https://valorant.fandom.com/wiki/Weapon_Skins"
    vp_html = requests.get(vp_url).text
    vp_soup = BeautifulSoup(vp_html, "lxml")
    
    
    # Find the tables with class fandom-table and extract the prices from the 6th column of each row
    vp_rows = vp_soup.select("table.wikitable.sortable")[1].find_all("tr")[1:]
    vp_prices = []
    for row in vp_rows:
        td_element = row.find("td", {"data-sort-value": True})
        if td_element:
            price_text = re.sub("[\xa0\n,]", "", td_element.text.strip())
            try:
                price = int(price_text)
                vp_prices.append(price)
            except ValueError:
                pass
        else:
            pass

    # Legacy items are those not returning back to the store eg. "Champions Bundle"
    # Find the table with class fandom-table and extract the prices from the Notes column
    # legacy_table = vp_soup.find_all("div", class_="wds-tab__content")[3]
    # legacy_rows = legacy_table.select("table.fandom-table")[0].find_all("tr")[1:]
    
    # Regex to find the Price from the Notes Column as an int
    # legacy_prices = [int(''.join(filter(str.isdigit, re.findall(r'\d{1,3}(?:,\d{3})+', 
    #                 row.find_all("td")[3].text.strip())[0]))) 
    #                 for row in legacy_rows if re.findall(r'\d{1,3}(?:,\d{3})+', row.find_all("td")[3].text.strip())]  
    # legacy_prices = [int(price) for price in legacy_prices]
    
    
    
    return (sum(vp_prices))