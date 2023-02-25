from tkinter import *
from utils.getSkins import getPrice

# Frame displaying all of the info

class Window(Frame):
    def __init__(self,master=None):
        Frame.__init__(self, master)
        self.master = master
        self.pack(fill=BOTH, expand=1)
        
        self.amount = getPrice()
        options = ["United States Dollar ($)", "Australian Dollar (A$)","Brazilian Real (R$)","Canadian Dollar (CA$)","Euro (€)","Indian Rupee (₹)", "Malaysian Ringgit (MYR)", "Mexican Dollar (MX$)", "New Zealand Dollar (NZ$)", "Russian Ruble (₽)", "Singapore Dollar (SGD)","Turkish Lira (₺)", "Pound Sterling (£)"]

        self.menu = StringVar()
        self.menu.set("United States Dollar ($)")
        self.menu.trace_add("write", self.updateLabel)  
        currency = OptionMenu(self, self.menu, *(options), command = self.getCurrency)
        currency.place(x=66, y=150)

    
        self.text = Label(self, text=f"Current Amount For Skins: {self.getCurrency()}", font=("Arial", 12))
        self.text.place(x=15, y=60)
        
        
        # Quit Button
        quit_button = Button(root, text="Quit", command= root.destroy)
        quit_button.pack(pady=10)
    
    # Updates the label when new currency is selected
    def updateLabel(self, *args):
        self.text.config(text=f"Current Amount For Skins: {self.getCurrency()}")

    # Gets the amount of MONEY for different currency types    
    def getCurrency(self, *args):
        match self.menu.get():
            case "United States Dollar ($)":
                self.VP = (int(self.amount)/11000)
                total = round(self.VP * 99.99)        
                return f"${total:,}"
        
            case "Australian Dollar (A$)":
                self.VP = (int(self.amount)/9750)
                total = round(self.VP * 129.99)
                return f"A${total:,}"
            
            case "Brazilian Real (R$)":
                self.VP = (int(self.amount)/11500)
                total = round(self.VP * 349.9)
                return f"R${total:,}"
            
            case "Canadian Dollar (CA$)":
                self.VP = (int(self.amount)/11000)
                total = round(self.VP * 139.99)
                return f"CA${total:,}"
            
            case "Euro (€)":
                self.VP = (int(self.amount)/11000)
                total = round(self.VP * 100)
                return f"€{total:,}"

            case "Indian Rupee (₹)":
                self.VP = (int(self.amount)/11000)
                total = round(self.VP * 7900)
                return f"₹{total:,}"   
                        
            case "Malaysian Ringgit (MYR)":
                self.VP = (int(self.amount)/6750)
                total = round(self.VP * 199.90)
                return f"MYR{total:,}"            
            
            case "Mexican Dollar (MX$)":
                self.VP = (int(self.amount)/12400)
                total = round(self.VP * 1999)
                return f"MX${total:,}"
        
            case "New Zealand Dollar (NZ$)":
                self.VP = (int(self.amount)/9750)
                total = round(self.VP * 144.99)
                return f"NZ${total:,}"             
        
            case "Russian Ruble (₽)":
                self.VP = (int(self.amount)/11000)
                total = round(self.VP * 5990)
                return f"₽{total:,}"  

            case "Singapore Dollar (SGD)":
                self.VP = (int(self.amount)/10500)
                total = round(self.VP * 128.98)
                return f"SGD{total:,}"  

            case "Turkish Lira (₺)":
                self.VP = (int(self.amount)/8500)
                total = round(self.VP * 700)
                return f"₺{total:,}"  

            case "Pound Sterling (£)":
                self.VP = (int(self.amount)/11500)
                total = round(self.VP * 90)
                return f"£{total:,}"  

# Main Window        
root= Tk()
app = Window(root)
root.wm_title("Valorant Skin Prices")
root.geometry("300x300")
root.mainloop()





