import tkinter

# the window
tkWindow = tkinter.Tk()
tkWindow.minsize(640, 480)
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
    MakeButtons(5)
    newbuttonlist = MakeButtons(5)
    for (newbuttons, counters) in newbuttonlist:
        # somehow we can create an entirely new set of buttons by re-packing them here
        newbuttons.pack(side=tkinter.TOP, anchor=tkinter.SW, before=frame)
        print(f"newbuttons \n {newbuttons.keys()}\n")
    print(f"tkWindow \n {tkWindow.keys()}\n")
    print(f"frame \n {frame.keys()}\n")
    tkWindow.mainloop()
    print("window closed")
