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
import ta_lib
import set_rank
import filter_stock_list



'''
사용자가 로직을 입력하는 부분
'''
class main():
    def __init__(self, stock_code, day_data, min_data):
        self.stock_code = stock_code
        self.day_data = day_data
        self.min_data = min_data

    ## 이 함수의 내용을 작성하세요
    ## output : DataFrame(type : bool)
    '''
    (불가능) 시가총액 : 50억원 이하
    
    (A) 0봉전 10봉 거래량 100,000 이상
    (B) 종가 > 이평(60일)
    (C) 0봉전 25봉 이내에서 종가대비 고가 15%이상
    '''
    def filter_logic_day(self, data = self.day_data, stock_code = self.stock_code):
        temp_data = pd.DataFrame()

        temp_data = ta_lib.sma_price(data, stock_code, 'volume', 10) ## MA_volume_10
        temp_data = ta_lib.sma(data, stock_code, 'close', 60) ## MA_close_60
        temp_data = ta_lib.compare_price(data, stock_code, 'high', 'close') ## 고가 대비 종가
        temp_data['high_by_close_15'] = temp_data['high_by_close'] > 15
        temp_data['high_by_close_15_check'] = temp_data.rolling(25)['high_by_close_15'].sum()

        temp_data['logic'] = (temp_data['MA_volume_10'] > 100000) & 
            (temp_data['MA_close_60'] < temp_data['close']) & (temp_data['high_by_close_15_check'] == 1)
        
        bool_data_day = temp_data[['date', 'logic']]

        return bool_data_day 

    '''    
    (A) 이격도 90, 120 1% 이내
    (B) 종가 > 볼린저밴드 상한선(종가, 80, 2)
    (C) 이격도 20, 120 2% 이내
    '''
    def filter_logic_minute(self, data = self.min_data, stock_code = self.stock_code):
        
        temp_data = ta_lib.sma_price(data, stock_code, 'close', 90)
        temp_data = ta_lib.sma_price(data, stock_code, 'close', 120)
        temp_data = ta_lib.sepr_price(data, stock_code, 'MA_close_90', 'MA_close_120', 1) ## 이격도 90, 120 1% 이내

        temp_data = ta_lib.bbands(data, stock_code, 'close', 800, 2, 2) ## 볼린저밴드(종가, 80, 2)

        temp_data = ta_lib.sma_price(data, stock_code, 'close', 90)
        temp_data = ta_lib.sma_price(data, stock_code, 'close', 120)
        temp_data = ta_lib.sepr_price(data, stock_code, 'MA_close_90', 'MA_close_120', 2) ## 이격도 20, 120 2% 이내

        temp_data['logic'] = (temp_data['SEP_1'] < 101) & 
            (temp_data['upper'] < temp_data['close']) & (temp_data['SEP_2'] < 102) & 
            (temp_data['SEP_1'] > 100) & (temp_data['SEP_2'] > 100)

        bool_data_min = temp_data[['date', 'logic']]

        return bool_data_min 

    def run(self):
        filter = filter_stock.main()
        filter.run()






class main():

    def __init__(self):
        self.rank_table = pd.DataFrame()
        self.raw_database = sqlite3.connect('stock_price(day).db')

    ## Database 호출
    def import_database(self, stock_code):
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
        filter_day = pd.DataFrame(self.get_trade_date_list()).reset_index(drop=True)
        filter_min = pd.DataFrame(self.get_trade_date_list()).reset_index(drop=True)

        for code in code_list:
            print('%s / %s' %(k, len(code_list)))
             
            price_data = self.import_database(code)

            get_logic = logic.main(code, price_data)
            logic_day = get_logic.filter_logic_day()
            logic_min = get_logic.filter_logic_min()

            filter_day = pd.merge(filter_day, logic_day, on='date', how='outer')
            filter_day = filter_day.rename(columns = {'logic' : '%s' %code})

            filter_min = pd.merge(filter_min, logic_min, on='date', how='outer')
            filter_min = filter_min.rename(columns = {'logic' : '%s' %code})

        filter_day.to_hdf('filter_day' %logic_idx, key = 'df')
        filter_min.to_hdf('filter_min' %logic_idx, key = 'df')

        return True

    
    def run(self):
        filtered_stock_list = self.make_filter_list()
        
        return filtered_stock_list