import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
# each entry in this list is a pair of [series_id : [data]]
fredrequests_history = []
# number of months between dates shown on the plot
date_spacing = 12
from JSONwithDADMIN import *


plot_key_var = 'netIncome'
plot_statementtype_var = 'INCOME_STATEMENT'
plot_ticker_var = 'EH'

def plotJSON():
    #testfile = LOADED_FILES["AMD_INCOME_STATEMENT"]
    testfile = LOADED_FILES[f"{plot_ticker_var}_{plot_statementtype_var}"]
    quarters = testfile["quarterlyReports"]
    PrintJSON(testfile)

    dates = [*reversed([Q['fiscalDateEnding'] for Q in quarters])]
    dataski = []
    reported_currency = [Q['reportedCurrency'] for Q in quarters]
    for Q in quarters:
        value = Q[plot_key_var]
        if value is not None:
            try:
                numeric_value = float(value)
                dataski.append(numeric_value)
            except ValueError:
                print(f"Could not convert value to float: {value}")
                dataski.append(0)
        else:
            dataski.append(0)

    dataski = [*reversed(dataski)]
    print(dates)
    print(dataski)

    # Create a custom formatter to format the y-axis labels
    def y_axis_formatter(x, pos):
        if x == 0:
            return '0'
        abs_x = abs(x)
        if abs_x >= 1e9:
            formatted_x = f'{abs_x / 1e9:.1f}B'
        elif abs_x >= 1e6:
            formatted_x = f'{abs_x / 1e6:.1f}M'
        else:
            formatted_x = f'{abs_x:.0f}'

        # Add a minus sign for negative values
        if x < 0:
            formatted_x = '-' + formatted_x

        return formatted_x

    plt.figure(figsize=(10, 10))
    plt.plot(dates, dataski, marker='o', linestyle='-')
    plt.xlabel('Date')
    plt.annotate(f'Values in {reported_currency[0]}',(0,1),xycoords='axes fraction',rotation=0)
    plt.title(f'{testfile["symbol"]} {testfile["StatementType"]} {plot_key_var}')
    plt.xticks(rotation=45)

    plt.gca().yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))  #apply formatter to y-axis

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
