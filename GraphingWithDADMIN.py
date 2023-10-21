import tkinter
from JSONwithDADMIN import *

import matplotlib
from matplotlib import pyplot
from matplotlib.ticker import FuncFormatter

# for some reason importing pyplot changes the behavior of Tk in Pycharm's console;
# it prints a message:
# 'Backend TkAgg is interactive backend. Turning interactive mode on.'
# and then immediately opens the tkWindow if/when it's defined

# normal python3/ipython is using 'QtAgg'
# for some reason ipython also prints: 'Installed qt5 event loop hook.'
# interactive console uses 'TkAgg'

# matplotlib.use('QtAgg', force=True)
print(f"matplotlib backend is using: {matplotlib.get_backend()}")
print(f"""interactive status:
    matplotlib: {matplotlib.is_interactive()}
    pyplot: {pyplot.isinteractive()}
""")

# backend supported values are:
# [ 'GTK3Agg', 'GTK3Cairo', 'GTK4Agg', 'GTK4Cairo',
# 'MacOSX', 'nbAgg',
# 'QtAgg', 'QtCairo', 'Qt5Agg', 'Qt5Cairo',
# 'TkAgg', 'TkCairo',
# 'WebAgg',
# 'WX', 'WXAgg', 'WXCairo',
# 'agg', 'cairo', 'pdf', 'pgf', 'ps', 'svg', 'template' ]


helptext = """
Single-clicks will completely replace current selection
To multi-select:
    Click and drag inside a list to select a whole block of lines
    Ctrl+Click to add/remove a line from the current selection
    Shift+Click to add a range (while keeping current selections)
ESC to deselect anything in the current list
"""

tkWindow = tkinter.Tk()
tkWindow.minsize(960, 640)
tkWindow.wm_title("-- Graphing With DADMIN --")
topframe = tkinter.Frame(tkWindow, relief=tkinter.RIDGE, borderwidth=2)
topframe.pack(fill=tkinter.BOTH, expand=tkinter.NO)
tkinter.Label(topframe, text=helptext).pack()
#tkinter.Button(topframe, text="Exit", command=tkWindow.destroy, name="exitbutton")\
#    .pack(fill="none", side=tkinter.BOTTOM)

CallbackList = []

tickerbox_frame = tkinter.LabelFrame(tkWindow, text="Tickers")
tickerbox_frame.pack(fill="both", expand=tkinter.YES, side=tkinter.LEFT, padx=5, pady=5)
# "extended" allows dragging to select a range of items, "multiple" does not
#   however, single-clicks will replace the current selection instead of adding to it
# disabling "exportselection" prevents the selection from being cleared when the list loses focus
ticker_listbox = tkinter.Listbox(tickerbox_frame, selectmode="extended", exportselection=False)
ticker_listbox.pack(side=tkinter.TOP, expand=tkinter.YES, fill="both", padx=5, pady=5)
ticker_listbox.insert(tkinter.END, *sorted(StatementMap.keys()))

tickerbox_selections = []
def tickerbox_callback():
    global tickerbox_selections
    tickerbox_selections = [ticker_listbox.get(I) for I in ticker_listbox.curselection()]
    print(tickerbox_selections)
tkinter.Button(tickerbox_frame, text="print ticker selections", command=tickerbox_callback)\
    .pack(fill="x", side=tkinter.BOTTOM)
CallbackList.append(tickerbox_callback)

keybox_selections = {}
for (K, L) in Keytable.items():
    if K == "SPECIAL": continue
    newframe = tkinter.LabelFrame(tkWindow, text=f"{K}")
    newframe.pack(fill="both", expand=tkinter.YES, side=tkinter.LEFT, padx=5, pady=5)
    newbox = tkinter.Listbox(newframe, selectmode="extended", exportselection=False)
    newbox.pack(side=tkinter.TOP, expand=tkinter.YES, fill="both", padx=5, pady=5)
    newbox.insert(tkinter.END, *sorted(L))
    keybox_selections[K] = []
    # defining parameters (which default to local variables) is required for lamba-like behavior
    def newbox_callback(B=newbox, bk=K):
        keybox_selections[bk] = [B.get(I) for I in B.curselection()]
        print(keybox_selections[bk])
    tkinter.Button(newframe, text=f"print {K} selections", command=newbox_callback)\
        .pack(fill="x", side=tkinter.BOTTOM)
    CallbackList.append(newbox_callback)
# TODO: set height of Listbox to the length of the list or ensure widow height is enough


def AllCallbacks():
    for Callback in CallbackList:
        Callback()
    print('\n')

tkinter.Button(topframe, text=f"GRAPH", command=AllCallbacks).pack(fill="both", side=tkinter.BOTTOM)


