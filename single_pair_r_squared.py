import pandas as pd
import numpy
import yfinance as yf
import statistics
# import csv
# pip install pandas
# pip install numpy
# pip install yfinance

# ---------------------------------------------------------------------------------------

# other method for r squared
# from sklearn.linear_model import LinearRegression
# pip install scipy
# pip install scikit-learn

# for charts
import pendulum
import matplotlib.pyplot as plt
# pip install matplotlib pendulum

# can import list of spy 500 with yahoo_fin seperate library
# tickers_sp500()

# ---------------------------------------------------------------------------------------

# stock_info = yf.Ticker('TSLA').info
# print(stock_info)
# {'zip': '78725', 'sector': 'Consumer Cyclical', 'fullTimeEmployees': 99290, 'longBusinessSummary': 'Tesla, Inc. designs, develops, manufactures, leases, and sells electric vehicles, and energy generation and storage systems in the United States, China, and internationally. The company operates in two segments, Automotive, and Energy Generation and Storage. The Automotive segment offers electric vehicles, as well as sells automotive regulatory credits. It provides sedans and sport utility vehicles through direct and used vehicle sales, a network of Tesla Superchargers, and in-app upgrades; and purchase financing and leasing services. This segment is also involved in the provision of non-warranty after-sales vehicle services, sale of used vehicles, retail merchandise, and vehicle insurance, as well as sale of products to third party customers; services for electric vehicles through its company-owned service locations, and Tesla mobile service technicians; and vehicle limited warranties and extended service plans. The Energy Generation and Storage segment engages in the design, manufacture, installation, sale, and leasing of solar energy generation and energy storage products, and related services to residential, commercial, and industrial customers and utilities through its website, stores, and galleries, as well as through a network of channel partners. This segment also offers service and repairs to its energy product customers, including under warranty; and various financing options to its solar customers. The company was formerly known as Tesla Motors, Inc. and changed its name to Tesla, Inc. in February 2017. Tesla, Inc. was incorporated in 2003 and is headquartered in Austin, Texas.', 'city': 'Austin', 'phone': '(512) 516-8177', 'state': 'TX', 'country': 'United States', 'companyOfficers': [], 'website': 'https://www.tesla.com', 'maxAge': 1, 'address1': '13101 Tesla Road', 'industry': 'Auto Manufacturers', 'ebitdaMargins': 0.21385999, 'profitMargins': 0.14947, 'grossMargins': 0.26613, 'operatingCashflow': 16030999552, 'revenueGrowth': 0.559, 'operatingMargins': 0.16569, 'ebitda': 16010000384, 'targetLowPrice': 24.33, 'recommendationKey': 'buy', 'grossProfits': 13606000000, 'freeCashflow': 6553249792, 'targetMedianPrice': 257.74, 'currentPrice': 151.1964, 'earningsGrowth': 0.977, 'currentRatio': 1.462, 'returnOnAssets': 0.11723, 'numberOfAnalystOpinions': 37, 'targetMeanPrice': 258.29, 'debtToEquity': 14.284, 'returnOnEquity': 0.32242, 'targetHighPrice': 436, 'totalCash': 21106999296, 'totalDebt': 5873999872, 'totalRevenue': 74863001600, 'totalCashPerShare': 6.684, 'financialCurrency': 'USD', 'revenuePerShare': 24.151, 'quickRatio': 0.953, 'recommendationMean': 2.2, 'exchange': 'NMS', 'shortName': 'Tesla, Inc.', 'longName': 'Tesla, Inc.', 'exchangeTimezoneName': 'America/New_York', 'exchangeTimezoneShortName': 'EST', 'isEsgPopulated': False, 'gmtOffSetMilliseconds': '-18000000', 'quoteType': 'EQUITY', 'symbol': 'TSLA', 'messageBoardId': 'finmb_27444752', 'market': 'us_market', 'annualHoldingsTurnover': None, 'enterpriseToRevenue': 6.427, 'beta3Year': None, 'enterpriseToEbitda': 30.055, '52WeekChange': -0.49278873, 'morningStarRiskRating': None, 'forwardEps': 5.52, 'revenueQuarterlyGrowth': None, 'sharesOutstanding': 3157750016, 'fundInceptionDate': None, 'annualReportExpenseRatio': None, 'totalAssets': None, 'bookValue': 12.619, 'sharesShort': 77644542, 'sharesPercentSharesOut': 0.024600001, 'fundFamily': None, 'lastFiscalYearEnd': 1640908800, 'heldPercentInstitutions': 0.44778, 'netIncomeToCommon': 11187000320, 'trailingEps': 3.15, 'lastDividendValue': None, 'SandP52WeekChange': -0.15688086, 'priceToBook': 11.981646, 'heldPercentInsiders': 0.16324, 'nextFiscalYearEnd': 1703980800, 'yield': None, 'mostRecentQuarter': 1664496000, 'shortRatio': 0.88, 'sharesShortPreviousMonthDate': 1667174400, 'floatShares': 2663153683, 'beta': 1.912715, 'enterpriseValue': 481175568384, 'priceHint': 2, 'threeYearAverageReturn': None, 'lastSplitDate': 1661385600, 'lastSplitFactor': '3:1', 'legalType': None, 'lastDividendDate': None, 'morningStarOverallRating': None, 'earningsQuarterlyGrowth': 1.035, 'priceToSalesTrailing12Months': 6.377041, 'dateShortInterest': 1669766400, 'pegRatio': 0.81, 'ytdReturn': None, 'forwardPE': 27.388586, 'lastCapGain': None, 'shortPercentOfFloat': 0.03, 'sharesShortPriorMonth': 76828235, 'impliedSharesOutstanding': 0, 'category': None, 'fiveYearAverageReturn': None, 'previousClose': 157.67, 'regularMarketOpen': 159.635, 'twoHundredDayAverage': 259.31717, 'trailingAnnualDividendYield': 0, 'payoutRatio': 0, 'volume24Hr': None, 'regularMarketDayHigh': 160.99, 'navPrice': None, 'averageDailyVolume10Day': 109389120, 'regularMarketPreviousClose': 157.67, 'fiftyDayAverage': 198.103, 'trailingAnnualDividendRate': 0, 'open': 159.635, 'toCurrency': None, 'averageVolume10days': 109389120, 'expireDate': None, 'algorithm': None, 'dividendRate': None, 'exDividendDate': None, 'circulatingSupply': None, 'startDate': None, 'regularMarketDayLow': 150.04, 'currency': 'USD', 'trailingPE': 47.995235, 'regularMarketVolume': 77077083, 'lastMarket': None, 'maxSupply': None, 'openInterest': None, 'marketCap': 477404430336, 'volumeAllCurrencies': None, 'strikePrice': None, 'averageVolume': 86241482, 'dayLow': 150.04, 'ask': 150.94, 'askSize': 800, 'volume': 77077083, 'fiftyTwoWeekHigh': 402.66666, 'fromCurrency': None, 'fiveYearAvgDividendYield': None, 'fiftyTwoWeekLow': 150.04, 'bid': 150.85, 'tradeable': False, 'dividendYield': None, 'bidSize': 1200, 'dayHigh': 160.99, 'coinMarketCapLink': None, 'regularMarketPrice': 151.185, 'preMarketPrice': 159.88, 'logo_url': 'https://logo.clearbit.com/tesla.com', 'trailingPegRatio': 1.2812}

