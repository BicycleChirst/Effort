import tkinter as gui
from tkinter import StringVar
from tkinter.ttk import OptionMenu, Notebook
import json
import pathlib
from JSONwithDADMIN import *
from FedGiveIt import *


def retrieve_and_display_data():
    import JSONwithDADMIN
    ticker = ticker_entry.get()  # Get the ticker from the entry field
    statement_type = statement_type_var.get()  # Get the selected statement type from the dropdown
    JSONwithDADMIN.ReportingPeriod = report_type_var.get()

    # Download data if it doesn't exist already
    filename = ticker + "_" + statement_type
    if filename not in LOADED_FILES:
        print("don't have that file")
        DownloadFile(ticker, statement_type)
        LoadAllFiles()
    data = LOADED_FILES[filename]

    # Display the data in the text widget
    data_text.delete(1.0, gui.END)  # Clear any existing data in the text widget
    data_text.insert(gui.END, json.dumps(FormatJSON(data), indent=4))

fredrequests_history = []

def retrieve_and_display_fred_data():
    Get_Fred_Inputs()
    print("entry values: ")
    print(series_id_entry.get())
    print(start_date_entry.get())
    print(end_date_entry.get())
    print("stored input variables: ")
    print(fred_series_id_input)
    print(fred_start_date_input)
    print(fred_end_date_input)
    return

    # Call the FRED data retrieval function
    key_indicators_data = get_series_data(fred_series_id_input, fred_start_date_input, fred_end_date_input)

    # Display the data in the FRED text widget
    fred_data_text.delete(1.0, gui.END)  # Clear any existing data in the text widget

    if key_indicators_data:
        fred_data_text.insert(gui.END, "Date\t\tValue\n")
        fred_data_text.insert(gui.END, "----------------------\n")
        for data in key_indicators_data:
            fred_data_text.insert(gui.END, f"{data['date']}\t{data['value']}\n")
    else:
        fred_data_text.insert(gui.END, "No data available.")
    
    fredrequests_history.append(key_indicators_data)


app = gui.Tk()
app.title("Visualized Effort")

# Create the Notebook widget to manage different pages
notebook = Notebook(app)
notebook.pack(fill='both', expand=True)

# Financial statement retrieval page
financial_statement_frame = gui.Frame(notebook)

ticker_label = gui.Label(financial_statement_frame, text="Enter Ticker:")
ticker_label.pack()

ticker_entry = gui.Entry(financial_statement_frame)
ticker_entry.pack()

statement_type_label = gui.Label(financial_statement_frame, text="Enter Statement Type:")
statement_type_label.pack()

statement_type_var = StringVar(financial_statement_frame)
statement_type_var.set("INCOME_STATEMENT")  # Default value for the dropdown
statement_type_menu = OptionMenu(financial_statement_frame, statement_type_var, "INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW", "INCOME_STATEMENT")
statement_type_menu.pack()

report_type_var = StringVar(financial_statement_frame)
report_type_var.set("annualReports")  # Default value for the dropdown
report_type_menu = OptionMenu(financial_statement_frame, report_type_var, "annualReports", "quarterlyReports")
report_type_menu.pack()

retrieve_statement_button = gui.Button(financial_statement_frame, text="Retrieve and Display Data", command=retrieve_and_display_data)
retrieve_statement_button.pack()

# Add the financial statement frame to the Notebook widget with the label "Financial Statement"
notebook.add(financial_statement_frame, text="Financial Statement")

# FRED data page
fred_data_frame = gui.Frame(notebook)

series_id_label = gui.Label(fred_data_frame, text="Enter FRED Series ID:")
series_id_label.pack()

series_id_entry = gui.Entry(fred_data_frame)
series_id_entry.pack()

start_date_label = gui.Label(fred_data_frame, text="Enter Start Date (YYYY-MM-DD):")
start_date_label.pack()

start_date_entry = gui.Entry(fred_data_frame)
start_date_entry.pack()

end_date_label = gui.Label(fred_data_frame, text="Enter End Date (YYYY-MM-DD):")
end_date_label.pack()

end_date_entry = gui.Entry(fred_data_frame)
end_date_entry.pack()

retrieve_fred_data_button = gui.Button(fred_data_frame, text="Retrieve and Display FRED Data", command=retrieve_and_display_fred_data)
retrieve_fred_data_button.pack()

data_text = gui.Text(financial_statement_frame, width=100, height=50)
data_text.pack()

# Create a text widget to display FRED data
fred_data_text = gui.Text(fred_data_frame, width=100, height=45)
fred_data_text.pack()

# Add the FRED data frame to the Notebook widget with the label "FRED Data"
notebook.add(fred_data_frame, text="FRED Data")

#setting defaults for entry fields
series_id_entry.insert(index=0, string="UNRATE")
start_date_entry.insert(index=0, string="2015-12-31")
end_date_entry.insert(index=0, string="2022-12-31")

fred_series_id_input = series_id_entry.get()
fred_start_date_input = start_date_entry.get()
fred_end_date_input = end_date_entry.get()

def Get_Fred_Inputs():
    fred_series_id_input = series_id_entry.get()  # Get the series ID from the entry field
    fred_start_date_input = start_date_entry.get()  # Get the start date from the entry field
    fred_end_date_input = end_date_entry.get()  # Get the end date from the entry field

    print(series_id_entry.get())
    print(start_date_entry.get())
    print(end_date_entry.get())



# only open the GUI if this script is run directly
if __name__ == "__main__":
    app.mainloop()