# 'pos' appears to be a magic variable
def y_axis_formatter(y, pos, currency='$'):
    if y == 0: return '0'
    abs_y = abs(y)
    if abs_y >= 1e9:
        formatted_y = f'{abs_y / 1e9:.1f}B'
    else:
        formatted_y = f'{abs_y / 1e6:.1f}M'
    formatted_y = currency + formatted_y
    # Add a minus sign for negative values
    if y < 0: formatted_y = '-' + formatted_y
    return formatted_y
# TODO: store currency-symbol in a global variable or bind it in a lambda or something


def LoadSelectedFiles():
    if not tickerbox_selections:  # if empty
        print("Error: No Tickers selected")
        return
    WantedKeys.update(keybox_selections)
    # ^ this only works because keybox_selections puts an empty list in the field
    # ('update' does not delete/empty non-existent keys)
    # can't be iterating through WantedKeys when you delete
    for (KK, KL) in keybox_selections.items():
        if not KL:  # empty list
            del WantedKeys[KK]
    if not WantedKeys:
        print("Error: No fields selected")
        return

    # {Ticker : [json-objects]}
    SelectedFilemap = {}
    for ticker in tickerbox_selections:
        SelectedFilemap[ticker] = []
        print(f"loading statements for: {ticker}")
        for statementtype in WantedKeys.keys():
            if statementtype not in StatementMap[ticker]:
                print(f"\tWARNING: skipping {statementtype}; file does not exist")
                continue
            print(f"\tloading {statementtype}")
            file = LOADED_FILES[f"{ticker}_{statementtype}"]
            file = ConvertJSONnumbers(file, True)
            # ^ convert all fields to floats, get rid of 'None's, reverse order of dates
            SelectedFilemap[ticker].append(file)
        # removing ticker if no files were loaded for it
        if not SelectedFilemap[ticker]:
            del SelectedFilemap[ticker]

    print("loaded all Selected Files")
    return SelectedFilemap


# TODO: figure out if annualReports are purely redundant (always overlap with quarterly)
# TODO: figure out if duplicate keys across statement-types are equivalent
    # like 'netIncome' in both 'INCOME_STATEMENT' and 'CASH_FLOW'

def ExtractData(filemap):
    extracted_data = {}
    for (ticker, filelist) in filemap.items():
        newdata = {}
        sharedinfoExtracted = False  # flag prevent redundant updates of info shared across statements
        for statement in filelist:
            if not sharedinfoExtracted:
                # we just grab the top-level info from the first statement and assume it's the same for all of them
                newdata.update({
                    'symbol':         ticker,
                    'Currency':       statement['Currency'],
                    'CurrencySymbol': statement['CurrencySymbol'],
                    'Dates':          statement['Dates']['quarterly'],
                    'TargetKeys':     []
                })
                sharedinfoExtracted = True
            targetkeys = WantedKeys[statement['StatementType']]
            newdata['TargetKeys'].extend(targetkeys)
            for tk in targetkeys:
                newdata.update({tk: [R[tk] for R in statement['quarterlyReports']]})
        extracted_data.update({ticker: newdata})
    return extracted_data


def Graph():
    # assume that all other callbacks have triggered
    filemap = LoadSelectedFiles()
    datamap = ExtractData(filemap)
    for (ticker, data) in datamap.items():
        # 'num' is an ID that's mapped to the figure
        figure = pyplot.figure(num=f"{ticker}_Fig", figsize=(10, 10))
        figure.suptitle(f"{ticker}")
        figure.supxlabel('Date')
        figure.supylabel(f'Values in {data["Currency"]}')
        ax = figure.subplots()
        ax.grid(True)
        pyplot.xticks(rotation=45)
        pyplot.gca().yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))  # apply formatter to y-axis
        for targetkey in data['TargetKeys']:
            #print(f"{targetkey}: {data[targetkey]}")
            ax.plot(data['Dates'], data[targetkey], marker='o', linestyle='-', label=f"{targetkey}")
        ax.legend()
    pyplot.show()
    #pyplot.show(block=False)   # freezes everything


if __name__ == '__main__':
    CallbackList.append(Graph)
    tkWindow.mainloop()
    print("window closed")


# sets variables manually so you can bypass the GUI
def SetupForTest():
    global tickerbox_selections
    global keybox_selections
    tickerbox_selections = ["AMD", "INTL"]
    keybox_selections = {
        "INCOME_STATEMENT": ["grossProfit", "netIncome"],
        "BALANCE_SHEET": ["longTermDebt", "totalAssets"],
        "CASH_FLOW": [],  # this will always have all entries, with blank lists if no selection
    }


# TODO: figure out how to prevent pyplot from blocking the tkinter mainloop
# TODO: button or callback to close all the graphs / windows on focus-switch
# TODO: option to put all the graphs into a single window / plot
# TODO: check/handle cases where shared info (dates, currency, etc) don't actually match between statements
# TODO: replace the jank nested-functions with actual lambdas
# TODO: implement some kind of config-file to save GUI-selection states
# TODO: right-click to hide lines from listbox (and button to unhide all)
# also default to only showing "Wanted_Tickers"
# TODO: functionality to save/load graphs
