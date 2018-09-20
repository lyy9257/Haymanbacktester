## 다종목 오버나잇(종가매수 시가매도) 백테스팅 템플릿

import create_data_base
import logic_overnight

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import win32com

from pandas import DataFrame
from datetime import datetime
import time
import sqlite3

resultdata = []

flag = 0

class Core():

    ## 파라미터 설정
    def __init__(self, stock_universe, k):

        self.stock_universe = stock_universe ## 종목 바스켓
        self.stockdata = 'kospi.db' ## 코스피 DB 파일
        self.con = sqlite3.connect(self.stockdata) 
        self.param = k ## 전략에 파라미터 들어갈때 사용
        self.trade_fee = 0.022 ## 크레온 수수료 0.011%

    ## 기술적 분석 데이터 추가
    def add_technical_analyze_data(self, stock_code):

        ## DB에서 원하는 종목 데이터 호출
        stock_data = pd.read_sql("SELECT * FROM %s" %stock_code, self.con, index_col=None)

        return stock_data

    ## 종목별 포지션 계산
    def set_position(self, stock_code):

        stock_data = self.add_technical_analyze_data(stock_code)
        position_array = logic_overnight.set_position(stock_data)

        return position_array


    ## 포지션에 따른 수익률 계산
    def calculate_profit(self, stock_code):

        position_data = self.set_position(stock_code)
        stock_data = self.add_technical_analyze_data(stock_code)
        profit_array = [1] ## 첫날에는 매수를 하지 않기 때문에 수익률이 0%

        today = 1
        yesterday = 0

        while today < len(position_data):

            ## 어제 Buy Position이었으면 전일 종가에 매수, 금일 시가에 매도 수익률을 돌려준다.
            if position_data[yesterday] == 'Buy':
                temp_profit = ((stock_data.at[today, "Open"]) / stock_data.at[yesterday, "Close"]) * (1 - (self.trade_fee/100))
                profit_array.append(temp_profit)

            ## 조건에 안맞으면 아무것도 하지 않음.
            else:    
                temp_profit = 1
                profit_array.append(temp_profit)
           
            today += 1
            yesterday += 1

        return profit_array

    ## 각 종목별 수익률 데이타 합성
    def merge_total_trade_data(self):

        total_trade_data = pd.DataFrame()
      
        for i in range(len(self.stock_universe)):
            temp_profit_data = self.calculate_profit(self.stock_universe[i])
            temp_profit_data.reverse()
            total_trade_data.insert(len(total_trade_data.columns), "%s" %self.stock_universe[i], pd.Series(temp_profit_data))   
            i += 1
            print("%d / %d" %(i, len(self.stock_universe)))

        total_trade_data = total_trade_data.reindex(index=total_trade_data.index[::-1])
        total_trade_tata = total_trade_data.fillna(1, inplace=True)
        total_trade_data["profit_average"] = total_trade_data.mean(axis=1)

        return total_trade_data
        
    ## 수익률에 따른 잔고 반영
    def calculate_account_data(self):
        
        account_data = [1000]
        profit_data = self.merge_total_trade_data()

        for i in range(len(profit_data.index)):
            temp_account_data = account_data[i] * 0.95 * profit_data.at[i, "profit_average"] + account_data[i] * 0.05
            account_data.append(temp_account_data)
            i += 1    

        account_data_dataframe = pd.DataFrame(account_data, columns = ['Basket']) 
        account_data_dataframe = pd.concat([account_data_dataframe, profit_data], axis=1)

        temp_date_data = self.add_technical_analyze_data(self.stock_universe[0])
        account_data_dataframe = pd.concat([account_data_dataframe, temp_date_data['Date']], axis=1)

        return account_data_dataframe

    ## 그래프 출력
    def draw_graph(self):

        data = self.calculate_account_data()
        
        CAGR_Strategy = round((((data.at[len(data.index) - 1, 'Basket']) / 1000)**(1/int(len(data.index)/365.0)) - 1), 4) * 100

        Roll_Max_Strategy = data['Basket'].rolling(len(data.index), min_periods=1).max()
        Daily_Drawdown_Strategy = data['Basket'] / Roll_Max_Strategy - 1.0
        Max_Daily_Drawdown_Strategy = Daily_Drawdown_Strategy.rolling(len(data.index), min_periods=1).min()

        data.insert(len(data.columns), "DD", Daily_Drawdown_Strategy)
        data.insert(len(data.columns), "MDD", Max_Daily_Drawdown_Strategy)

        fig = plt.figure(figsize=(16, 9))

        top_axes = plt.subplot2grid((4,4), (0,0), rowspan=3, colspan=4)
        bottom_axes = plt.subplot2grid((4,4), (3,0), rowspan=1, colspan=4)

        top_axes.plot(data.index, data['Basket'], label='Basket')

        bottom_axes.plot(data.index, Daily_Drawdown_Strategy, label='DD')
        bottom_axes.plot(data.index, Max_Daily_Drawdown_Strategy, label='MDD')

        top_axes.legend(loc='best')
        data.to_excel("./BackTestResult(Param = %s).xlsx" %self.param, encoding = 'euc_KR')

        MDD_Strategy = round(abs(pd.Series.min(Max_Daily_Drawdown_Strategy)) * 100, 2)
        print('Strategy Result, CAGR : %.2f %%, MDD : %.2f %%, C/M : %.2f' %(CAGR_Strategy, MDD_Strategy, CAGR_Strategy/MDD_Strategy))

        plt.savefig("./BackTestResult(Param = %s).png" %self.param, dpi=240)       
        plt.title('Strategy Result, CAGR : %.2f %%, MDD : %.2f %%, C/M : %.2f' %(CAGR_Strategy, MDD_Strategy, CAGR_Strategy/MDD_Strategy))
        plt.tight_layout()
        plt.show()
        plt.close(fig)


if __name__ == '__main__':
    '''
    유니버스 설정시 유의 사항
    백테스팅 기간은 맨 첫번째에 있는 종목의 상장기간으로 설정됩니다.
    '''

    etf_universe = ['A114800']
  
    backtesting = Core(etf_universe, 2)
    backtesting.draw_graph()