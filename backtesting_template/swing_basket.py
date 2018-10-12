## 다종목 스윙(해당일 종가매수 해당일 종가매도) 백테스팅 템플릿

import create_data_base
import logic

import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import win32com

from pandas import DataFrame
from datetime import datetime
import time
import sqlite3

import config

resultdata = []
flag = 0

class Core():

    ## 파라미터 설정
    def __init__(self, stock_universe, k):

        self.stock_universe = stock_universe ## 종목 바스켓
        self.stockdata = 'kospi.db' ## 코스피 DB 파일
        self.con = sqlite3.connect(self.stockdata) 
        self.param = k ## 전략에 파라미터 들어갈때 사용
        
        self.trade_fee = config.trade_fee * 2 ## 왕복 수수료
        self.trade_tax = config.trade_tax
        self.position_size = config.position_size

    ## 기술적 분석 데이터 추가
    def add_technical_analyze_data(self, stock_code):

        ## DB에서 유니버 소속 종목 데이터 호출
        stock_data = pd.read_sql("SELECT * FROM %s" %stock_code, self.con, index_col=None)

        return stock_data


    ## 종목별 포지션 설정
    def set_position(self, stock_code):

        stock_data = self.add_technical_analyze_data(stock_code)
        position_array = logic.set_position(stock_data)

        return position_array


    ## 포지션에 따른 수익률 계산
    def calculate_profit(self, stock_code):

        position_data = self.set_position(stock_code)
        stock_data = self.add_technical_analyze_data(stock_code)
        profit_array = [1] ## 첫날에는 매수를 하지 않기 때문에 수익률이 0%

        today = 1
        yesterday = 0

        while today < len(position_data):

            ## 매수 포지션
            ## 수익률 = 종가에 매수하였으므로 전일 수익률 * (1 - 증권 수수료) 
            if position_data[yesterday] == 'Hold' and position_data[today] == 'Buy':
                temp_profit = profit_array[yesterday] * (1 - (self.trade_fee/100))
                profit_array.append(temp_profit)

            ## 매수 유지 포지션
            ## 수익률 = 전일 수익률 * 전일 종가 / 금일 종가 
            elif position_data[yesterday] == 'Buy' and position_data[today] == 'Buy':
                temp_profit = profit_array[yesterday] * (stock_data.at[today, "Close"]) / stock_data.at[yesterday, "Close"])
                profit_array.append(temp_profit)

            ## 매도 포지션
            ## 수익률 = 전일 수익률 * 전일 종가 / 금일 종가 
            elif position_data[yesterday] == 'Buy' and position_data[today] == 'Hold':
                temp_profit = profit_array[yesterday] * (stock_data.at[today, "Close"]) / stock_data.at[yesterday, "Close"]) * (1 - (self.trade_fee/100) - (self.trade_tax/100))
                profit_array.append(temp_profit)

            ## 현금 보유 포지션
            else:    
                temp_profit = profit_array[yesterday]
                profit_array.append(temp_profit)
           
            today += 1
            yesterday += 1

        return profit_array


    ## 각 종목별 수익률 데이터 합성
    def merge_total_trade_data(self):

        ## 총 수익 데이터 저장용 Dataframe 선언
        total_trade_data = pd.DataFrame()
      
        ## 종목별 수익률 로드후 데이터프레임에 저장
        for i in range(len(self.stock_universe)):
            temp_profit_data = self.calculate_profit(self.stock_universe[i])
            temp_profit_data.reverse()
            total_trade_data.insert(len(total_trade_data.columns), "%s" %self.stock_universe[i], pd.Series(temp_profit_data))   
            i += 1

        ## 종목별 수익률의 평균 산출    
        total_trade_data = total_trade_data.reindex(index=total_trade_data.index[::-1])
        total_trade_tata = total_trade_data.fillna(1, inplace=True)
        total_trade_data["profit_average"] = total_trade_data.mean(axis=1)

        return total_trade_data
        

    ## 수익률에 따른 잔고 반영
    def calculate_account_data(self):
        
        ## 기본 잔고 = 1000
        account_data = [1000]
        profit_data = self.merge_total_trade_data()

        ## 기본 잔고 = 1000
        for i in range(len(profit_data.index)):
            temp_account_data = account_data[i] * self.position_size * profit_data.at[i, "profit_average"] + account_data[i] * (1 - self.position_size)
            account_data.append(temp_account_data)
            i += 1    

        account_data_dataframe = pd.DataFrame(account_data, columns = ['Basket']) 
        account_data_dataframe = pd.concat([account_data_dataframe, profit_data], axis=1)

        temp_date_data = self.add_technical_analyze_data(self.stock_universe[0])
        account_data_dataframe = pd.concat([account_data_dataframe, temp_date_data['Date']], axis=1)

        return account_data_dataframe

