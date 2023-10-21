from GraphingWithDADMIN import *

# messing around with the tkinter buttons to test their behavior
# you can create / return them from a function / loop
# they don't need to be stored anywhere, and don't need a name
# normally, 'command' can only be set during the constructor call,
# but it can actually be rebound by setting the value of the "command" key (indexing Button as a dict)
# the behavior of the bound callbacks and variables is really confusing
# nested-function definitions with default parameters is a really jank way to get lambda-like behavior


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
        newbutton.pack(side=tkinter.LEFT, before=topframe)
        queue.append((newbutton, newcounter))
    return queue


def ButtonExperiment():
    firstset, newbuttonlist = MakeButtons(3), MakeButtons(3)
    for (FSB, FSC) in firstset:
        FSB.pack(side=tkinter.TOP, anchor=tkinter.SW, before=topframe)
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
    print(f"frame \n {topframe.keys()}\n")
