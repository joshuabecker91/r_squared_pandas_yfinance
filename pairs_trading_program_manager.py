import pandas as pd
import numpy
import csv
import os
import schedule
import datetime
import time
import yfinance as yf
import math

cwd = os.getcwd()

account_size = 250000
leverage = 4
capital = account_size * leverage


def get_recent_candidates_dataframe():
    df = pd.read_csv('candidates_high.csv', names=['Stock 1',
                                                    'Stock 2',
                                                    'Average Ratio',
                                                    'Total Capital Used', 
                                                    'Standard Dev', 
                                                    'Average Hold', 
                                                    'Trade Count',
                                                    'Largest Winner',
                                                    'Max Open Loss',
                                                    'R Squared',
                                                    'Total Return'])
                                            # header=None)

    # Sort by Highest R Squared / Descending
    df2 = df.sort_values(by=['R Squared'], ascending=False, inplace=False) 
    # if by index -> df2 = df.sort_values(by=9, ascending=False, inplace=False)

    # Remove Duplicates on Stock 1 and Stock 2 columns
    df3 = df2.drop_duplicates(
        subset = ['Stock 1', 'Stock 2'], # if by index # subset = [0, 1], 
        keep = 'first').reset_index(drop = True)
    # print(df3.to_string())
    # print(df3)
    
    # Can Add other filter criteria here - st dev > 4 for example and anything else
    # ***Update this to filter 40 % annualized - Filter Based on > 15% Trade Performance
    df4 = df3[df3['Total Return'] >= .15]
    
    # average_trade_count = df4['Trade Count'].mean()

    # df5 = df4[df4['Trade Count'] >= math.floor(average_trade_count*.5)]
    df5 = df4[df4['Trade Count'] >= 3]

    print(df5.to_string()) 
    print(len(df5), 'Candidates with > 15% annual performance and > trade count of 3')

    # Save dataframe to csv
    df5.to_csv('find_trade.csv', encoding='utf-8', index=False)

    return df5


# POSITIONS DATAFRAME
# if positions dataframe exists in directly - load it, otherwise create new here ...pandas dataframe for open positions / or database
# Stock 1, shares +/-, Stock 2, shares +/-, Ratio, open_spread, Date Traded
    # delete rows and add rows when a trade is made
if os.path.isfile('./open_positions.csv'):
    positions_dataframe = pd.read_csv('open_positions.csv', sep=',', header=0)
                                                            # names=['Stock 1', 
                                                            #     'Shares', 
                                                            #     'Stock 2', 
                                                            #     'Shares', 
                                                            #     'Average Ratio',
                                                            #     'Open Spread', 
                                                            #     'Standard Dev', 
                                                            #     'Date Traded'])
else:
    positions_dataframe = pd.DataFrame(columns = ['Stock 1', 'Shares', 'Stock 2', 'Shares', 'Average Ratio','Open Spread', 'Standard Dev', 'Standard Dev Ratio', 'R Squared', 'Annual Performance', 'Date Traded'])

# print(positions_dataframe)



# Find first trade opportunity where we don't already own either Stock 1 or Stock 2 on either long or short side
def is_owned(stock_1, stock_2):
    # search col 1 and 3 of position dataframe for these stocks
    # if len(positions_dataframe == 0):
        # return False
    # stock_1_string = stock_1
    # count_1 = (positions_dataframe['Stock 1'].values == str(stock_1)).sum() #.equals()
    # count_2 = (positions_dataframe['Stock 2'].values == str(stock_1)).sum()
    # count_3 = (positions_dataframe['Stock 1'].values == str(stock_2)).sum()
    # count_4 = (positions_dataframe['Stock 2'].values == str(stock_2)).sum()
    # total_count = count_1 + count_2 + count_3 + count_4
    # print(total_count, count_1, count_2, count_3, count_4)

    c1 = (stock_1 in positions_dataframe['Stock 1'].values)
    c2 = (stock_1 in positions_dataframe['Stock 2'].values)
    c3 = (stock_2 in positions_dataframe['Stock 1'].values)
    c4 = (stock_2 in positions_dataframe['Stock 2'].values)
    # print(c1, c2, c3, c4)
    # owned_in_open_positions = [c1, c2, c3, c4]
    # if not any(owned_in_open_positions):
    #     return True

    if c1 == True:
        return True
    if c2 == True:
        return True
    if c3 == True:
        return True
    if c4 == True:
        return True
    return False


