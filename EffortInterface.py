import tkinter as gui
from tkinter import StringVar
from tkinter.ttk import OptionMenu
import json
import pathlib
from FinanceFuckAround import *

def retrieve_and_display_data():
    ticker = ticker_entry.get()  # Get the ticker from the entry field
    statement_type = statement_type_var.get()  # Get the selected statement type from the dropdown

    # Download data if it doesn't exist already
    filename = GetFilename(ticker, statement_type)
    if not pathlib.Path(filename).exists():
        data = DownloadFile(ticker, statement_type)
    else:
        # Load the data if it exists
        with open(filename) as file:
            data = json.load(file)

    # Display the data in the text widget
    data_text.delete(1.0, gui.END)  # Clear any existing data in the text widget
    data_text.insert(gui.END, json.dumps(data, indent=4))


def download_data():
    ticker = download_ticker_entry.get()
    statement_type= download_statement_type_entry.get()
    
    DownloadFile(ticker,statement_type)


app = gui.Tk()
app.title("Visualized Effort")

ticker_label = gui.Label(app, text="Enter Ticker:")
ticker_label.pack()

ticker_entry = gui.Entry(app)
ticker_entry.pack()

statement_type_label = gui.Label(app, text="Enter Statement Type:")
statement_type_label.pack()

statement_type_var = StringVar(app)
statement_type_var.set("INCOME_STATEMENT")  # Default value for the dropdown
# listing it twice as a jank-ass workaround to prevent "INCOME_STATEMENT" from disappearing from the drop-down
statement_type_menu = OptionMenu(app, statement_type_var, "INCOME_STATEMENT", "INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW")
statement_type_menu.pack()

retrieve_button = gui.Button(app, text="Retrieve and Display Data", command=retrieve_and_display_data)
retrieve_button.pack()

data_text = gui.Text(app, width=100, height=50)
data_text.pack()

app.mainloop()
