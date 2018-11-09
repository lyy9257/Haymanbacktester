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
        self.stock_universe = config.basket_universe ## 종목 바스켓
        self.position_size = config.position_size ## 포지션 사이즈
        self.backtesting_time_peroid = config.backtesting_time_peroid ## 백테스팅 타임프레임 간격(DB 호출용)

        self.con = sqlite3.connect('stock_data_%s.db' %self.backtesting_time_peroid) ## 종목 데이터 호출용 DB 연결

        self.raw_data_dataframe = pd.DataFrame() ## 종목별 주가 데이터 저장용 데이터프레임 

    ## 종목별 데이터 호출
    def call_stock_raw_data(self):

        ## 데이터베이스 호출 컬럼 리스트
        database_column_list = ['Date', 'Open', 'High', 'Low', 'Close', 'TradeVolume']
        
        ## 포지션 설정 전 종목 데이터 호출   
        ## 종목의 [날짜, 시고종저가, 거래량] 데이터를 호출한다.
        for i in range(len(self.stock_universe)):
            for j in range(len(database_column_list)):
            stock_data_column = pd.read_sql("SELECT %s FROM %s" %(database_column_list[j], self.stock_universe[i]), con, index_col=None)
            self.raw_data_dataframe.insert(len(self_raw_data_dataframe.columns), "%s_%s"%(database_column_list[j], self.stock_universe[i]), stock_data_column)

        return self.raw_data_dataframe


## 백테스팅 실시
class run_simulation():

    ## 파라미터 설정
    def __init__(self):
        self.stock_universe = config.stock_universe ## 종목 바스켓
        self.trade_fee = config.trade_fee  ## 왕복 수수료
        self.trade_tax = config.trade_tax  ## 편도 거래세
        self.position_size = config.position_size ## 포지션 사이즈

        self.raw_data_dataframe = call_raw_data.call_stock_raw_data() ## 종목별 주가 데이터 저장용 데이터프레임 
        self.profit_buy_and_hold_dataframe = pd.Dataframe() ## 종목별 단순 바이앤 홀딩 저장용 데이터프레임
        self.profit_strategy_dataframe = pd.Dataframe() ## 트레이딩 결과 데이터프레임

    ## 단순 바이앤 홀딩 데이터 생성
    def make_index_trade_data(self):

        return self.profit_buy_and_hold_dataframe

    ## 전략에 따른 트레이딩 데이터 생성
    def make_strategy_trade_data(self):

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

    ## sheet 별 데이터 저장
    ## 저장 순서 : [전략 결과] - [종목 로우데이터] - [단순 바이앤 홀딩 데이터] - [전략 트레이딩 데이터]
    def export_trade_data_to_excel(self):