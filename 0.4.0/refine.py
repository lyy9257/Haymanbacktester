# Perfomance
import asyncio
import multiprocessing
import parmap

# Data Control
import numpy as np
import pandas as pd

# DB Control
import sqlite3
from sqlalchemy import create_engine
import pymysql

## etc
import datetime
import talib

# Graph
import matplotlib
from matplotlib import style, font_manager, rc
import matplotlib.pyplot as plt

import plotly.express as px
import plotly.graph_objects as go  
import plotly.figure_factory as ff

import seaborn as sns
import squarify # pip install squarify


class end_timing_betting():

    ## 초기화
    def __init__(self, code):
        self.code = code
        self.database = sqlite3.connect('stock_price(5min).db')
        self.price_data = pd.DataFrame()

    ## Database 호출
    def import_database(self):
        c = self.database.cursor()
        sql = "SELECT date, open, close, volume FROM %s" %self.code
        self.price_data = pd.read_sql(sql, con = self.database)

        return True

    ## 데이터 정제
    def refine(self):
        self.price_data['time'] = self.price_data['date'].astype(str).str.slice(start=-4).astype(int)
        self.price_data['date'] = self.price_data['date'].astype(str).str.slice(stop=-4).astype(int)
        self.price_data['date'] = self.price_data['date'].apply(lambda x: pd.to_datetime(str(x), format='%Y%m%d'))
        self.price_data = self.price_data[(self.price_data['time'] >= 1450) | (self.price_data['time'] <= 930)]
        self.price_data = self.price_data.reset_index(drop=True)          

        return True

    ## 로직 입력
    '''
    로직 입력 방법
    Logic Column을 bool type의 데이터로 넘겨주세요.
    (True시 투자, False시 미투자)
    '''

    '''
    일봉 패턴분석 
    '''

    def logic(self):
        logic_dataframe = self.price_data[['date', 'time']]

        self.price_data['upperband'], self.price_data['middleband'], self.price_data['lowerband'] = talib.BBANDS(self.price_data['close'])
        
        ## logic_dataframe['Logic'] = self.price_data['High']
        
        print(self.price_data)
        ## return logic_dataframe['Logic']

    ## 계산
    def calculate(self):
        profit_data = pd.DataFrame()
        profit_data['date'] = self.price_data['date'].drop_duplicates().reset_index(drop=True)
        
        ### 주식 거래시간 연장 전후로 분리
        temp_1 = profit_data[profit_data['date'] < datetime.datetime(2017, 8, 1)]
        temp_2 = profit_data[profit_data['date'] >= datetime.datetime(2017, 8, 1)]
        
        ### 10분전 동시호가때 종가로 종가 매수
        temp_price_1 = self.price_data.loc[(self.price_data['time'] == 1450) & (self.price_data['date'] < datetime.datetime(2017, 8, 1)), ['date', 'close']]
        temp_price_2 = self.price_data.loc[(self.price_data['time'] == 1520) & (self.price_data['date'] >= datetime.datetime(2017, 8, 1)), ['date', 'close']]

        ### 날짜를 Key로 맞추어 종가 합체
        temp_1 = temp_1.merge(temp_price_1)
        temp_2 = temp_2.merge(temp_price_2)

        ### 거래시간 연장 전,후 데이터를 합체한 뒤 인덱스 초기화
        ### 이후 시가 임포팅
        temp = pd.concat([temp_1, temp_2]).reset_index(drop=True)
        temp = temp.merge(self.price_data.loc[self.price_data['time'] == 910, ['date', 'open']])

        ### 시가를 -1칸 시프트 하는 이유는 D+1일 시가에 팔 것이기 때문이다.
        temp['open'] = temp['open'].shift(-1)
        
        ### 로직 입력
        self.logic()
        temp['Logic'] = True

        #temp = temp.merge(self.logic())

        ### 일일수익률, 누적수익률 계산
        temp['profit_D+1'] = temp['open'] / temp['close'] * (1-0.015/100) - 1
    
        ### 로직에 맞지 않는곳은 수익률 0(미투자)으로 변경
        temp.loc[temp['Logic'] != True, 'profit_D+1'] = 0

        temp['total'] = (temp['profit_D+1'] + 1).cumprod() * 100
        temp['total'] = (temp['total'] - 100).round(2)
        temp['profit_D+1'] = (temp['profit_D+1'] * 100 ).round(2)

        temp = temp.dropna()

        return temp
        


    def run(self):
        self.import_database()
        self.refine()

        result = self.calculate()

        self.get_result(result)
        self.draw_graph(result)

        return True

if __name__ == '__main__':
    input_code = input("원하는 종목코드 입력(숫자 6자리) : ")
    analyze = end_timing_betting('A'+ str(input_code))
    analyze.run()