# def is_outside_standard_dev():
#     # more code here
#     return True


#     WANT to check for >40% annualized rather than 15% total (or both)
def performance_metrics(total_return, trade_count, average_hold):
    average_win = total_return / trade_count
    return_per_day = average_win / average_hold
    return_per_month = return_per_day * 20
    annualized = return_per_day * 250
    return [average_win, return_per_day, return_per_month, annualized]


def get_current_stock_price(stock):
    current_stock_price = yf.Ticker(stock).history(period='1d')['Close'][0] # is this current live data or yest close?
    return current_stock_price


def calculate_position_size(stock_1, stock_2, average_ratio, current_spread):
    slot = capital / 10
    stock_1_price = get_current_stock_price(stock_1)
    stock_2_price = get_current_stock_price(stock_2)
    one_unit = abs(stock_1_price*average_ratio) + stock_2_price
    number_of_units = math.floor(slot / one_unit)
    stock_1_shares = math.floor(number_of_units * average_ratio)
    stock_2_shares = number_of_units
    if current_spread > 0:
        stock_1_shares = stock_1_shares * -1
    else:
        stock_2_shares = stock_2_shares * -1
    return [stock_1_shares, stock_2_shares]


def calculate_current_spread(stock_1, stock_2, average_ratio):
    stock_1_price = get_current_stock_price(stock_1)
    stock_2_price = get_current_stock_price(stock_2)
    spread = (stock_1_price * average_ratio) - stock_2_price
    return spread




# This may be in another file after refactoring
def place_order_open_new_pair(stock_1, stock_2, average_ratio, current_spread):
#     [stock_1_shares, stock_2_shares] = calculate_position_size(stock_1, stock_2, average_ratio)
#     if current_spread > 1:     # define which side is long and which is short depending on current_spread pos or neg
#         place_order(stock_1, stock_1_shares, "SELL")
#         time.sleep(1)
#         place_order(stock_2, stock_2_shares, "BUY")
#         time.sleep(1)
#     else:
#         place_order(stock_1, stock_1_shares, "BUY")
#         time.sleep(1)
#         place_order(stock_2, stock_2_shares, "SELL")
#         time.sleep(1)
    # write line to csv test .... send with positive or negative value for shares 1 and 2 depending on long / short

    # print("order placed: ", stock_1, stock_1_shares, "SELL") these print statements in place order function
    # print("order placed: ", stock_2, stock_2_shares, "BUY")
    # print("order placed: ", stock_1, stock_1_shares, "BUY")
    # print("order placed: ", stock_2, stock_2_shares, "SELL")
    # update entry in trade log, write line
    # test placing order IB with order
    pass


# This may be in another file
def place_order_close_pair(stock_1, stock_1_shares, stock_2, stock_2_shares, average_ratio, current_spread):
    # update entry in trade log, write line
    # get pos or neg share count to know which stock to buy or sell
    
    pass