# market_price = stock_info['regularMarketPrice']
# print(market_price)

# ---------------------------------------------------------------------------------------

# for testing to see if yahoo finance is having issues
# stock_1_current_price = yf.Ticker(a).info # ['regularMarketPreviousClose']
# stock_2_current_price = yf.Ticker(b).info # ['regularMarketPreviousClose']
# print(stock_1_current_price)
# print(stock_2_current_price)


# this was working and not working anymore
# stock_1_current_price = yf.Ticker(a).info['regularMarketPrice']
# stock_2_current_price = yf.Ticker(b).info['regularMarketPrice']

# ---------------------------------------------------------------------------------------

# make modular with different functions to call for loop 
# and write to csv

#  10 semi conductors call the function double for loop skip itself and write to cvs the results of each


# smh 
# stock_list = ['tsm', 'nvda', 'asml', 'avgo', 'txn', 'amat', 'adi', 'klac', 'lrcx', 'qcom', 'intc', 'mu' 'amd']


# Input two stocks and set stock 1 and 2 ------------------------------------------------

a = input('Stock 1:')
b = input('Stock 2:')

# you want stock 1 to be the smaller one so ratio > 1.0 so we reassign if input backwards
stock_1_current_price = yf.Ticker(a).history(period='1d', # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
                                   interval='1d', # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                                   actions=False)
stock_2_current_price = yf.Ticker(b).history(period='1d', # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
                                   interval='1d', # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                                   actions=False)

stock_1_current_price = stock_1_current_price['Close']
stock_2_current_price = stock_2_current_price['Close']
# print(stock_1_current_price)
# print(stock_2_current_price)

a1 = int(stock_1_current_price)
b1 = int(stock_2_current_price)
# print(type(a))
# print(type(b))

if a1 > b1:
    stock_1 = b
    stock_2 = a
else:
    stock_1 = a
    stock_2 = b

print("stock 1 is: ", stock_1, stock_1_current_price)
print("stock 2 is: ", stock_2, stock_2_current_price)
# print(type(stock_1_current_price))
# print(type(stock_2_current_price))

# ---------------------------------------------------------------------------------------

# Stock 1
price_history_1 = yf.Ticker(stock_1).history(period='1y', # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
                                   interval='60m', # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                                   actions=False)
# print(price_history_1)
time_series1 = list(price_history_1['Close'])
print(time_series1)

# ---------------------------------------------------------------------------------------

# Stock 2
price_history_2 = yf.Ticker(stock_2).history(period='1y', # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
                                   interval='60m', # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                                   actions=False)
# print(price_history_2)
time_series2 = list(price_history_2['Close'])
print(time_series2)


# ---------------------------------------------------------------------------------------

# ratio - we should get a rolling one year average? rolling 90 day average?
ratio = []
for x in range(0, len(time_series1)):
    # print(time_series2[x], time_series1[x])
    # print(time_series2[x] / time_series1[x])
    days_ratio = (time_series2[x] / time_series1[x])
    ratio.append(days_ratio)
# print(ratio)

average_ratio = (sum(ratio) / len(ratio))
# print("average ratio: ", average_ratio)

# ---------------------------------------------------------------------------------------

# spread
spread = []
for x in range(0, len(ratio)):
    # print((time_series1[x]*average_ratio - time_series2[x]) - average_ratio)
    days_spread = ((time_series1[x]*average_ratio - time_series2[x]) - average_ratio)
    spread.append(days_spread)

# ---------------------------------------------------------------------------------------

# Standard Deviation of Spread
st_dev = statistics.stdev(spread)
# print("standard dev: ", st_dev)

# R squared -----------------------------------------------------------------------------

corr_matrix = numpy.corrcoef(time_series1, time_series2)
corr = corr_matrix[0,1]
R_sq = corr**2

# print("r squared: ", R_sq)

# ---------------------------------------------------------------------------------------

#create DataFrame
df = pd.DataFrame({stock_1 : time_series1,
                   stock_2 : time_series2,
                   'Ratio' : ratio,
                   'Spread' : spread,
                   })

#'Date': date,
print("average ratio: ", average_ratio)
print(df)

df.to_csv('result.csv')

# ---------------------------------------------------------------------------------------

# find biggest open loss for each trade
# pnl graph / equity graph

# backtest pnl
trades_pnl = []
trade_enter = []
trade_exit = []
hold_period = []
open_price = 0
close_price = 0
for x in range(0,len(spread)):
    if spread[x] > st_dev and open_price == 0:
        open_price = spread[x]
        trade_enter.append(x)
        print("trade opened at: ", open_price)
    elif spread[x] < st_dev*-1 and open_price == 0:
        open_price = spread[x]
        trade_enter.append(x)
        print("trade opened at: ", open_price)
    if open_price > 1 and spread[x] < 1:
        close_price = spread[x]
        trades_pnl.append(open_price - close_price)
        trade_exit.append(x)
        hold_period.append(trade_exit[len(trade_exit) - 1] - trade_enter[len(trade_enter) - 1])
        print("trade closed at: ", close_price)
        open_price = 0
        close_price = 0
    if open_price < -1 and spread[x] > -1:
        close_price = spread[x]
        trades_pnl.append(close_price - open_price)
        trade_exit.append(x)
        hold_period.append(trade_exit[len(trade_exit) - 1] - trade_enter[len(trade_enter) - 1])
        print("trade closed at: ", close_price)
        open_price = 0
        close_price = 0

print("trades PnL: ", trades_pnl)
print("trade enter: ", trade_enter)
print("trade exit: ", trade_exit)
print("hold period: ", hold_period)
print("average hold period: ", sum(hold_period) / len(hold_period) )
print("number of round trips: ", len(hold_period))
print("total PnL per unit", sum(trades_pnl))
print("total profit per 100 shares: $", sum(trades_pnl)*100)


print("capital used on leg 1:", time_series1[0]*average_ratio*100)
print("capital used on leg 2:", time_series2[0]*100)
capital_leg_1 = time_series1[0]*average_ratio*100
capital_leg_2 = time_series2[0]*100

total_capital = capital_leg_1 + capital_leg_2
print("total capital used: ", total_capital)
total_return = (sum(trades_pnl)*100) / total_capital

print("r squared: ", R_sq)
print("standard dev: ", st_dev)
print("average ratio: ", average_ratio)
print("total return: ", total_return*100, "%")

# we want to make it monitor the ratios every minute, not just once a day...

# csv write line for each loop


# ---------------------------------------------------------------------------------------

# Creating a Graph / Chart
dt_list = [pendulum.parse(str(dt)).float_timestamp for dt in list(price_history_1.index)]
plt.style.use('dark_background')
plt.plot(dt_list, spread, linewidth=2)
plt.show()