import matplotlib.pyplot as plt

# each entry in this list is a pair of [series_id : [data]]
fredrequests_history = []

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

    # Create the line graph
    plt.figure(figsize=(10, 6))
    plt.plot(dates, values, marker='o', linestyle='-')
    plt.xlabel('Date')
    plt.ylabel('Value')
    plt.title(f'FRED Data {series_id}')
    plt.xticks(rotation=45)
    plt.grid(True)

    # Display the line graph in a new window
    plt.show()
