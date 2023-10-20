import tkinter
#from tkinter.constants import *
from JSONwithDADMIN import *

#from tkinter import filedialog
from matplotlib import pyplot
from matplotlib.ticker import FuncFormatter


# the window
tkWindow = tkinter.Tk()
tkWindow.minsize(960, 640)
tkWindow.wm_title("-- Graphing With DADMIN --")
# can't one-line the frame because the label and button need to reference it
frame = tkinter.Frame(tkWindow, relief=tkinter.RIDGE, borderwidth=2)
frame.pack(fill=tkinter.BOTH, expand=1)
tkinter.Label(frame, text="GraphingWithDADMIN").pack(fill="x", expand=1)
tkinter.Button(frame, text="Exit", command=tkWindow.destroy, name="exitbutton").pack(fill="none", side=tkinter.BOTTOM)


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
    #tkWindow.mainloop()
    userselection = LoadUserSelections()
    newfig = None
    for F in userselection:
        newfig = PlotWantedKeys(F)
    pyplot.show()
    print("window closed")
