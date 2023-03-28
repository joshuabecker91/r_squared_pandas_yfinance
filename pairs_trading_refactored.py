import pandas as pd
import numpy
import yfinance as yf
import statistics
import csv
import os
import pendulum
import matplotlib.pyplot as plt

import schedule
import datetime
import time

cwd = os.getcwd()

# Pairs Trading ================================================================================================================



# Get Pair  ====================================================================================================================


# Get Ticker Data for any Ticker passed in
def get_ticker_data(ticker):
    try:
        ticker_data = yf.Ticker(ticker).history(period='1y', # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
                                            interval='60m', # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                                            actions=False)
        return ticker_data
    except:
        print("error: ", ticker)
        with open('error_log.txt', 'a') as f:
            f.write(f'error getting data for {ticker}')
            f.write('\n')
        return


# Calculate the average price for entire price series of two tickers
def calculate_average_price(ticker_a_closing_prices, ticker_b_closing_prices):
    a_avg_price = sum(ticker_a_closing_prices) / len(ticker_a_closing_prices)
    b_avg_price = sum(ticker_b_closing_prices) / len(ticker_b_closing_prices)
    return [a_avg_price, b_avg_price]


# Get Pair Data and assign Stock A and B ensuring A is the lower priced stock so ratio is > 1
def get_pair(ticker_a, ticker_b):
    # Get data for stocks a and b from yfinance
    ticker_a_data = get_ticker_data(ticker_a)
    ticker_b_data = get_ticker_data(ticker_b)

    # Calculate average price for a and b
    ticker_a_closing_prices = list(ticker_a_data['Close'])
    ticker_b_closing_prices = list(ticker_b_data['Close'])
    # catch errors if length differs
    if len(ticker_a_closing_prices) != len(ticker_b_closing_prices):
        print("error: ", "length of arrays are not the same")
        with open('error_log.txt', 'a') as f:
            f.write(f'{ticker_a} {ticker_b} length of arrays are not the same')
            f.write('\n') 
        return
    [a_avg_price, b_avg_price] = calculate_average_price(ticker_a_closing_prices, ticker_b_closing_prices)

    # assign lower average price to be stock stock_1. Swap ticker and all data if a > b
    if a_avg_price > b_avg_price:
        [stock_1_data, stock_2_data] = [ticker_b_data, ticker_a_data] 
        [stock_1, stock_2] = [ticker_b, ticker_a]
        [stock_1_closing_prices, stock_2_closing_prices] = [ticker_b_closing_prices, ticker_a_closing_prices]
    else:
        [stock_1_data, stock_2_data] = [ticker_a_data, ticker_b_data]
        [stock_1, stock_2] = [ticker_a, ticker_b]
        [stock_1_closing_prices, stock_2_closing_prices] = [ticker_a_closing_prices, ticker_b_closing_prices]

    return [[stock_1, stock_1_data, stock_1_closing_prices],
            [stock_2, stock_2_data, stock_2_closing_prices]]


# Calculation Logic ============================================================================================================


# Want to updgrade to Rolling 251 day ratio / rolling 1761 period
def calculate_ratio(stock_1_closing_prices, stock_2_closing_prices):
    pair_daily_ratios = []
    for x in range(0, len(stock_1_closing_prices)):
        days_ratio = (stock_2_closing_prices[x] / stock_1_closing_prices[x])
        pair_daily_ratios.append(days_ratio)
    return pair_daily_ratios


def calculate_spreads(stock_1_closing_prices, stock_2_closing_prices, pair_daily_ratios, average_ratio):
    pair_daily_spreads = []
    for x in range(0, len(pair_daily_ratios)):
        days_spread = ((stock_1_closing_prices[x]*average_ratio) - stock_2_closing_prices[x])
        pair_daily_spreads.append(days_spread)
    return pair_daily_spreads


def calculate_standard_deviation(spreads):
    st_dev = statistics.stdev(spreads)
    return st_dev


def calculate_r_squared_correlation(stock_1, stock_2, stock_1_closing_prices, stock_2_closing_prices):
    try:
        corr_matrix = numpy.corrcoef(stock_1_closing_prices, stock_2_closing_prices)
        corr = corr_matrix[0,1]
        r_sq = corr**2
        return r_sq
    except:
        print("error: ", "error calculating R_sq correlation")
        with open('error_log.txt', 'a') as f:
            f.write(f'{stock_1} {stock_2} error calculating R_sq correlation')
            f.write('\n') 
        return


# Create Pandas Dataframe with Ratio and Spread ===================================================================================


# Create Pandas Dataframe
def create_pair_dataframe(stock_1, stock_2, stock_1_closing_prices, stock_2_closing_prices, pair_daily_ratios, pair_daily_spreads):
    df = pd.DataFrame({stock_1 : stock_1_closing_prices,
                    stock_2 : stock_2_closing_prices,
                    'Ratio' : pair_daily_ratios,
                    'Spread' : pair_daily_spreads,
                    })
    df.to_csv(cwd + '/pairs/' + f'{stock_1}_{stock_2}.csv')
    return df


# Creating a Graph / Chart of Spread
def create_graph(stock_1, stock_2, stock_1_data, pair_daily_spreads, st_dev, r_sq):
    dt_list = [pendulum.parse(str(dt)).float_timestamp for dt in list(stock_1_data.index)]
    plt.style.use('dark_background')
    plt.plot(dt_list, pair_daily_spreads, linewidth=2)
    # plot standard dev line range and equilibrium zero line
    plt.axhline(y=st_dev*2, xmin=0.0, xmax=1.0, color='m')
    plt.axhline(y=st_dev, xmin=0.0, xmax=1.0, color='r')
    plt.axhline(y=0, xmin=0.0, xmax=1.0, color='w')
    plt.axhline(y=(st_dev*-1), xmin=0.0, xmax=1.0, color='r')
    plt.axhline(y=(st_dev*-2), xmin=0.0, xmax=1.0, color='m')
    if r_sq > .65:
        plt.savefig((cwd + '/figs_high/' + f'{stock_1}_{stock_2}.png'))
        plt.clf()
    else:
        plt.savefig((cwd + '/figs_low/' + f'{stock_1}_{stock_2}.png'))
        plt.clf()
        # plt.show()
        # add standard dev line


# Backtest ========================================================================================================================


def backtest_pair(stock_1, stock_2, stock_1_closing_prices, stock_2_closing_prices, pair_daily_spreads, st_dev, r_sq, average_ratio):
    trades_pnl = []
    trade_enter = []
    trade_exit = []
    hold_period = []
    max_open_loss = 0
    open_price = 0
    close_price = 0
    for x in range(0,len(pair_daily_spreads)):
        if pair_daily_spreads[x] > st_dev and open_price == 0:
            open_price = pair_daily_spreads[x]
            trade_enter.append(x)
            # print("trade opened at: ", open_price)
        elif pair_daily_spreads[x] < st_dev*-1 and open_price == 0:
            open_price = pair_daily_spreads[x]
            trade_enter.append(x)
            # print("trade opened at: ", open_price)
        if open_price > 1 and pair_daily_spreads[x] < 1:
            close_price = pair_daily_spreads[x]
            trades_pnl.append(open_price - close_price)
            trade_exit.append(x)
            hold_period.append(trade_exit[len(trade_exit) - 1] - trade_enter[len(trade_enter) - 1])
            # print("trade closed at: ", close_price)
            open_price = 0
            close_price = 0
        if open_price < -1 and pair_daily_spreads[x] > -1:
            close_price = pair_daily_spreads[x]
            trades_pnl.append(close_price - open_price)
            trade_exit.append(x)
            hold_period.append(trade_exit[len(trade_exit) - 1] - trade_enter[len(trade_enter) - 1])
            # print("trade closed at: ", close_price)
            open_price = 0
            close_price = 0
        # Finding biggest open loss
        if open_price > 1:
            open_pnl = open_price - pair_daily_spreads[x]
            if open_pnl < max_open_loss:
                max_open_loss = open_pnl
        if open_price < -1:
            open_pnl = pair_daily_spreads[x] - open_price
            if open_pnl < max_open_loss:
                max_open_loss = open_pnl

    capital_leg_1 = stock_1_closing_prices[0]*average_ratio*100
    capital_leg_2 = stock_2_closing_prices[0]*100

    total_capital = capital_leg_1 + capital_leg_2
    total_return = (sum(trades_pnl)*100) / total_capital

    # print("trades PnL: ", trades_pnl)
    # print("trade enter: ", trade_enter)
    # print("trade exit: ", trade_exit)
    # print("hold period: ", hold_period)
    # print("average hold period: ", sum(hold_period) / len(hold_period) )
    # print("largest winner: ", max(trades_pnl) / (total_capital/100))
    # print("max open loss: ", max_open_loss / (total_capital/100))
    # print("number of round trips: ", len(hold_period))
    # print("total PnL per unit", sum(trades_pnl))
    # print("total profit per 100 shares: $", sum(trades_pnl)*100)

    # print("capital used on leg 1:", stock_1_closing_prices[0]*average_ratio*100)
    # print("capital used on leg 2:", stock_2_closing_prices[0]*100)
    # print("total capital used: ", total_capital)

    # print("r squared: ", r_sq)
    # print("standard dev: ", st_dev)
    # print("average ratio: ", average_ratio)
    # print("total return: ", total_return*100, "%")

    # we want to update the average ratio so its 250 trading days prior to that day, a real time rolling figure...


    if r_sq > .65:
    # csv write line for each loop - candidates > .65 r squared
        with open('candidates_high.csv', 'a', newline='') as csvfile:
            fieldnames = ['Stock 1', 'Stock 2', 'Average Ratio', 'Total Capital Used', 'Standard Dev', 'Average Hold', 'Trade Count', 'Largest Winner', 'Max Open Loss', 'R Squared', 'Total Return']
            thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # thewriter.writeheader()
            thewriter.writerow({'Stock 1': stock_1,
                                'Stock 2': stock_2,
                                'Average Ratio' : average_ratio,
                                'Total Capital Used' : total_capital,
                                'Standard Dev' : st_dev,
                                'Average Hold' : (sum(hold_period) / 7) / len(hold_period), # hold period divided by 7 if 60 min. remove if doing 1d period
                                'Trade Count' : len(hold_period),
                                'Largest Winner' : max(trades_pnl) / (total_capital/100),
                                'Max Open Loss' : max_open_loss / (total_capital/100),
                                'R Squared' : r_sq,
                                'Total Return' : total_return})
    # csv write line for each loop - candidates < .65 r squared
    else:
        with open('candidates_low.csv', 'a', newline='') as csvfile:
            fieldnames = ['Stock 1', 'Stock 2', 'Average Ratio', 'Total Capital Used', 'Standard Dev', 'Average Hold', 'Trade Count', 'Largest Winner', 'Max Open Loss', 'R Squared', 'Total Return']
            thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
            # thewriter.writeheader()
            thewriter.writerow({'Stock 1': stock_1,
                                'Stock 2': stock_2,
                                'Average Ratio' : average_ratio,
                                'Total Capital Used' : total_capital,
                                'Standard Dev' : st_dev,
                                'Average Hold' : (sum(hold_period) / 7) / len(hold_period), # hold period divided by 7 if 60 min. remove if doing 1d period
                                'Trade Count' : len(hold_period),
                                'Largest Winner' : max(trades_pnl) / (total_capital/100),
                                'Max Open Loss' : max_open_loss / (total_capital/100),
                                'R Squared' : r_sq,
                                'Total Return' : total_return})


# Pairs Trading Main ==============================================================================================================


def pairs_trade(ticker_a, ticker_b): # pass in a and b with loop
    # ticker_a = 'NVDA'
    # ticker_b = 'TSM'
    try:
        [[stock_1, stock_1_data, stock_1_closing_prices],[stock_2, stock_2_data, stock_2_closing_prices]] = get_pair(ticker_a, ticker_b)
        # print('stock_1: ', stock_1, 'stock_1_data: ', stock_1_data, 'stock_1_closing_prices: ', stock_1_closing_prices)
        # print('stock_2: ', stock_2, 'stock_2_data: ', stock_2_data, 'stock_2_closing_prices: ', stock_2_closing_prices)
    except:
        print("error")
        return

    # Pair Calculations
    pair_daily_ratios = calculate_ratio(stock_1_closing_prices, stock_2_closing_prices)
    average_ratio = (sum(pair_daily_ratios) / len(pair_daily_ratios))
    
    pair_daily_spreads = calculate_spreads(stock_1_closing_prices, stock_2_closing_prices, pair_daily_ratios, average_ratio)
    st_dev = calculate_standard_deviation(pair_daily_spreads)
    r_sq = calculate_r_squared_correlation(stock_1, stock_2, stock_1_closing_prices, stock_2_closing_prices)
    
    # Create Pandas DataFrame
    pair_dataframe = create_pair_dataframe(stock_1, stock_2, stock_1_closing_prices, stock_2_closing_prices, pair_daily_ratios, pair_daily_spreads)

    # Create matplotlib Graph / Chart of Spread
    create_graph(stock_1, stock_2, stock_1_data, pair_daily_spreads, st_dev, r_sq)

    # Backtest
    try:
        backtest_pair(stock_1, stock_2, stock_1_closing_prices, stock_2_closing_prices, pair_daily_spreads, st_dev, r_sq, average_ratio)
    except:
        print("error backtesting, length of trades is zero")
        with open('error_log.txt', 'a') as f:
            f.write(f'error backtesting trade performance for {stock_1} and {stock_2}')
            f.write('\n')
    # backtest_pair(stock_1, stock_2, stock_1_closing_prices, stock_2_closing_prices, pair_daily_spreads, st_dev*1.1, r_sq, average_ratio)
    # backtest_pair(stock_1, stock_2, stock_1_closing_prices, stock_2_closing_prices, pair_daily_spreads, st_dev*1.2, r_sq, average_ratio)
    # backtest_pair(stock_1, stock_2, stock_1_closing_prices, stock_2_closing_prices, pair_daily_spreads, st_dev*1.25, r_sq, average_ratio)
    # backtest_pair(stock_1, stock_2, stock_1_closing_prices, stock_2_closing_prices, pair_daily_spreads, st_dev*1.3, r_sq, average_ratio)
    # backtest_pair(stock_1, stock_2, stock_1_closing_prices, stock_2_closing_prices, pair_daily_spreads, st_dev*1.5, r_sq, average_ratio)
    # backtest_pair(stock_1, stock_2, stock_1_closing_prices, stock_2_closing_prices, pair_daily_spreads, st_dev*1.6, r_sq, average_ratio)
    # can backtest all the different st_dev multiples to test performance

    print(stock_1, stock_2)
    print('average_ratio: ', average_ratio)
    print('st_dev: ', st_dev, 'r_sq: ', r_sq)
    return


# pairs_trade()

# address average price for capital used 



# All Sectors ========================================================================================================================


# XLY Consumer Discretionary
xly = ['amzn', 'tsla', 'mcd', 'hd', 'low', 'nke', 'sbux', 'tjx', 'tgt', 'bkng']

# XLP Cons Staples 
xlp = ['pg', 'pep', 'ko', 'cost', 'wmt', 'pm', 'mo', 'cl', 'adm'] # 'mdlz', 

# XLF Financial  brk.b
xlf = ['jpm', 'bac', 'wfc', 'schw', 'gs', 'ms', 'spgi', 'blk', 'cb']

# XLV Healthcare
xlv = ['unh', 'jnj', 'lly', 'pfe', 'abbv', 'mrk', 'tmo', 'abt', 'bmy', 'dhr']

# XLI Industrials
xli = ['rtx', 'hon', 'unp', 'ups', 'lmt', 'cat', 'de', 'ge', 'noc', 'ba']

# XLB Materials
xlb = ['lin', 'apd', 'shw', 'ctva', 'fcx', 'ecl', 'nue', 'nem', 'dow', 'alb']

# XLK / QQQ Technology
xlk = ['aapl', 'msft', 'v', 'nvda', 'ma', 'avgo', 'csco', 'acn', 'crm', 'adbe', 'qcom', 'ibm', 'amd', 'amat', 'intc']
qqq = ['aapl', 'amzn', 'msft', 'goog', 'meta', 'nvda', 'tsla', 'pypl', 'adbe', 'nflx'] # 'adbe', 

# XLC Communications
xlc = ['meta', 'googl', 'nflx', 'chtr', 'cmcsa', 'tmus', 'dis', 't', 'vz']

# SMH Semiconductors 
smh = ['tsm', 'nvda', 'asml', 'avgo', 'txn', 'adi', 'klac', 'lrcx', 'qcom', 'intc', 'amat', 'mu', 'amd'] # 'intc', 'amat', error

# Lots of dividends - avoid for now, don't want to be short and pay the dividends:
# XLE Energy, XLRE Real Estate, XLU Utilities


# Auto Schedule Program ===============================================================================================================


# Run the program for every possible combination for two stocks within the same sector
def sector(stock_list):
    for x in range(0,len(stock_list)):
        for y in range(0,len(stock_list)):
            print("Pair: ", stock_list[x], stock_list[y])
            if x != y:
                pairs_trade(stock_list[x], stock_list[y])

def run_pairs_all_sectors():
    sector(xly)
    sector(xlp)
    sector(xlf)
    sector(xlv)
    sector(xli)
    sector(xlb)
    sector(xlk)
    sector(qqq)
    sector(xlc)
    sector(smh)

nowtime = str(datetime.datetime.now())

# Run once on first launch, then scheduler takes over
run_pairs_all_sectors()
print("I'm working...", str(datetime.datetime.now()), "First Run")

def job(t):
    # Delete these three files to start clean run
    try:
        os.remove('error_log.txt')
        os.remove('candidates_high.csv')
        os.remove('candidates_low.csv')
    except:
        pass
    time.sleep(5)
    # Run Main Pairs Trading Program on All Sectors
    run_pairs_all_sectors()
    # Confirm that the program is still working as of: time
    print("I'm working...", str(datetime.datetime.now()), t)

for i in ["06:40", "07:15", "08:00", "09:00", "10:00", "11:00", "12:00", "13:00"]:
    schedule.every().monday.at(i).do(job, i)
    schedule.every().tuesday.at(i).do(job, i)
    schedule.every().wednesday.at(i).do(job, i)
    schedule.every().thursday.at(i).do(job, i)
    schedule.every().friday.at(i).do(job, i)

while True:
    schedule.run_pending()
    time.sleep(30)
