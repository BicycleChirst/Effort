from EffortEngine import *

InitializeEverything(printLoaded=True)
InitializationCompleteFlag = True

# fields of each reporting-period in the JSON-files of a given statement-type (AlphaVantage)
Keytable = {
    "SPECIAL": {'fiscalDateEnding', 'reportedCurrency'},  # these keys are present in every StatementType
    # the 'special' keys are non-numerical; exclude them from formatting and conversions.
    # the 'special' keys are omitted from the following lists
    "INCOME_STATEMENT": [
        'grossProfit', 'totalRevenue', 'costOfRevenue', 'costofGoodsAndServicesSold', 'netIncome',
        'operatingIncome', 'sellingGeneralAndAdministrative', 'researchAndDevelopment', 'operatingExpenses',
        'investmentIncomeNet', 'netInterestIncome', 'interestIncome', 'interestExpense', 'nonInterestIncome',
        'otherNonOperatingIncome', 'depreciation', 'depreciationAndAmortization', 'incomeBeforeTax', 'incomeTaxExpense',
        'interestAndDebtExpense', 'netIncomeFromContinuingOperations', 'comprehensiveIncomeNetOfTax', 'ebit', 'ebitda',
    ],
    "BALANCE_SHEET": [
        'totalAssets', 'totalCurrentAssets', 'cashAndCashEquivalentsAtCarryingValue', 'commonStockSharesOutstanding',
        'cashAndShortTermInvestments', 'inventory', 'currentNetReceivables', 'totalNonCurrentAssets', 'commonStock',
        'propertyPlantEquipment', 'accumulatedDepreciationAmortizationPPE', 'intangibleAssets', 'retainedEarnings',
        'intangibleAssetsExcludingGoodwill', 'goodwill', 'investments', 'longTermInvestments', 'shortTermInvestments',
        'otherCurrentAssets', 'otherNonCurrentAssets', 'totalLiabilities', 'totalCurrentLiabilities',
        'currentAccountsPayable', 'deferredRevenue', 'currentDebt', 'shortTermDebt', 'totalNonCurrentLiabilities',
        'capitalLeaseObligations', 'longTermDebt', 'currentLongTermDebt', 'longTermDebtNoncurrent', 'treasuryStock',
        'shortLongTermDebtTotal', 'otherCurrentLiabilities', 'otherNonCurrentLiabilities', 'totalShareholderEquity',
    ],
    "CASH_FLOW": [
        'operatingCashflow', 'paymentsForOperatingActivities', 'proceedsFromOperatingActivities', 'dividendPayout',
        'changeInOperatingLiabilities', 'changeInOperatingAssets', 'depreciationDepletionAndAmortization', 'netIncome',
        'capitalExpenditures', 'changeInReceivables', 'changeInInventory', 'profitLoss', 'cashflowFromInvestment',
        'cashflowFromFinancing', 'proceedsFromRepaymentsOfShortTermDebt', 'paymentsForRepurchaseOfCommonStock',
        'paymentsForRepurchaseOfEquity', 'paymentsForRepurchaseOfPreferredStock', 'changeInExchangeRate',
        'dividendPayoutCommonStock', 'dividendPayoutPreferredStock', 'proceedsFromIssuanceOfCommonStock',
        'proceedsFromIssuanceOfLongTermDebtAndCapitalSecuritiesNet', 'proceedsFromIssuanceOfPreferredStock',
        'proceedsFromRepurchaseOfEquity', 'proceedsFromSaleOfTreasuryStock', 'changeInCashAndCashEquivalents',
    ],
}

# TODO: sort and re-align the keys

# every statementtype has two lists of reports; annual and quarterly
# the two lists always have the same keys
# TODO: write a function to verify that

WantedKeys = {
    "INCOME_STATEMENT": ["grossProfit", "netIncome", "operatingExpenses"],
    "BALANCE_SHEET": ["commonStockSharesOutstanding", "retainedEarnings", "longTermDebt", "totalAssets", ],
    "CASH_FLOW": ["operatingCashflow", "netIncome", "dividendPayout"],
}

## these maps are laid out as denominator : list[numerator]
WantedPercentages = {
    "BALANCE_SHEET": {
        "totalAssets": ["totalCurrentAssets", "inventory", "propertyPlantEquipment", ],
        "longTermDebt": ["currentDebt", ],
        "totalLiabilities": ["totalCurrentLiabilities", ],
    },
    "INCOME_STATEMENT": {
        "totalRevenue": ["grossProfit", "operatingExpenses", ],
        "incomeBeforeTax": ["incomeTaxExpense", ],
    },
    "CASH_FLOW": {
        "operatingCashflow": ["netIncome", ],
    },
}

