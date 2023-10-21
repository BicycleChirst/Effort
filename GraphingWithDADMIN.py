import tkinter
from JSONwithDADMIN import *

from matplotlib import pyplot
from matplotlib.ticker import FuncFormatter


helptext = """
Single-clicks will completely replace current selection
To multi-select:
    Click and drag inside a list to select a whole block of lines
    Ctrl+Click to add/remove a line from the current selection
    Shift+Click to add a range (while keeping current selections)
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
for (K, L) in StatementType_Keylist.items():
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
def y_axis_formatter(x, pos, currency='$'):
    if x == 0: return '0'
    abs_x = abs(x)
    if abs_x >= 1e9:
        formatted_x = f'{abs_x / 1e9:.1f}B'
    else:
        formatted_x = f'{abs_x / 1e6:.1f}M'
    formatted_x = currency + formatted_x
    # Add a minus sign for negative values
    if x < 0: formatted_x = '-' + formatted_x
    return formatted_x
# TODO: store currency-symbol in a global variable or bind it in a lambda


def LoadUserSelections():
    plot_ticker_var = 'AMD'
    plot_statementtype_var = 'INCOME_STATEMENT'
    selectedfiles = []
    file = LOADED_FILES[f"{plot_ticker_var}_{plot_statementtype_var}"]
    # convert all fields to floats, get rid of 'None's, reverse order of dates
    file = ConvertJSONnumbers(file, True)
    selectedfiles.append(file)
    return selectedfiles


def PlotWantedKeys(thejson, figure=None):
    # setup
    if figure is None:
        figure = pyplot.figure(figsize=(10, 10), layout='constrained', clear=True)
        figure.suptitle(f'{thejson["symbol"]} {thejson["StatementType"]} {str(WantedKeys[thejson["StatementType"]])}')
    ax = figure.add_subplot()
    ax.set_title('Axes', loc='left', fontstyle='oblique', fontsize='medium')
    pyplot.xlabel('Date')
    pyplot.annotate(f'Values in {thejson["reportedCurrency"]}', (-0.135, 1.05), xycoords='axes fraction', rotation=0)
    # the tuple positions the text; units seem to be the size of the graph.
    # set the y-coord to 0 if you want the annotation at the bottom instead
    pyplot.xticks(rotation=45)
    pyplot.gca().yaxis.set_major_formatter(FuncFormatter(y_axis_formatter))  # apply formatter to y-axis
    pyplot.grid(True)

    # handles, labels = ax.get_legend_handles_labels()
    quarters = thejson["quarterlyReports"]
    dates = [Q['fiscalDateEnding'] for Q in quarters]
    for K in WantedKeys[thejson["StatementType"]]:
        ax.plot(dates, [Q[K] for Q in quarters], marker='o', linestyle='-', label=f"{K}")
    ax.legend()
    return figure


# we'll add this function to the callbacks
def Graph():
    # assume that all other callbacks have triggered
    userselection = LoadUserSelections()
    newfig = None
    for F in userselection:
        newfig = PlotWantedKeys(F)
    PlotWantedKeys(userselection[0])
    pyplot.show(block=False)

# instead of calling '.show' without blocking,
# you can instead enable "interactive mode", which automatically shows figures
# without the need to call "show"
#pyplot.ion()
# do I call this before the other pyplot stuff or what?

if __name__ == '__main__':
    CallbackList.append(Graph)
    tkWindow.mainloop()
    print("window closed")

# TODO: check that the selected statementtypes actually exist
# TODO: replace the jank nested-functions with actual lambdas
# TODO: figure out why passing the 'newfig' creates overlapping axes
# TODO: implement some kind of config-file to save GUI-selection states
# TODO: right-click to hide lines from listbox (and button to unhide all)
# also default to only showing "Wanted_Tickers"
# TODO: functionality to save/load graphs
