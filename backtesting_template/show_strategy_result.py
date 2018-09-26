import overnight_basket

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import win32com

from pandas import DataFrame
from datetime import datetime
import time
import sqlite3    
    
class show_result_strategy():
    def __init__(self, trade_data_strategy):
        self.trade_data_strategy = trade_data_strategy

        self.daily_drawdown_dtrategy = []
        self.max_daily_drawdown_strategy = []
    

    def make_stategy_result_data(self):
        data = self.trade_data_strategy
        CAGR_strategy = round((((data.at[len(data.index) - 1, 'Basket']) / data.at[0, 'Basket'])**\
                        (1/int(len(data.index)/365.0)) - 1), 4) * 100

        roll_max_strategy = data['Basket'].rolling(len(data.index), min_periods=1).max()
        daily_drawdown_strategy = data['Basket'] / roll_max_strategy - 1.0
        max_daily_drawdown_strategy = daily_drawdown_strategy.rolling(len(data.index), min_periods=1).min()
        max_draw_dowm_strategy = round(abs(pd.Series.min(max_daily_drawdown_strategy)) * 100, 2)
        
        return_portfolio_log = np.log(data['Basket'] / data['Basket'].shift(1))
        volatility_month = pd.DataFrame.rolling(return_portfolio_log, window = 20).std() * np.sqrt(20)
        volatility_year = pd.DataFrame.rolling(return_portfolio_log, window = 252).std() * np.sqrt(252)

        data.insert(len(data.columns), "draw_down", daily_drawdown_strategy)
        data.insert(len(data.columns), "max_draw_down", max_daily_drawdown_strategy)
        data.insert(len(data.columns), "volatility_month", volatility_month)
        data.insert(len(data.columns), "volatility_year", volatility_year)

        print("CAGR : %.2f" %CAGR_strategy)
        return data

if __name__ == '__main__':
    '''
    유니버스 설정시 유의 사항
    백테스팅 기간은 맨 첫번째에 있는 종목의 상장기간으로 설정됩니다.
    '''

    etf_universe = ['A233740']
  
    backtesting = overnight_basket.Core(etf_universe, 2)
    data = backtesting.calculate_account_data()

    show_result_strategy = show_result_strategy(data)
    print(show_result_strategy.make_stategy_result_data())


'''
    def show_asset_growth_graph(self):
        fig = plt.figure(figsize=(16, 9))

        top_axes = plt.subplot2grid((4,4), (0,0), rowspan=3, colspan=4)
        bottom_axes = plt.subplot2grid((4,4), (3,0), rowspan=1, colspan=4)

        top_axes.plot(data.index, data['Basket'], label='Basket')

        bottom_axes.plot(data.index, daily_drawdown_strategy, label='draw_down')
        bottom_axes.plot(data.index, max_daily_drawdown_strategy, label='max_draw_dowm')

        top_axes.legend(loc='best')
        data.to_excel("./Backtest_result(Param = %s).xlsx" %self.param, encoding = 'euc_KR')

        plt.savefig("./BackTestResult.png" %self.param, dpi=240)       
        plt.title('strategy Result')
        plt.tight_layout()
        plt.show()
        plt.close(fig)


    def show_strategy_result_table(self):
        result_table = pd.DataFrame(columns = ['CAGR', 'MDD', 'Volluity', 'HitRatio'])
'''
