import json
import pprint
from FinanceFuckAround import *

GlobNames = list(pathlib.Path('./PyFinDump').glob('*.txt'))
EveryFile = []
for f in GlobNames:
    EveryFile.append(str(f))

CalcFolder = pathlib.Path('./PyFinCalcs/')

def OutputName(ticker, statement_type):
    name = f"{ticker}_{statement_type}_calc.txt"
    calcpath = str(CalcFolder) + name
    return calcpath

def process_income_reports(reports):
    for report in reports:
        fiscal_date_ending = report['fiscalDateEnding']
        gross_profit = report['grossProfit']
        total_revenue = report['totalRevenue']
        cost_of_revenue = report['costOfRevenue']
        cost_of_Goods_And_Services_Sold = report['costofGoodsAndServicesSold']
        operating_Income = report['operatingIncome']
        SGA = report['sellingGeneralAndAdministrative']
        researchAndDevelopment = report['researchAndDevelopment']
        OpEx = report['operatingExpenses']
        investment_income_Net = report['investmentIncomeNet']
        net_Interest_Income = report['netInterestIncome']
        interest_Income = report['interestIncome']
        interest_Expense = report['interestExpense']
        non_Interest_Income = report['nonInterestIncome']
        other_Non_Operating_Income = report['otherNonOperatingIncome']
        depreciation = report['depreciation']
        depreciation_And_Amortization = report['depreciationAndAmortization']
        income_Before_Tax = report['incomeBeforeTax']
        income_Tax_Expense = report['incomeTaxExpense']
        interest_And_Debt_Expense = report['interestAndDebtExpense']
        net_Income_From_Continuing_Operation = report['netIncomeFromContinuingOperations']
        comprehensive_Income_Net_Of_Tax = report['comprehensiveIncomeNetOfTax']
        ebit = report['ebit']
        ebitda = report['ebitda']
        net_Income = report['netIncome']
        #gross_profit_int = int(gross_profit.replace(',', ''))
        #total_revenue_int = int(total_revenue.replace(',', ''))
        gross_margin = int(gross_profit.replace(',', '')) / int(total_revenue.replace(',', ''))
        print(f"=== {fiscal_date_ending} ===")
        #print("\n")
        #print(f"Gross Profit: {format(int(gross_profit), ',')}") # doesn't work for some reason
        print(f"Gross Profit: {gross_profit}")
        print(f"Net Income: {format(float(net_Income), ',')}")
        print(f"Total Revenue: {format(int(total_revenue), ',')}")
        print(f"Gross Margin: {gross_margin:.2f}")
        
        #print("all:\n")
        #pprint.pprint(report)
        
        print("\n")

def LoadJSON_FromComponents(ticker=default_ticker, statement_type=default_statementtype):
    filename = GetFilename(ticker, statement_type)
    print("loading JSON from: ", filename)
    #with open(f"PyFinDump/{ticker}_INCOME_STATEMENT.txt") as file:
    with open(filename) as file:
        data = json.load(file)
    return data
    
def LoadJSON_FromFilename(theFilename):
    print("loading JSON from: ", theFilename)
    with open(theFilename) as file:
        data = json.load(file)
    return data

def DoTheDan(data):
    theTicker = data['symbol']
    # Access the annualReports field and process the data
    annual_reports = data['annualReports']
    
    print("\n")
    print("-" * 55)
    print("\t\tANNUAL_REPORTS:", theTicker)
    print("-" * 55)
    #print("\n")
    process_income_reports(annual_reports)
    
    #print("\n\n")
    
    # Access the quarterlyReports field and process the data
    quarterly_reports = data['quarterlyReports']
    print("-" * 55)
    print("\t\tQUARTELY_REPORTS:", theTicker)
    print("-" * 55)
    #print("\n")
    process_income_reports(quarterly_reports)


Wanted_Keys_BS = ["commonStockSharesOutstanding","retainedEarnings","longTermDebt", "totalAssets","deferredRevenue"]

def Balance_Sheet_Prints(ticker=wanted_names, statement_type=wanted_statements):
    data = LoadJSON_FromComponents(ticker=ticker, statement_type=statement_type)
    if statement_type == "BALANCE_SHEET":
        for report in data["annualReports"]:
            for key in Wanted_Keys_BS:
                if key in report:
                    print(key, ":", report[key])

                
    
    
    

def CalculatePercentages(data):
    Calc_Dict:dict = {}
    base_keyname = data["symbol"] + "_BALANCE_SHEET" + "_annualReports_"
    for Rep in data["annualReports"]:
        keyname = base_keyname + Rep["fiscalDateEnding"]
        Results = []
        
        def AsPercentage(fieldOne="totalCurrentAssets", fieldTwo="totalAssets"):
            if int(Rep[fieldTwo]) == 0:
                return "Division By Zero"
            thenumber = int(Rep[fieldOne]) / int(Rep[fieldTwo]) * 100
            return f"{fieldOne} as a percentage of {fieldTwo}: {thenumber:.3f}%"
        print(Balance_Sheet_Prints)
        #Results.append(AsPercentage())
        #Results.append(AsPercentage("inventory"))
        #Results.append(AsPercentage("propertyPlantEquipment"))
        ##Results.append(AsPercentage("currentDebt", "longTermDebt"))
        #Results.append(AsPercentage("totalCurrentLiabilities", "totalLiabilities"))
        #Calc_Dict.update({keyname:Results})
        ##print(Rep["calcs"])
    return Calc_Dict

def CreateCalc(ticker=default_ticker, statement_type=default_statementtype):
    data = LoadJSON_FromComponents(ticker, statement_type)
    # the JSON structure for income statements is:
    # Symbol:str, Annual_Reports:dict, Quarterly_Reports:dict
    if statement_type == "BALANCE_SHEET":
        Calcs = CalculatePercentages(data)
        pprint.pprint(Calcs)
    if statement_type == "INCOME_STATEMENT":
        DoTheDan(data)

#CreateCalc("CCJ", "BALANCE_SHEET")

def CreateAllCalcs():
    for f in LOADED_FILES:
        data = LoadJSON_FromFilename(f)
        # the JSON structure for income statements is:
        # Symbol:str, Annual_Reports:dict, Quarterly_Reports:dict
        if f.endswith("BALANCE_SHEET.txt"):
            Calcs = CalculatePercentages(data)
            pprint.pprint(Calcs)
            pprint.pprint(Balance_Sheet_Prints)
        if f.endswith("INCOME_STATEMENT.txt"):
            DoTheDan(data)

CreateAllCalcs()