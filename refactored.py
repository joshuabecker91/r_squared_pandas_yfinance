import pandas as pd
import numpy
import yfinance as yf
import statistics
import csv
import os
# pip install pandas
# pip install numpy
# pip install yfinance

# ---------------------------------------------------------------------------------------

# for charts
import pendulum
import matplotlib.pyplot as plt
# pip install matplotlib pendulum

# can import list of spy 500 with yahoo_fin seperate library
# tickers_sp500()

# better to loop through spy 500 or do top 20 holdings in each sector one at a time?

# ---------------------------------------------------------------------------------------

def correlation(a, b):

    # a = input('Stock 1:')
    # b = input('Stock 2:')

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
                                    interval='1d', # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
                                    actions=False)
    # print(price_history_1)
    time_series1 = list(price_history_1['Close'])
    print(time_series1)

    # ---------------------------------------------------------------------------------------

    # Stock 2
    price_history_2 = yf.Ticker(stock_2).history(period='1y', # valid periods: 1d,5d,1mo,3mo,6mo,1y,2y,5y,10y,ytd,max
                                    interval='1d', # valid intervals: 1m,2m,5m,15m,30m,60m,90m,1h,1d,5d,1wk,1mo,3mo
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

    cwd = os.getcwd()

    df.to_csv(cwd + '/pairs/' + f'{a}_{b}.csv')

    # ---------------------------------------------------------------------------------------

    # find biggest open loss for each trade
    # pnl graph / equity graph

    # backtest pnl
    trades_pnl = []
    trade_enter = []
    trade_exit = []
    hold_period = []
    max_open_loss = 0
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
        # Finding biggest open loss
        if open_price > 1:
            open_pnl = open_price - spread[x]
            if open_pnl < max_open_loss:
                max_open_loss = open_pnl
        if open_price < -1:
            open_pnl = spread[x] - open_price
            if open_pnl < max_open_loss:
                max_open_loss = open_pnl


    capital_leg_1 = time_series1[0]*average_ratio*100
    capital_leg_2 = time_series2[0]*100

    total_capital = capital_leg_1 + capital_leg_2
    total_return = (sum(trades_pnl)*100) / total_capital

    print("trades PnL: ", trades_pnl)
    print("trade enter: ", trade_enter)
    print("trade exit: ", trade_exit)
    print("hold period: ", hold_period)
    print("average hold period: ", sum(hold_period) / len(hold_period) )
    print("max open loss: ", max_open_loss / (total_capital/100))
    print("number of round trips: ", len(hold_period))
    print("total PnL per unit", sum(trades_pnl))
    print("total profit per 100 shares: $", sum(trades_pnl)*100)

    print("capital used on leg 1:", time_series1[0]*average_ratio*100)
    print("capital used on leg 2:", time_series2[0]*100)
    print("total capital used: ", total_capital)

    print("r squared: ", R_sq)
    print("standard dev: ", st_dev)
    print("average ratio: ", average_ratio)
    print("total return: ", total_return*100, "%")

    # we want to make it monitor the ratios every minute, not just once a day...

    # csv write line for each loop
    with open('candidates.csv', 'a', newline='') as csvfile:
        fieldnames = ['Stock 1', 'Stock 2', 'Average Ratio', 'Total Capital Used', 'Standard Dev', 'Average Hold', 'Trade Count', 'Max Open Loss', 'R Squared', 'Total Return']
        thewriter = csv.DictWriter(csvfile, fieldnames=fieldnames)
        # thewriter.writeheader()
        thewriter.writerow({'Stock 1': stock_1,
                            'Stock 2': stock_2,
                            'Average Ratio' : average_ratio,
                            'Total Capital Used' : total_capital,
                            'Standard Dev' : st_dev,
                            'Average Hold' : sum(hold_period) / len(hold_period),
                            'Trade Count' : len(hold_period),
                            'Max Open Loss' : max_open_loss / (total_capital/100),
                            'R Squared' : R_sq,
                            'Total Return' : total_return})
        # for item in data:


    # ---------------------------------------------------------------------------------------

    # Creating a Graph / Chart
    dt_list = [pendulum.parse(str(dt)).float_timestamp for dt in list(price_history_1.index)]
    plt.style.use('dark_background')
    plt.plot(dt_list, spread, linewidth=2)
    plt.savefig((cwd + '/figs/' + f'{a}_{b}.png'))
    plt.clf()
    # plt.show()


# ---------------------------------------------------------------------------------------

# make modular with different functions to call for loop 
# and write to csv

#  10 semi conductors call the function double for loop skip itself and write to cvs the results of each


# smh 
stock_list = ['tsm', 'nvda', 'asml', 'avgo', 'txn', 'amat', 'adi', 'klac', 'lrcx', 'qcom', 'intc', 'mu', 'amd']

for x in range(0,len(stock_list)):
    for y in range(x+1,len(stock_list)):
        print("Pair: ", stock_list[x], stock_list[y])
        if x != y:
            correlation(stock_list[x], stock_list[y])