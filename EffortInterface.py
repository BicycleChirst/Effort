import tkinter as gui
from FinanceFuckAround import *

def retrieve_and_display_data():
    ticker = ticker_entry.get()  # Get the ticker from the entry field
    statement_type = statement_type_entry.get()  # Get the statement type from the entry field

    # Download data if it doesn't exist already
    filename = GetFilename(ticker, statement_type)
    if not pathlib.Path(filename).exists():
        DownloadFile(ticker, statement_type)

    # Load the data and display it in the text widget
    with open(filename) as file:
        data = json.load(file)
        data_text.delete(1.0, gui.END)  # Clear any existing data in the text widget
        data_text.insert(gui.END, json.dumps(data, indent=4))

app = gui.Tk()
app.title("Visualized Effort")

ticker_label = gui.Label(app, text="Enter Ticker:")
ticker_label.pack()

ticker_entry = gui.Entry(app)
ticker_entry.pack()

statement_type_label = gui.Label(app, text="Enter Statement Type:")
statement_type_label.pack()

statement_type_entry = gui.Entry(app)
statement_type_entry.pack()

retrieve_button = gui.Button(app, text="Retrieve and Display Data", command=retrieve_and_display_data)
retrieve_button.pack()

data_text = gui.Text(app, width=80, height=50)
data_text.pack()

app.mainloop()
