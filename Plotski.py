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

plot_multiselect_keys = []

def PlotWantedKeys():
    testfile = LOADED_FILES[f"{plot_ticker_var}_{plot_statementtype_var}"]
    # convert all fields to floats, get rid of 'None's, reverse order of dates
    testfile = ConvertJSONnumbers(testfile, True)
    quarters = testfile["quarterlyReports"]

    # Create a custom formatter to format the y-axis labels
    def y_axis_formatter(x, pos):
        if x == 0: return '0'
        abs_x = abs(x)
        if abs_x >= 1e9:
            formatted_x = f'{abs_x / 1e9:.1f}B'
        else:
            formatted_x = f'{abs_x / 1e6:.1f}M'
        formatted_x = testfile["CurrencySymbol"] + formatted_x
        # Add a minus sign for negative values
        if x < 0: formatted_x = '-' + formatted_x
        return formatted_x

    # setup
    plt.figure(figsize=(10, 10))
    plt.xlabel('Date')
    plt.annotate(f'Values in {testfile["Currency"]}', (0, 1), xycoords='axes fraction', rotation=0)
    plt.title(f'{testfile["symbol"]} {testfile["StatementType"]} {str(WantedKeys[testfile["StatementType"]])}')
    plt.xticks(rotation=45)
    plt.gca().yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))  # apply formatter to y-axis
    plt.grid(True)

    dates = [Q['fiscalDateEnding'] for Q in quarters]
    for K in WantedKeys[testfile["StatementType"]]:
        plt.plot(dates, [Q[K] for Q in quarters], marker='o', linestyle='-')

    plt.show()


def plotJSON():
    #testfile = LOADED_FILES["AMD_INCOME_STATEMENT"]
    testfile = LOADED_FILES[f"{plot_ticker_var}_{plot_statementtype_var}"]
    quarters = testfile["quarterlyReports"]
    PrintJSON(testfile)

    dates = [*reversed([Q['fiscalDateEnding'] for Q in quarters])]
    dataski = []
    print(plot_key_var)

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

    reported_currency = quarters[0]['reportedCurrency']
    currency_symbol = currency_symbolmap[reported_currency]

    # Create a custom formatter to format the y-axis labels
    def y_axis_formatter(x, pos):
        if x == 0: return '0'
        abs_x = abs(x)
        if abs_x >= 1e9:
            formatted_x = f'{abs_x / 1e9:.1f}B'
        else:
            formatted_x = f'{abs_x / 1e6:.1f}M'
        formatted_x = currency_symbol + formatted_x
        # Add a minus sign for negative values
        if x < 0: formatted_x = '-' + formatted_x
        return formatted_x

    plt.figure(figsize=(10, 10))
    plt.plot(dates, dataski, marker='o', linestyle='-')
    plt.xlabel('Date')
    plt.annotate(f'Values in {reported_currency}',(0,1),xycoords='axes fraction',rotation=0)
    plt.title(f'{testfile["symbol"]} {testfile["StatementType"]} {plot_key_var}')
    plt.xticks(rotation=45)

    plt.gca().yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))  #apply formatter to y-axis

    plt.grid(True)
    plt.show()


def plotMultiSelect():
    testfile = LOADED_FILES[f"{plot_ticker_var}_{plot_statementtype_var}"]
    quarters = testfile["quarterlyReports"]

    dates = [*reversed([Q['fiscalDateEnding'] for Q in quarters])]
    dataski = []
    for AK in plot_multiselect_keys:
        dataski.append( [*reversed([Q[AK] for Q in quarters])] )

    reported_currency = quarters[0]['reportedCurrency']
    currency_symbol = currency_symbolmap[reported_currency]

    # Create a custom formatter to format the y-axis labels
    def y_axis_formatter(x, pos):
        if x == 0: return '0'
        abs_x = abs(x)
        if abs_x >= 1e9:
            formatted_x = f'{abs_x / 1e9:.1f}B'
        else:
            formatted_x = f'{abs_x / 1e6:.1f}M'
        formatted_x = currency_symbol + formatted_x
        # Add a minus sign for negative values
        if x < 0: formatted_x = '-' + formatted_x
        return formatted_x

    fig, ax1 = plt.subplots(figsize=(10, 10))
    ax1.set_xlabel('Date')

    # Create the first y-axis on the left side (primary y-axis)
    ax1.set_ylabel(f'Values in {reported_currency}', color='tab:blue')
    ax1.tick_params(axis='y', labelcolor='tab:blue')

    # Plot the first set of data on the left y-axis
    for AK in enumerate(plot_multiselect_keys):
        ax1.plot(dates, quarters[AK], label=AK, marker='o', linestyle='-', color='tab:green')

    ax1.legend(loc='upper left')

    # Create the second y-axis on the right side (secondary y-axis)
    ax2 = ax1.twinx()
    ax2.set_ylabel(f'Values in {reported_currency}', color='tab:red')
    ax2.tick_params(axis='y', labelcolor='tab:red')

    # Plot the second set of data on the right y-axis
    for AK in enumerate(plot_multiselect_keys):
        ax2.plot(dates, quarters[AK], label=AK, marker='s', linestyle='--', color='tab:red')

    ax2.legend(loc='upper right')

    plt.title(f'{testfile["symbol"]} {testfile["StatementType"]} {", ".join(plot_multiselect_keys)}')
    plt.xticks(rotation=45)

    # Apply the custom formatter to both y-axes
    ax1.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))
    ax2.yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))

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
