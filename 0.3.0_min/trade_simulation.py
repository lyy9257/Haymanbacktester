'''
백테스팅 시뮬레이션 데이터 제작
단일 전략, 분봉 데이터 기반
'''


import logic
import config

import xlrd, xlwt
import xlsxwriter
import sqlite3
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import math


## 주식 데이터 호출
class call_raw_data():

    ## 파라미터 설정
    def __init__(self):
        self.stock_universe = config.stock_universe ## 종목 바스켓
        self.position_size = config.position_size ## 포지션 사이즈
        self.backtesting_time_peroid = config.backtesting_time_peroid ## 백테스팅 타임프레임 간격(DB 호출용)

        self.con = sqlite3.connect('stock_data_%s.db' %self.backtesting_time_peroid) ## 종목 데이터 호출용 DB 연결

        self.raw_data_dataframe = pd.DataFrame() ## 종목별 주가 데이터 저장용 데이터프레임 

    ## 종목별 데이터 호출
    def call_stock_raw_data(self):
        
        '''
        백테스팅 실행 전 종목 데이터 호출   
        '''
        
        backtestng_data = pd.read_sql("SELECT * FROM %s" %(self.stock_universe[0]), self.con, index_col=None)
        self.raw_data_dataframe = backtestng_data

        return self.raw_data_dataframe


## 백테스팅 실시
class run_simulation_buy_and_hold():

    ## 파라미터 설정
    def __init__(self, stock_raw_data):
        self.stock_universe = config.stock_universe ## 종목 바스켓
        self.position_size = 0.95 ## 포지션 사이즈 (벤치마크이므로 95% 투자 고정)

        self.raw_data_df = stock_raw_data ## 종목별 주가 데이터 저장용 데이터프레임 
        self.profit_df = pd.DataFrame() ## 종목별 단순 바이앤 홀딩 저장용 데이터프레임

    ## 단순 바이앤 홀딩 데이터 생성
    def make_index_trade_data(self):

        ## 종가 데이터 추가
        self.profit_df["close"] = self.raw_data_df['Close']

        ## 종목별 수익률 측정
        self.profit_df['hold'] = self.raw_data_df['Close'] / self.raw_data_df['Close'].shift(1)   
        self.profit_df = self.profit_df.fillna(1)

        ## 기본 잔고 = 1000
        account_data = [1000] * len(self.profit_df.index)

        ## 1000원 투자시 수익률 측정
        for i in range(len(self.profit_df.index) - 1):
            stock_ratio = account_data[i] * self.position_size * self.profit_df.at[i, "hold"]
            cash_ratio = account_data[i] * (1 - self.position_size)
            temp_account_data =  cash_ratio + stock_ratio
            account_data[i+1] = temp_account_data
            i += 1   

        self.profit_df["account_buy_and_hold"] = account_data

        return self.profit_df


