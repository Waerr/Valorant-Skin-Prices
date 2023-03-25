from tkinter import *
from utils.currencyMap import CURRENCY_MAP
from utils.getSkins import getPrice


class Window(Frame):
    """Frame displaying all of the info."""
    
    def __init__(self, master=None):
        """Initialize the window."""
        super().__init__(master, bg="#333333")
        self.master = master
        self.pack(fill=BOTH, expand=1)
        
        # Get the current skin price
        try:
            self.amount = getPrice()
        except Exception as e:
            self.amount = 0
            print(f"Error getting skin price: {e}")
        
        # Create the currency menu
        self.menu = StringVar()
        self.menu.set("United States Dollar ($)")
        self.menu.trace_add("write", self.updateLabel)  
        options = list(CURRENCY_MAP.keys())
        currency = OptionMenu(self, self.menu, *options)
        currency.config(width=25, bg="#444444", fg="#FFFFFF", activebackground="#555555", activeforeground="#FFFFFF", highlightthickness=0)
        currency["menu"].config(bg="#444444", fg="#FFFFFF")
        

        # Create the label displaying the currency amount
        self.text = Label(self, text=f"Current Amount for Skins: {self.getCurrency()}", font=("Arial", 12), bg="#333333", fg="#FFFFFF")
        
        # Create the quit button
        quit_button = Button(self, text="Quit", command=self.master.destroy, bg="#555555", fg="#FFFFFF", activebackground="#666666", activeforeground="#FFFFFF", highlightthickness=0)
        
        # Pack the items onto the screen
        self.text.pack(side=TOP, pady=10)
        currency.pack(side=TOP, pady=10)
        quit_button.pack(side=BOTTOM, pady=10)
    
    
    def updateLabel(self, *args):
        """Update the label when a new currency is selected."""
        vp, format_string, price = CURRENCY_MAP[self.menu.get()]
        total = round(self.amount * vp * price)
        self.text.config(text=f"Current Amount for Skins: {format_string.format(total).rstrip('0').rstrip('.')}")

    def getCurrency(self, *args):
        """Get the amount of MONEY for different currency types."""
        vp, format_string, price = CURRENCY_MAP[self.menu.get()]
        total = round(self.amount * vp * price)
        return format_string.format(total).rstrip('0').rstrip('.')


if __name__ == "__main__":
    root = Tk()
    root.configure(bg="#333333")
    app = Window(root)
    root.wm_title("Valorant Skin Prices")
    root.geometry("300x150")
    root.resizable(False, False)
    root.mainloop()
