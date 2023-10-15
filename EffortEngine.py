import requests
import json
import pathlib
import time
from API_tokens import ALPHAVANTAGE_TOKEN

import pprint
JSON_Printer = pprint.PrettyPrinter(indent=4, width=120, compact=False)
# if you just print the json-object, it will either be a single, bigass line (no-indents)
# otherwise (if you use indents), it lists put each element and bracket (in lists, for example) on a newline.
# seriously, there's absolutely no other way to prevent that retard-tier formatting
def PrintJSON(J): # pass a JSON-object, not a string (like the ones created by JSON.dumps)
    JSON_Printer.pprint(J)
    print('\n')
# note that the 'pretty-printed' strings are NOT valid JSON; you cannot reconstruct an object from them

Dumpfolder = pathlib.Path('./PyFinDump/') # Downloaded files stored here
CalcFolder = pathlib.Path('./PyFinCalcs/') # location to save calculated stats

default_ticker = "CCJ"
default_statementtype = "INCOME_STATEMENT"

wanted_tickers = ["CCJ","EH", "ACOR"]
wanted_statements = ["INCOME_STATEMENT", "BALANCE_SHEET"]

# dict: {filename: json}
LOADED_FILES = {}
TickerMap = {}  # {ticker : list[filenames]}
StatementMap = {} # same as TickerMap, except it lists Statement-Types instead of filenames

def AllFilenames():
    GlobNames = list(Dumpfolder.glob('*.txt'))
    return [str(f) for f in  GlobNames]

def GetFilename(ticker, statement_type):
    return f"PyFinDump/{ticker}_{statement_type}.txt" # don't append a suffix

currency_symbolmap = {
    'USD': '$',
    'CNY': '¥',
    'EURO': '€',
    'GBP': '£',
}

def LoadAllFiles(subdir=Dumpfolder):
    LOADED_FILES.clear()
    TickerMap.clear()
    StatementMap.clear()
    DownloadedFiles = [X for X in subdir.iterdir() if X.is_file()]
    for F in DownloadedFiles:
        filename = F.name.removesuffix('.txt')
        print(f"loading: {str(filename)}")
        with F.open(mode="r", encoding="utf-8") as thefile:
            try:
                thejson = json.load(thefile)  # look into the 'parse_int/float' arguments
                symbol = thejson['symbol']
                ST = filename.removeprefix(f"{symbol}_")
                thejson.update({'StatementType': ST})  # inserting this info to make things easier
                # these are annoying to look up so we're writing them into the root of the json
                thejson.update({"reportedCurrency": thejson["annualReports"][0]["reportedCurrency"]})
                thejson.update({"currencySymbol": currency_symbolmap[thejson["reportedCurrency"]]})
                LOADED_FILES.update({filename: thejson})
                TickerMap.setdefault(symbol, []).append(filename)
                StatementMap.setdefault(symbol, []).append(ST)
            except KeyError as e:
                print(f"Error processing {filename}: {e}")
                continue
    print('\n')
    return


def MoveJsonFiles():
    NewFolder = pathlib.Path('./DownloadedStatements')
    NewFolder.mkdir(exist_ok=True)
    NewFileList = []
    # go through TickerMap and create a subdir for each ticker
    for [tick, oldnamelist] in TickerMap.items():
        NewSubdir = NewFolder / tick
        NewSubdir.mkdir(exist_ok=True)
        # iterate through TickerMap's keys to get the filenames
        for oldname in oldnamelist:
            # use filenames to lookup json from LOADED_FILES
            actualJSON = LOADED_FILES[oldname]
            NewFile = NewSubdir / f"{actualJSON['StatementType']}.json"
            if NewFile.exists(): continue
            NewFile.touch()
            NewFileList.append(NewFile)
            # and rewrite it to the new file with .json suffix
            json.dump(actualJSON, NewFile.open(mode='w', encoding="utf-8"), indent=4)
    if len(NewFileList) > 0:
        print("created new json files: ")
        for f in NewFileList:
            print(str(f))
    return NewFileList

def DownloadFile(ticker=default_ticker, statement_type=default_statementtype):
    url = "https://www.alphavantage.co/query"
    headers = {"X-RapidAPI-Key": f"{ALPHAVANTAGE_TOKEN}", "X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com"}
    params={"apikey": f"{ALPHAVANTAGE_TOKEN}","X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com","symbol":ticker,"function":statement_type,"output_size":"full"} # should have timeout
    response = requests.get(url, headers=headers, params=params)
    
    match response.status_code:
        case 200: pass # OK
        case 404 | 403 | _ : print ("Alphavantage said go fuck yourself"); return;

    try:
        response.json()["symbol"]
    except KeyError:
        print("Alphavantage sent a bullshit response")
        return json.dumps(response.json(), indent=4)
    
    niceoutput = json.dumps(response.json(), indent=4)
    filename = GetFilename(ticker, statement_type)
    with open(filename, mode='w', encoding="utf-8") as thefile:
        thefile.writelines(niceoutput) # should be using 'json.dump' instead (proper key/value/nan handling)
    return niceoutput

def DownloadEverything(forceOverwrite=False):
    AlreadyExists = []
    # finding which files we've already saved
    if not forceOverwrite:
        for X in Dumpfolder.iterdir():
            AlreadyExists.append(str(X))
    for N in wanted_tickers:
        for S in wanted_statements:
            WantedFilename = GetFilename(N,S)
            if WantedFilename in AlreadyExists:
                print(WantedFilename, " already exists, skipping")
                continue
            else:
                print("Downloading New File: ", WantedFilename)
                DownloadFile(N, S)
                time.sleep(13)
                # should probably validate the response, in case they sent back a "fuck off you're sending too many requests"
                #response = DownloadFile("WOLF", "INCOME_STATEMENT")
                #if response.status_code == (403): print ("go fuck yourself")
                #if response.status_code == (200): print ("Nice effort")

DownloadEverything()
LoadAllFiles()
print("Loaded Statements: ")
PrintJSON(StatementMap)
MoveJsonFiles()