class run_simulation_strategy():

    ## 파라미터 설정
    def __init__(self, stock_raw_data):
        self.stock_universe = config.stock_universe ## 종목 바스켓
        self.trade_fee = config.trade_fee  ## 왕복 수수료
        self.trade_tax = config.trade_tax  ## 편도 거래세
        self.position_size = config.position_size ## 포지션 사이즈 (벤치마크이므로 95% 투자 고정)

        self.raw_data_df = stock_raw_data ## 종목별 주가 데이터 저장용 데이터프레임 
        self.profit_strategy_df = pd.DataFrame(stock_raw_data) ## 트레이딩 결과 데이터프레임
        self.account_strategy_df = pd.DataFrame() ## 잔고 변화 데이터프레임
   
    ## 전략에 따른 매수매도 포지션 설정
    def make_strategy_position_data(self):
        position_data = ['sell'] * len(self.profit_strategy_df.index)
        logic_data = logic.logic(self.profit_strategy_df)

        ## 포지션 데이터 설정
        for i in range(max(config.optmizize_list), len(position_data) - 1):
            buy_signal = logic_data.buy_logic(i)
            sell_signal = logic_data.sell_logic(i)   

            ## 매수 시그널 발생시
            if buy_signal == 1 and sell_signal == 0:
                position_data[i] = 'buy'
            
            else:
                position_data[i] = 'sell'

            i += 1
        
        self.profit_strategy_df['position'] = position_data

        return self.profit_strategy_df

    ## 전략에 따른 트레이딩 데이터 생성
    def make_strategy_trade_data(self):

        #사용 데이터 호출
        self.profit_strategy_df = self.make_strategy_position_data()
        stock_data = self.profit_strategy_df
        profit_table = ['1'] * len(self.profit_strategy_df)

        ## 포지션 데이터에 따른 일일 수익률 설정
        for i in range (max(config.optmizize_list), len(profit_table) - 1):
            position_today = self.profit_strategy_df.at[i, 'position']

            if i > 0:
                position_yesterday = self.profit_strategy_df.at[i - 1, 'position']

            if i == 0:
                if position_today == 'buy':
                    profit_table[i] = 1 * (1 - (self.trade_fee/100))

                else:
                    profit_table[i] = 1
                
                i+=1

            else:
                ## 매수 포지션
                ## 수익률 = 종가에 매수하였으므로 전일 수익률 * (1 - 증권 거래수수료) 
                if position_yesterday == 'sell' and position_today == 'buy':
                    profit_table[i] = 1 * (1 - (self.trade_fee/100))

                ## 매수 유지 포지션
                ## 수익률 = 전일 수익률 * 전일 종가 / 금일 종가 
                elif position_yesterday == 'buy' and position_today == 'buy':
                    profit_table[i] = 1 * (stock_data.at[i, "Close"] / stock_data.at[i-1, "Close"])

                ## 매도 포지션
                ## 수익률 = 전일 수익률 * 전일 종가 / 금일 종가 * (1 - 증권 거래수수료 - 증권거래세)
                elif position_yesterday == 'buy' and position_today == 'sell':
                    profit_table[i] = 1 * (stock_data.at[i, "Close"] / stock_data.at[i-1, "Close"]) * (1 - (self.trade_fee/100) - (self.trade_tax/100))

                ## 현금 보유 포지션
                else:    
                    profit_table[i] = 1

        self.profit_strategy_df['strategy'] = profit_table

        return self.profit_strategy_df

    ## 계좌 데이터 설정
    def make_strategy_account_data(self):

        ## 종가 데이터 추가
        self.account_strategy_df = self.make_strategy_trade_data()

        ## 기본 잔고 = 1000
        account_data = [1000] * len(self.account_strategy_df.index)

        ## 1000원 투자시 수익률 측정
        for i in range(len(self.account_strategy_df.index) - 1):
            stock_ratio = account_data[i] * self.position_size * float(self.account_strategy_df.at[i, "strategy"])
            cash_ratio = account_data[i] * (1 - self.position_size)
            temp_account_data =  cash_ratio + stock_ratio
            account_data[i+1] = temp_account_data
            i += 1   

        self.account_strategy_df["account_strategy"] = account_data

        ## Drawdowm 및 Max Drawdown 측정
        temp_df = self.account_strategy_df["account_strategy"]

        roll_max_strategy = temp_df.rolling(len(self.account_strategy_df.index), min_periods=1).max()
        daily_drawdown_strategy = temp_df / roll_max_strategy - 1.0
        max_daily_drawdown_strategy = daily_drawdown_strategy.rolling(len(temp_df.index), min_periods=1).min()
        max_draw_dowm_strategy = round(abs(pd.Series.min(max_daily_drawdown_strategy)) * 100, 2)

        self.account_strategy_df.insert(len(self.account_strategy_df.columns), "daily_drawdown", daily_drawdown_strategy)
        self.account_strategy_df.insert(len(self.account_strategy_df.columns), "max_draw_down", max_daily_drawdown_strategy)

        return self.account_strategy_df


## 엑셀 파일로 저장
class write_to_excel():

    ## 파라미터 설정
    def __init__(self):
        self.result_book = xlsxwriter.Workbook('strategy_result.xlsx')


    ## sheet 별 데이터 저장
    ## 저장 순서 : [전략 결과] - [종목 로우데이터] - [단순 바이앤 홀딩 데이터] - [전략 트레이딩 데이터]
    def export(self, raw_data, index_data, strategy_data):
        writer = pd.ExcelWriter('strategy_result.xlsx', engine='xlsxwriter')
        
        raw_data.to_excel(writer, sheet_name='raw data')
        index_data.to_excel(writer, sheet_name='index trade data')
        strategy_data.to_excel(writer, sheet_name='strategy trade data')
        
        writer.save()
    
if __name__ == "__main__":
    call_raw_data_from_database = call_raw_data()
    stock_raw_data = call_raw_data_from_database.call_stock_raw_data()

    run_buy_and_hold = run_simulation_buy_and_hold(stock_raw_data)
    run_strategy = run_simulation_strategy(stock_raw_data)

    excel = write_to_excel()
    
    index_trade_data = run_buy_and_hold.make_index_trade_data()
    strategy_trade_data = run_strategy.make_strategy_account_data()

    ## print(strategy_trade_data)

    excel.export(stock_raw_data, index_trade_data, strategy_trade_data)






