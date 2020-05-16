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

## my custom library
import broker
import filter_stock
import rank_stock
import vis

logic_name = 'Overnight'
start_date = datetime.datetime(2016, 1, 2)
end_date = datetime.datetime(2020, 5, 8)
# start_balance = 10000000 ## 현재 지원되지 않는 기능  

broker = broker.broker(logic_name, start_date, end_date, start_balance)
trading_day_list = broker.get_trade_date_list()

if __name__ == '__main__':

    ## 1. 종목 필터 리스트 추출
    filter = filter_stock.filter_stock_list()
    filter.run()

    for day in trading_day_list:

        