KeyFormattingExcluded = ["fiscalDateEnding", "reportedCurrency"]
ReportingPeriod = "quarterlyReports"

# this function converts all the fields in a JSON file
# from "None" -> 0, and otherwise from string to float
# skipping the (non-numerical fields) listed in KeyFormattingExcluded
def ConvertJSONnumbers(theJson, reverseDates=False):
    P = ['annualReports', 'quarterlyReports']
    [X, Y] = [theJson[Z] for Z in P]
    for reportingPeriod in [*X, *Y]:
        for key, value in reportingPeriod.items():
            if key in KeyFormattingExcluded: continue;
            if value == "None": reportingPeriod[key] = 0
            else: reportingPeriod[key] = float(value)
    if reverseDates:
        theJson.update({'annualReports': [*reversed(theJson['annualReports'])]})
        theJson.update({'quarterlyReports': [*reversed(theJson['quarterlyReports'])]})
    return theJson


def OutputName(ticker, statement_type):
    name = f"{ticker}_{statement_type}_calc.txt"
    calcpath = str(CalcFolder) + name
    return calcpath


def LoadJSON_FromComponents(ticker=default_ticker, statement_type=default_statementtype):
    filename = GetFilename(ticker, statement_type)
    print("loading JSON from: ", filename)
    with open(filename) as file:
        data = json.load(file)
    return data


def LoadJSON_FromFilename(theFilename):
    print("loading JSON from: ", theFilename)
    with open(theFilename) as file:
        data = json.load(file)
    return data


# the JSON structure for income statements is:
# Symbol:str, Annual_Reports:list[dict], Quarterly_Reports:list[dict]
# the reports are lists where each entry represents the data for that year / quarter

def PrintKeys(ticker=default_ticker, statement_type=default_statementtype):
    data = LoadJSON_FromComponents(ticker, statement_type)
    wanted = WantedKeys.setdefault(statement_type, [])
    if len(wanted) == 0: return
    print("-" * 55)
    for report in data["annualReports"]:
        print(report["fiscalDateEnding"])
        for key in wanted:
            value = report[key]
            if value == "None" : print(f"{key} : ${0}")
            else: print(f"{key} : ${'{:,.2f}'.format(int(value))}")
    print('\n')


# it's actuallly easier to just print everything
def PrintAllKeys(ticker, statement_type):
    data = LoadJSON_FromComponents(ticker, statement_type)
    for report in data["annualReports"]:
        for key, value in report.items():
            if key in KeyFormattingExcluded: print(f"{key} : {value}"); continue;
            if value == "None": print(f"{key} : ${0}"); continue;
            print(f"{key} : ${'{:,.2f}'.format(int(value))}")
        print('\n')


def FormatJSON(thejson):
    newjson = []
    for report in thejson[ReportingPeriod]:
        for key, value in report.items():
            if key in KeyFormattingExcluded: newjson.append(f"{key} : {value}"); continue;
            if value == "None": newjson.append(f"{key} : ${0}"); continue;
            newjson.append(f"{key} : ${'{:,.2f}'.format(float(value))}")
        newjson.append("-" * 93)
    return newjson


def CalculatePercentages(data):
    Calc_Dict: dict = {}
    dictname = data["symbol"] + "_" + data["StatementType"] + "_annualReports"
    Calc_Dict.update({"dictname" : dictname})
    ToCalc = WantedPercentages[data["StatementType"]]
    if len(ToCalc) == 0 : return
    for Rep in data["annualReports"]:
        Results = []

        def AsPercentage(fieldOne, fieldTwo):
            if Rep[fieldOne] == "None" or Rep[fieldTwo] == "None":
                return "None"
            thenumber = float(Rep[fieldOne]) / float(Rep[fieldTwo]) * 100
            return f"{fieldOne} = {thenumber:.3f}% of {fieldTwo}"

        for denominator, FieldOneList in ToCalc.items():
            for FieldOne in FieldOneList:
                Results.append(AsPercentage(FieldOne, denominator))
        Calc_Dict.update({Rep["fiscalDateEnding"] : Results})
    return Calc_Dict


def CreateCalcsFor(tickersToUse):
    for T in tickersToUse:
        filenames = TickerMap[T]
        for N in filenames:
            data = LOADED_FILES[N]
            print(N)
            Calcs = CalculatePercentages(data)
            pprint.pprint(Calcs)
            print('\n')


if __name__ == '__main__':
    PrintKeys("NVDA")
    PrintKeys("MSFT", "BALANCE_SHEET")
    PrintAllKeys("AMD", "INCOME_STATEMENT")
    wanted_calcs = ["MSFT", "NVDA", "EXTR"]
    CreateCalcsFor(wanted_calcs)