# add current spread, rules for if negative and positive to know which is long and which is short
def find_next_trade(candidates_dataframe):
    for i in candidates_dataframe.index:
        if is_owned(candidates_dataframe['Stock 1'][i], candidates_dataframe['Stock 2'][i]) == False:
            if candidates_dataframe['Standard Dev'][i] > 4: # print(i)  # # print(candidates_dataframe.iloc[i-1])
                performance = performance_metrics(candidates_dataframe['Total Return'][i], candidates_dataframe['Trade Count'][i], candidates_dataframe['Average Hold'][i])
                if performance[3] > .30:   # if candidates_dataframe['Total Return'][i] >= .15:    # returns [average_win, return_per_day, return_per_month, annualized]
                    current_spread = calculate_current_spread(candidates_dataframe['Stock 1'][i], candidates_dataframe['Stock 2'][i], candidates_dataframe['Average Ratio'][i])
                    if abs(current_spread) > abs(candidates_dataframe['Standard Dev'][i]):
                        standard_dev_ratio = abs(current_spread) / abs(candidates_dataframe['Standard Dev'][i])
                        trade_position_size = calculate_position_size(candidates_dataframe['Stock 1'][i], candidates_dataframe['Stock 2'][i], candidates_dataframe['Average Ratio'][i], current_spread)
                        return [candidates_dataframe['Stock 1'][i], trade_position_size[0], candidates_dataframe['Stock 2'][i], trade_position_size[1], candidates_dataframe['Average Ratio'][i], current_spread, candidates_dataframe['Standard Dev'][i], standard_dev_ratio, candidates_dataframe['R Squared'][i], performance[3]]
    print("no new trade found")
    return None

# positions = [] #replace with dataframe
# names = {}

def fill_empty_slots():
    candidates_dataframe = get_recent_candidates_dataframe()
    while len(positions_dataframe) < 10:
        try:
            next_trade = find_next_trade(candidates_dataframe)
            positions_dataframe.loc[len(positions_dataframe.index)] = [next_trade[0], next_trade[1], next_trade[2], next_trade[3], next_trade[4], next_trade[5], next_trade[6], next_trade[7], next_trade[8], next_trade[9], str(datetime.datetime.now())]
        except:
            print("no trades at this time")
        # want to add a bunch of columns here. open prices, capital a, capital b, percentage possible profit...and more   r_squared, average hold time, st_dev, standard dev multiple

        # positions_dataframe.append({'Stock 1' :,
        #                             'Shares' : 
        #                             'Stock 2' :,
        #                             'Shares' :
        #                             'Average Ratio' :,
        #                             'Open Spread' :, 
        #                             'Date Traded' :, ignore_index=True)

        # place_order_open_new_pair(next_trade)

        # PLACE TRADE AND UPDATE TRADE LOG
        print(next_trade)

        # trade_confirm = input("would you like to place trade (enter y to confirm): ", next_trade)
        # if trade_confirm == "y":
        # else:
            # continue



# monitor open position on schedule every 5 minutes check prices, from yf or 1 min IB?
def monitor_positions():

    # CHECK OPEN SPREADS
    # for each position in position_dataframe:
        # current_spread = calculate_current_spread(stock_1, stock_2, ratio), if reached profit target 1 / -1 close trade


    # PLACE ANY CLOSING TRADES AND UPDATE TRADE LOG
    # current_spread = calculate_current_spread('TSM', 'NVDA', 2.055611)
    # print(current_spread)


    # CHECK FOR PROFIT TAKING RULES
            # positive and negative and spread 
    #         if open_spread > 0:
    #             if current_spread < 1:
    #                 place_order_close_pair()
    #                 # print order closed
    #         if open_spread < 0:
    #             if current_spread > -1:
    #                 place_order_close_pair()
    #                 # print order closed


    # CHECK IF SLOT OPEN LOOK FOR NEW TRADES
    if len(positions_dataframe) < 10:
        fill_empty_slots()

    print(positions_dataframe)
    # save updated position dataframe to csv
    positions_dataframe.to_csv('open_positions.csv', encoding='utf-8', index=False)


nowtime = str(datetime.datetime.now())

# Run once on first launch, then scheduler takes over
monitor_positions()
print("I'm working...", str(datetime.datetime.now()), "First Run")

def job():
    monitor_positions()
    print("I'm working...", str(datetime.datetime.now()))

schedule.every(5).minutes.do(job)

while True:
    schedule.run_pending()
    time.sleep(5)



# figure out place order orderId issue 