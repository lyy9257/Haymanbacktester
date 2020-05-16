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

## custom
import backtest
import ta_lib
'''
조건에 맞는 종목 필터링
- 종목 데이터 추출
- 로직에 맞게 추출
- 정렬 후 해당되는 종목 필터
'''

class filter_stock_list():

    def __init__(self):
        self.rank_table = pd.DataFrame()
        self.raw_database = sqlite3.connect('stock_price(day).db')
        self.rank_database = sqlite3.connect('stock_rank.db')

    ## Database 호출
    def import_day_database(self, stock_code):
        c = self.raw_database.cursor()
        sql = "SELECT * FROM %s" %stock_code
        data = pd.read_sql(sql, con = self.raw_database).astype('int32')

        return data

    ## Database 호출
    def import_min_database(self, stock_code):
        c = self.raw_database.cursor()
        sql = "SELECT * FROM %s" %stock_code
        data = pd.read_sql(sql, con = self.raw_database).astype('int32')

        return data

    ## 종목 코드 리스트 호출
    def get_stock_code_list(self):
        cursor = self.raw_database.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        
        db_code_list = cursor.fetchall()

        return db_code_list

    ## 거래일 리스트 호출
    def get_trade_date_list(self):
        c = self.raw_database.cursor()
        sql = "SELECT date FROM A069500" 

        datetime_raw_list = pd.read_sql(sql, con = self.raw_database)
        datetime_list = datetime_raw_list.loc[(datetime_raw_list['date'] > 20150101)]        

        return datetime_list['date']

    ## 필터 리스트 호출
    ## 데이터프레임 테이블로 True/False로 감별
    def make_filter_list(self):
        code_list = self.get_stock_code_list()
        filter_day_data = pd.DataFrame(self.get_trade_date_list()).reset_index(drop=True)
        
        for code in code_list:
            print('%s / %s' %(k, len(code_list)))
             
            day_data = self.import_day_database(code)
            min_data = self.import_min_database(code)

            logic = backtest.main(code, day_data, min_data)
            
            logic_day_data = logic.filter_logic_day()
            logic_min_data = logic.filter_logic_min()

            filter_day_data = pd.merge(filter_data, logic_day_data, on='date', how='outer')
            filter_day_data = filter_day_data.rename(columns = {'logic' : '%s' %code})

            filter_min_data = pd.merge(filter_data, logic_min_data, on='date', how='outer')
            filter_min_data = filter_min_data.rename(columns = {'logic' : '%s' %code})

        filter_day_data.to_hdf('filter_day', key = 'df')
        filter_min_data.to_hdf('filter_min', key = 'df')

        return True
    
    def run(self):
        filtered_stock_list = self.filter()
        
        return filtered_stock_list