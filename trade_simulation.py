'''
백테스팅 시뮬레이션 데이터 제작
'''

import logic
import config

import xlsxwriter
import sqlite3
import pandas as pd
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt

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
        종목의 [날짜, 시가, 고가, 종가, 저가, 거래량] 데이터를 호출한다.
        출력 컬럼 형태 : (칼럼이름)_(종목코드) 형식으로 반환이 된다.
        * intersection(교집합)을 이용하여 여러종목 합성을 가능하게 할 예정.
        '''
        
        for i in range(len(self.stock_universe)):
            stock_data_column = pd.read_sql("SELECT * FROM %s" %(self.stock_universe[i]), self.con, index_col=None)
            stock_data_column.set_index('Date')            
            stock_data_column = stock_data_column.add_suffix('_%s'%(self.stock_universe[i]))
            stock_data_column = stock_data_column.drop(['index_%s'%(self.stock_universe[i])], axis=1)
            print(stock_data_column)
            
            if i == 0:
                self.raw_data_dataframe = stock_data_column
   
            else:
                self.raw_data_dataframe = pd.merge(dfA, dfB, how='inner', on=['S', 'T'])                                    

        return self.raw_data_dataframe


## 백테스팅 실시
class run_simulation_buy_and_hold():

    ## 파라미터 설정
    def __init__(self, stock_raw_data):
        self.stock_universe = config.stock_universe ## 종목 바스켓
        self.position_size = 0.95 ## 포지션 사이즈 (벤치마크이므로 95% 투자 고정)

        self.raw_data_dataframe = stock_raw_data ## 종목별 주가 데이터 저장용 데이터프레임 
        self.profit_buy_and_hold_dataframe = pd.DataFrame() ## 종목별 단순 바이앤 홀딩 저장용 데이터프레임
        self.profit_strategy_dataframe = pd.DataFrame() ## 트레이딩 결과 데이터프레임

    ## 단순 바이앤 홀딩 데이터 생성
    def make_index_trade_data(self):

        ## 종목별 수익률 측정
        for i in range(len(self.stock_universe)):
            stock_code = self.stock_universe[i]
            self.profit_buy_and_hold_dataframe['hold_%s' %stock_code] = self.raw_data_dataframe['Close_%s' %stock_code] / self.raw_data_dataframe['Close_%s' %stock_code].shift(1)

        ## 통합 수익률 측정
        self.profit_buy_and_hold_dataframe["profit_average"] = self.profit_buy_and_hold_dataframe.mean(axis=1)
        self.profit_buy_and_hold_dataframe = self.profit_buy_and_hold_dataframe.fillna(1)       

        ## 기본 잔고 = 1000
        account_data_buy_and_hold = [1000] * len(self.profit_buy_and_hold_dataframe.index)

        ## 1000원 투자시 수익률 측정
        for i in range(len(self.profit_buy_and_hold_dataframe.index) - 1):
            temp_account_data = account_data_buy_and_hold[i] * self.position_size * self.profit_buy_and_hold_dataframe.at[i, "profit_average"] + account_data_buy_and_hold[i] * (1 - self.position_size)
            account_data_buy_and_hold[i+1] = temp_account_data
            i += 1   

        self.profit_buy_and_hold_dataframe["account_buy_and_hold"] = account_data_buy_and_hold

        return self.profit_buy_and_hold_dataframe


class run_simulation_strategy():

    ## 파라미터 설정
    def __init__(self, stock_raw_data):
        self.stock_universe = config.stock_universe ## 종목 바스켓
        self.trade_fee = config.trade_fee  ## 왕복 수수료
        self.trade_tax = config.trade_tax  ## 편도 거래세
        self.position_size = config.position_size ## 포지션 사이즈 (벤치마크이므로 95% 투자 고정)

        self.raw_data_dataframe = stock_raw_data ## 종목별 주가 데이터 저장용 데이터프레임 
        self.profit_strategy_dataframe = pd.DataFrame(stock_raw_data, columns=['Date']) ## 트레이딩 결과 데이터프레임
    
    ## 전략에 따른 매수매도 포지션 설정
    def make_strategy_position_data(self):
        buy_signal = logic.buy_logic
        sell_signal = logic.sell_logic
        position_data = ['sell'] * len(self.profit_buy_and_hold_dataframe.index)

        ## 포지션 데이터 설정
        for i in range(len(position_data)):
            
            ## 매수 시그널 발생시
            if buy_signal == 1:
                position_data[i] = 'buy'
            
            elif sell_signal == 1:
                position_data[i] = 'sell'

            else:
                if i == 0:
                    position_data[i] = 'sell'
                else:
                    position_data[i] = position_data[i-1]

            i += 1
        
        print(position_table)
        self.profit_strategy_dataframe['position'] = position_table
        
        return self.profit_strategy_dataframe

    ## 전략에 따른 트레이딩 데이터 생성
    def make_strategy_trade_data(self):
        profit_table = ['1'] * len(self.profit_strategy_dataframe)

        ## 포지션 데이터에 따른 일일 수익률 설정
        for i in range (len(position_data)):
            if i == 0:
                if self.profit_strategy_dataframe.at[i, 'position'] == 'buy':
                    profit_table[i] = 1 * (1 - (self.trade_fee/100))

                else:
                    profit_table[i] = 1
                
                i+=1

            else:
        
                ## 매수 포지션
                ## 수익률 = 종가에 매수하였으므로 전일 수익률 * (1 - 증권 거래수수료) 
                if position_data[yesterday] == 'hold' and self.profit_strategy_dataframe.at[i, 'position'] == 'buy':
                    profit_table[i] = 1 * (1 - (self.trade_fee/100))

                ## 매수 유지 포지션
                ## 수익률 = 전일 수익률 * 전일 종가 / 금일 종가 
                elif self.profit_strategy_dataframe.at[i-1, 'position'] == 'buy' and self.profit_strategy_dataframe.at[i, 'position'] == 'buy':
                    profit_table[i] = 1 * (stock_data.at[today, "Close"] / stock_data.at[yesterday, "Close"])
                    profit_array[i+1] = temp_profit

                ## 매도 포지션
                ## 수익률 = 전일 수익률 * 전일 종가 / 금일 종가 * (1 - 증권 거래수수료 - 증권거래세)
                elif self.profit_strategy_dataframe.at[i-1, 'position'] == 'buy' and self.profit_strategy_dataframe.at[i, 'position'] == 'sell':
                    temp_profit = 1 * (stock_data.at[today, "Close"] / stock_data.at[yesterday, "Close"]) * (1 - (self.trade_fee/100) - (self.trade_tax/100))
                    profit_array[i+1] = temp_profit

                ## 현금 보유 포지션
                else:    
                    temp_profit = 1
                    profit_array[i+1] = temp_profit
           
                today += 1
                yesterday += 1
    
        return self.profit_strategy_dataframe


## 엑셀 파일로 저장
class write_to_excel():

    ## 파라미터 설정
    def __init__(self):
        self.raw_data_dataframe = call_raw_data.call_stock_raw_data() ## 주가 데이터 저장 데이터프레임 
        self.profit_buy_and_hold_dataframe = pd.Dataframe() ## 바이앤 홀딩 데이터프레임
        self.profit_strategy_dataframe = pd.Dataframe() ## 전략 트레이딩 데이터프레임

    ## 전략 성과 요약 테이블 제작
    def make_strategy_summary(self):

        return True

    ## sheet 별 데이터 저장
    ## 저장 순서 : [전략 결과] - [종목 로우데이터] - [단순 바이앤 홀딩 데이터] - [전략 트레이딩 데이터]
    def export_trade_data_to_excel(self):
    
        return True


if __name__ == "__main__":
    call_raw_data_from_database = call_raw_data()
    stock_raw_data = call_raw_data_from_database.call_stock_raw_data()

    run_backtest = run_simulation(stock_raw_data)

    print(run_backtest.make_index_trade_data())

