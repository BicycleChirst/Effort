import tkinter
from JSONwithDADMIN import *

from matplotlib import pyplot
from matplotlib.ticker import FuncFormatter


# the window
tkWindow = tkinter.Tk()
tkWindow.minsize(960, 640)
tkWindow.wm_title("-- Graphing With DADMIN --")
# can't one-line the frame because the label and button need to reference it
frame = tkinter.Frame(tkWindow, relief=tkinter.RIDGE, borderwidth=2)
frame.pack(fill=tkinter.BOTH, expand=tkinter.NO)
tkinter.Label(frame, text="GraphingWithDADMIN").pack(fill="x", expand=1)
tkinter.Button(frame, text="Exit", command=tkWindow.destroy, name="exitbutton")\
    .pack(fill="none", side=tkinter.BOTTOM)

tickerbox_frame = tkinter.LabelFrame(tkWindow, text="Tickers")
tickerbox_frame.pack(fill="both", expand=tkinter.YES, side=tkinter.LEFT, padx=5, pady=5)
# "extended" allows dragging to select a range of items, "multiple" does not
# however, single-clicks will replace the current selection instead of adding to it
ticker_listbox = tkinter.Listbox(tickerbox_frame, selectmode="extended")
ticker_listbox.pack(side=tkinter.TOP, expand=tkinter.YES, fill="both", padx=5, pady=5)
for T in sorted(StatementMap.keys()):
    ticker_listbox.insert(tkinter.END, T)

tickerbox_selections = []
def tickerbox_callback():
    global tickerbox_selections
    tickerbox_selections = [ticker_listbox.get(I) for I in ticker_listbox.curselection()]
    print(tickerbox_selections)
tkinter.Button(tickerbox_frame, text="print ticker selections", command=tickerbox_callback)\
    .pack(fill="x", side=tkinter.BOTTOM)

keybox_selections = {}
for K, L in StatementType_Keylist.items():
    if K == "SPECIAL": continue
    newframe = tkinter.LabelFrame(tkWindow, text=f"{K}")
    newframe.pack(fill="both", expand=tkinter.YES, side=tkinter.LEFT, padx=5, pady=5)
    newbox = tkinter.Listbox(newframe, selectmode="extended")
    newbox.pack(side=tkinter.TOP, expand=tkinter.YES, fill="both", padx=5, pady=5)
    for li in sorted(L):
        newbox.insert(tkinter.END, li)
    keybox_selections[K] = []
    # defining parameters (which default to local variables) is required for lamba-like behavior
    def newbox_callback(B=newbox, bk=K):
        keybox_selections[bk] = [B.get(I) for I in B.curselection()]
        print(keybox_selections[bk])
    tkinter.Button(newframe, text=f"print {K} selections", command=newbox_callback)\
        .pack(fill="x", side=tkinter.BOTTOM)
# TODO: set height of Listbox to the length of the list or ensure widow height is enough


# 'keyevent' gets passed implicitly
def KeybindTest(keyevent):
    print("bound function called")
    print(f"passed: {keyevent}")


tkWindow.bind('<Key-Return>', KeybindTest)


def MakeButtons(count):
    queue = []
    for x in range(count):
        newcounter = tkinter.IntVar(value=x)
        def newfun(somecounter=newcounter): somecounter.set(somecounter.get() + 1)
        newbutton = tkinter.Button(tkWindow, textvariable=newcounter, anchor=tkinter.NE, command=newfun)
        newbutton.pack(side=tkinter.LEFT, before=frame)
        queue.append((newbutton, newcounter))
    return queue


def ButtonExperiment():
    firstset, newbuttonlist = MakeButtons(3), MakeButtons(3)
    for (FSB, FSC) in firstset:
        FSB.pack(side=tkinter.TOP, anchor=tkinter.SW, before=frame)
        FSC.set(FSC.get() + 1)
        FSB["height"] += FSC.get()
        FSB["width"] += FSC.get()
    for (newbuttons, counters) in [*firstset, *newbuttonlist]:
        def switcheroo(NB=newbuttons, NC=counters):
            NC.set(NC.get() + 1)
            NB["width"] = NC.get()
            NB["height"] = NC.get()
        newbuttons["command"] = switcheroo
    print(f"tkWindow \n {tkWindow.keys()}\n")
    print(f"frame \n {frame.keys()}\n")


# Create a custom formatter to format the y-axis labels
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
# TODO: store currency-symbol in a global variable bind it in a lambda


# TODO: read tickers / statement types from UI
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


if __name__ == '__main__':
    #ButtonExperiment()
    tkWindow.mainloop()
    #userselection = LoadUserSelections()
    #newfig = None
    #for F in userselection:
    #    newfig = PlotWantedKeys(F)
    #pyplot.show()
    print("window closed")
