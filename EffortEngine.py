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
def PrintJSON(J):
    # pass a JSON-object, not a string (like the ones created by JSON.dumps)
    JSON_Printer.pprint(J)
    print('\n')
# note that the 'pretty-printed' strings are NOT valid JSON; you cannot reconstruct an object from them

# TODO: update these folder names
Dumpfolder = pathlib.Path('./PyFinDump/')  # Downloaded files stored here
CalcFolder = pathlib.Path('./PyFinCalcs/')  # location to save calculated stats

default_ticker = "AMD"
default_statementtype = "INCOME_STATEMENT"

wanted_tickers = ["AMD", "NVDA", "MSFT", "AMZN", "INTL", "IBM"]
wanted_statements = ["INCOME_STATEMENT", "BALANCE_SHEET", "CASH_FLOW"]

# dict: {filename: json}
LOADED_FILES = {}
TickerMap = {}  # {ticker : list[filenames]}
StatementMap = {}  # same as TickerMap, except it lists Statement-Types instead of filenames


def AllFilenames(subdir=Dumpfolder):
    GlobNames = list(subdir.glob('*.txt'))
    return [str(f) for f in GlobNames]


def GetFilename(ticker, statement_type):
    return f"PyFinDump/{ticker}_{statement_type}.txt"
# TODO: don't append a suffix


currency_symbolmap = {
    'USD': '$',
    'CNY': '¥',
    'EURO': '€',
    'GBP': '£',
}


def LoadAllFiles(forceReloadAll=False, subdir=Dumpfolder):
    LocalFiles = [X for X in subdir.iterdir() if X.is_file()]
    newlyLoadedList = []
    if forceReloadAll:
        LOADED_FILES.clear()
        TickerMap.clear()
        StatementMap.clear()
    elif not forceReloadAll:
        LocalFiles = [F for F in LocalFiles if str(F) not in LOADED_FILES.keys()]
    for F in LocalFiles:
        filename = F.name.removesuffix('.txt')
        print(f"loading: {str(filename)}")
        newlyLoadedList.append(filename)
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
    return newlyLoadedList


def MoveJsonFiles(forceOverwrite=False):
    NewFolder = pathlib.Path('./SavedJSON')
    NewFolder.mkdir(exist_ok=True)
    newFilePaths = []
    # go through TickerMap and create a subdir for each ticker
    for [tick, oldnamelist] in TickerMap.items():
        NewSubdir = NewFolder / tick
        NewSubdir.mkdir(exist_ok=True)
        # iterate through TickerMap's keys to get the filenames
        for oldname in oldnamelist:
            # use filenames to lookup json from LOADED_FILES
            actualJSON = LOADED_FILES[oldname]
            NewFile = NewSubdir / f"{actualJSON['StatementType']}.json"
            if NewFile.exists() and not forceOverwrite: continue
            NewFile.touch()
            newFilePaths.append(NewFile)
            # and rewrite it to the new file with .json suffix
            json.dump(actualJSON, NewFile.open(mode='w', encoding="utf-8"), indent=4)
    if len(newFilePaths) > 0:
        print("created new json files: ")
        for f in newFilePaths:
            print(str(f))
    return newFilePaths
# TODO: skip existing files WITHOUT loading the whole damn json
# TODO: add some mechanism to detect outdated files


# https://www.alphavantage.co/documentation/#fundamentals
# https://documentation.alphavantage.co/FundamentalDataDocs/index.html
def DownloadFile(ticker, statement_type):
    url = "https://www.alphavantage.co/query"
    headers = {"X-RapidAPI-Key": f"{ALPHAVANTAGE_TOKEN}", "X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com"}
    params = {
        "apikey":   f"{ALPHAVANTAGE_TOKEN}", "X-RapidAPI-Host": "alpha-vantage.p.rapidapi.com",
        "symbol": ticker, "function": statement_type, "output_size": "full"
    }
    try:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        # we should check the certificate before doing a conversion to json on unknown data
    except requests.exceptions.RequestException as Problem:
        print(f"BIG PROBLEM in DownloadFile: {Problem}")
        return
    
    match response.status_code:
        case 200: pass  # OK
        case 404 | 403 | _ : print("Alphavantage said go fuck yourself"); return;

    try:
        response.json()["symbol"]
    except KeyError:
        print("Alphavantage sent a bullshit response")
        return json.dumps(response.json(), indent=4)
    
    niceoutput = json.dumps(response.json(), indent=4)
    filename = GetFilename(ticker, statement_type)
    with open(filename, mode='w', encoding="utf-8") as thefile:
        thefile.writelines(niceoutput)  # should be using 'json.dump' instead (proper key/value/nan handling)
    return niceoutput


def DownloadEverything(forceRedownload=False):
    AlreadyExists = []
    newDownloadedFiles = []
    # finding which files we've already saved
    if not forceRedownload:
        for X in Dumpfolder.iterdir():
            AlreadyExists.append(str(X))
    for N in wanted_tickers:
        for S in wanted_statements:
            WantedFilename = GetFilename(N, S)
            if WantedFilename in AlreadyExists:
                print(WantedFilename, " already exists, skipping")
                continue
            else:
                print("Downloading New File: ", WantedFilename)
                DownloadFile(N, S)
                newDownloadedFiles.append(WantedFilename)
                time.sleep(13)
    return newDownloadedFiles


InitializationCompleteFlag = False

def InitializeEverything(printLoaded=False, forceReloadAll=False, forceOverwrite=False, forceRedownload=False):
    global InitializationCompleteFlag
    if InitializationCompleteFlag: return
    InitializationCompleteFlag = True
    # ^ This isn't working?
    newdownloads = DownloadEverything(forceRedownload)
    newlyloaded = LoadAllFiles(forceReloadAll)
    movedfiles = MoveJsonFiles(forceOverwrite)
    if printLoaded:
        print("Loaded Statements: ")
        PrintJSON(StatementMap)


if __name__ == '__main__':
    InitializeEverything(printLoaded=True)
    InitializationCompleteFlag = True
