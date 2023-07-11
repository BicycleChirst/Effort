import requests
#import pprint
import json
import io
import pathlib
import time

Dumpfolder = pathlib.Path('./PyFinDump/')

default_ticker = "CCJ"
default_statementtype = "INCOME_STATEMENT"

wanted_names = ["CCJ","EH"]
wanted_statements = ["INCOME_STATEMENT", "BALANCE_SHEET"]

LOADED_FILES = []

#function_options = []
def GetFilename(ticker, statement_type):
    return f"PyFinDump/{ticker}_{statement_type}.txt"

def GetTheThing(ticker, statement_type):
    url = "https://www.alphavantage.co/query"
    headers = {"X-RapidAPI-Key": "0000000", "X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com"}
    params={"apikey": "","X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com","symbol":ticker,"function":statement_type,"interval":"5min","output_size":"full","datatype":".csv"}
    return requests.get(url, headers=headers, params=params) # should have timeout

def SaveToFile(ticker=default_ticker, statement_type=default_statementtype):
    response = GetTheThing(ticker, statement_type)
    niceoutput = json.dumps(response.json(), indent=4)
    #filename = "PyFinDump/{0}_{1}.txt".format(ticker, statement_type)
    filename = GetFilename(ticker, statement_type)
    with open(filename, mode='w', encoding="utf-8") as thefile:
        thefile.writelines(niceoutput)
    return niceoutput

def GetAllThings(forceOverwrite=False):
    AlreadyExists = []
    # finding which files we've already saved
    if forceOverwrite != True:
        for X in Dumpfolder.iterdir():
            AlreadyExists.append(str(X))
    for N in wanted_names:
        for S in wanted_statements:
            WantedFilename = GetFilename(N,S)
            LOADED_FILES.append(WantedFilename)
            print("checking if ", WantedFilename, "already exists")
            if WantedFilename in AlreadyExists:
                print(WantedFilename, " already exists, skipping")
                continue
            else:
                print("Getting New File: ", WantedFilename)
                SaveToFile(N, S)
                time.sleep(13)
                # should probably validate the response, in case they sent back a "fuck off you're sending too many requests"

#GetAllThings()

#response = GetTheThing("", default_statementtype)
#print("plsdontexit")
#print("end")

#response = GetTheThing("WOLF", "INCOME_STATEMENT")
#if response.status_code == (403): print ("go fuck yourself")
#if response.status_code == (200): print ("Nice effort")

#pprint.pprint(response.json())
## alphavantage API key: 
##python3 -i FinanceFuckAround.py >>> SaveToFile(“AMD”) to ouput statment in PyFinDump
