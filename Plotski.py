import matplotlib.pyplot as plt

# each entry in this list is a pair of [series_id : [data]]
fredrequests_history = []
# number of months between dates shown on the plot
date_spacing = 12

from EffortEngine import *

def plotJSON():
    testfile = LOADED_FILES["AMD_INCOME_STATEMENT"]
    quarters = testfile["quarterlyReports"]
    PrintJSON(testfile)

    dates = [*reversed([Q['fiscalDateEnding'] for Q in quarters])]
    dataski = [float(Q['grossProfit']) for Q in quarters]

    print(dates)
    print(dataski)

    plt.figure(figsize=(10, 10))
    plt.plot(dates, dataski, marker='o', linestyle='-')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.title(f'Testgraph')
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.show()


def plot_fred_data():
    # for some reason our requests are lists inside of lists
    series_id, data = fredrequests_history[-1:][0]
    # Check if data is available
    if not data:
        print("empty data in plot function")
        return

    # Extract dates and values from the data
    dates = [item['date'] for item in data]
    values = [float(item['value']) for item in data]

    # list of dates at date_spacing interval
    yearsonly = dates[::date_spacing]

    # Create the line graph
    plt.figure(figsize=(10, 6))
    plt.plot(dates, values, marker='o', linestyle='-')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.title(f'FRED Data {series_id}')
    #plt.xticks(ticks=[]) # remove all dates from display
    plt.xticks(ticks=yearsonly, rotation=45)
    plt.grid(True)

    # Display the line graph in a new window
    plt.show()
