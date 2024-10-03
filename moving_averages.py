import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

name = input("Enter your name: ")

ticker = input("Enter ticker of the stock you would like to trade: ").upper()

start_date = input("Enter the start date in the format 'YYYY-MM-DD': ")

end_date = input("Enter the end date in the format 'YYYY-MM-DD': ")

interval = input("Enter the interval (1d, 1wk, 1mo): ")

short_window = int(input("Enter the short window for the moving average: "))

long_window = int(input("Enter the long window for the moving average: "))

initial_capital = float(input("Enter the initial capital for the portfolio: "))


def fetch_stock_data(ticker, start_date, end_date, interval): 
    ''' None -> DataFrame
    Returns the stock data of the stock in the form of a DataFrame'''
    stock_data = yf.download(ticker, start=start_date, end=end_date, interval=interval)
    return stock_data

def moving_averages(data, short_window, long_window): 
    ''' DataFrame, int, int -> DataFrame
    Returns the stock data with the short and long moving averages'''
    data['Short_Moving_Avg'] = data['Close'].rolling(window=short_window, min_periods=1).mean()
    data['Long_Moving_Avg'] = data['Close'].rolling(window=long_window, min_periods=1).mean()
    return data

def generate_signals(data, short_window):
    ''' DataFrame -> DataFrame
    Returns the stock data with the buy and sell signals'''
    data['Signal'] = 0
    data['Signal'][short_window:] =\
        (data['Short_Moving_Avg'][short_window:] > data['Long_Moving_Avg'][short_window:]).astype(int)
    data['Position'] = data['Signal'].diff()
    return data 

def stimulate_trading(data, initial_capital): 
    ''' DataFrame -> floats
    Returns the users portfolio'''
    positions = pd.DataFrame(index=data.index).fillna(0.0)
    positions['Stock_Position'] = 100*data['Signal']
    portfolio = positions.multiply(data['Close'], axis=0)
    pos_diff = positions.diff()

    portfolio['Holdings'] = (positions.multiply(data['Close'], axis=0)).sum(axis=1)
    portfolio['Cash'] = initial_capital - (pos_diff.multiply(data['Close'], axis=0)).sum(axis=1).cumsum()
    portfolio['Total'] = portfolio['Cash'] + portfolio['Holdings']
    portfolio['Returns'] = portfolio['Total'].pct_change()

    return portfolio

def plot_results(data, portfolio):
    plt.figure(figsize=(16, 10))
    plt.plot(data['Close'], label='Stock Price', alpha=0.5)
    plt.plot(data['Short_Moving_Avg'], label=f'{short_window} Day Short Moving Average', alpha=0.5)
    plt.plot(data['Long_Moving_Avg'], label=f'{long_window} Day Long Moving Average', alpha=0.5)

    plt.plot(data[data['Position'] == 1].index,
                data['Short_Moving_Avg'][data['Position'] == 1],
                '^', markersize=5, color='green', lw=0, label='Buy Signal')
    
    plt.plot(data[data['Position'] == -1].index,
                data['Short_Moving_Avg'][data['Position'] == -1],
                'v', markersize=5, color='red', lw=0, label='Sell Signal')
    
    plt.title('Moving Averages Crossover Strategy')
    plt.legend()
    plt.show()

    plt.figure(figsize=(16, 10))
    plt.plot(portfolio['Total'], label=f"{name}'s Portfolio Value", alpha=0.5)
    plt.title('Portfolio Performance')
    plt.legend()
    plt.show()


data = fetch_stock_data(ticker, start_date, end_date, interval)  
data = moving_averages(data, short_window, long_window)
data = generate_signals(data, short_window)
portfolio = stimulate_trading(data, initial_capital)
plot_results(data, portfolio)