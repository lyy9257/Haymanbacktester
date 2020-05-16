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

'''
모든 함수는 종목코드, 가격데이터, 지표를 만드는데 필요한 변수를 받아서
date와 지표_(종목코드)의 이름을 가지는 column으로 반한됩니다.

pd.merge 함수를 이용해 날짜를 key로 하여 join하여 사용합니다.
'''

# 주가이동평균
def sma(data, stock_code, col_name, time):
    data["MA_%s_%s" %(col_name, time)] = talib.SMA(data['%s' %col_name], timeperiod=time).astype(int)    

    return data 

# (주가) 대비 (주가)
def compare_price(data, stock_code, col_1, col_2):
    data["%s_by_%s" %(col_1, col_2)] = ((data['%s' %col_1] / data['%s' %col_2] - 1) * 100).round(2)

    return data 

# 이격도
def sepr_price(data, stock_code, col1, col2, idx):
    data["SEP_%s" %idx] = ((data['%s' %col1] / data['%s' %col2] - 1) * 100).round(2) 

    return data 

# ATR
def atr(data, stock_code, price_data, time):
    data['ATR'] = talib.ATR(data['high'], data['high'], data['high'], timeperiod=time).astype(int)    

    return data 

# 볼린저 밴드
def bbands(data, stock_code, col, time, devup, devdown):
    data["upper"], data["middle"], data["lower"] = talib.BBANDS(
        data['%s' %col], timeperiod=5, nbdevup=2, nbdevdn=2, matype=0).astype(int)    

    return data 


