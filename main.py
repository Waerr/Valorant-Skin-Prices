import requests, re, lxml
from tkinter import *
from bs4 import BeautifulSoup
import pandas as pd


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


df = pd.DataFrame(data=all_rows[1:], columns=headings)

df.to_csv('Prices.csv', index=None)


pricedf = pd.read_csv('Prices.csv', sep=',')

amount = pricedf[['Price']].sum()

VP = (int(amount)/11500)
total = round(VP * 90)


class Window(Frame):
    def __init__(self,master=None):
        Frame.__init__(self, master)
        self.master = master
        self.pack(fill=BOTH, expand=1)
        text = Label(self, text=f"Current Amount For Skins: £{total}", font=("Arial", 20))
        text.place(x=37, y=60)
        quit_button = Button(root, text="Quit", command= root.destroy)
        quit_button.pack(pady=10)

root= Tk()
app = Window(root)
root.wm_title("Valorant Skin Prices")
root.geometry("500x150")
root.mainloop()



