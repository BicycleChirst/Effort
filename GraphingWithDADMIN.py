import tkinter
#from tkinter.constants import *
#from JSONwithDADMIN import *

# the window
tkWindow = tkinter.Tk()
tkWindow.minsize(960, 640)
tkWindow.wm_title("-- Graphing With DADMIN --")
# can't one-line the frame because the label and button need to reference it
frame = tkinter.Frame(tkWindow, relief=tkinter.RIDGE, borderwidth=2)
frame.pack(fill=tkinter.BOTH, expand=1)
tkinter.Label(frame, text="GraphingWithDADMIN").pack(fill="x", expand=1)
tkinter.Button(frame, text="Exit", command=tkWindow.destroy, name="exitbutton").pack(fill="none", side=tkinter.BOTTOM)


def MakeButtons(count):
    queue = []
    for x in range(count):
        newcounter = tkinter.IntVar(value=x)
        def newfun(somecounter=newcounter): somecounter.set(somecounter.get() + 1)
        newbutton = tkinter.Button(tkWindow, textvariable=newcounter, anchor=tkinter.NE, command=newfun)
        newbutton.pack(side=tkinter.LEFT, before=frame)
        queue.append((newbutton, newcounter))
    return queue


if __name__ == '__main__':
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
    tkWindow.mainloop()
    print("window closed")
