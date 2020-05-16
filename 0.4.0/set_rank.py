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

'''
종목 랭킹 추출
'''
class rank_stock_list():
    
    def __init__(self):
        self.rank_table = pd.DataFrame()
        self.raw_database = sqlite3.connect('stock_price(day).db')
        self.rank_database = sqlite3.connect('stock_rank.db')

    ## Database 호출
    def import_database(self, stock_code):
        c = self.raw_database.cursor()
        sql = "SELECT date, volume FROM %s" %stock_code
        data = pd.read_sql(sql, con = self.raw_database)

        return data

    def get_stock_code_list(self):
        cursor = self.raw_database.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        
        db_code_list = cursor.fetchall()

        return db_code_list

    def get_trade_date_list(self):
        c = self.raw_database.cursor()
        sql = "SELECT date FROM A069500" 

        datetime_raw_list = pd.read_sql(sql, con = self.raw_database)
        datetime_list = datetime_raw_list.loc[(datetime_raw_list['date'] > 20150101)]        

        return datetime_list['date']
    
    def rank_volume(self):
        code_list = self.get_stock_code_list()
        temp_data = pd.DataFrame(self.get_trade_date_list()).reset_index(drop=True)
        k=0
        
        for code in code_list:
            k=k+1
            print('%s / %s' %(k, len(code_list)))

            price_data = self.import_database(code)
            price_data = price_data.loc[(price_data['date'] > 20150101)]  
            temp_data = pd.merge(temp_data, price_data, on='date', how='outer')
            temp_data = temp_data.fillna(0)
            temp_data = temp_data.rename(columns = {'volume' : '%s' %code}).astype('int32')

        rank_data = temp_data.rank(method='max', ascending=False, axis=1).astype('int32')
        rank_data.to_hdf('rank_volume', key = 'df')

        return True

    def run(self):
        self.rank()

        return True


if __name__ == '__main__':
    rank = rank_stock_list()
    rank.run()


    

    
