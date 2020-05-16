# Perfomance
import asyncio
import multiprocessing
import parmap

# Data Control
import pandas as pd
import numpy as np

# DB Control
import sqlite3
import pymysql
from sqlalchemy import create_engine

## etc
import talib
import datetime

'''
정밀계산용 브로커 모듈
추후 버전업시 개발 예정
'''

'''
class broker(self):

    def __init__(self, name, start_date, end_date, start_balance):

        ### 시작일, 종료일, 시작잔고, 거래일 리스트 생성
        self.start_date = start_date
        self.end_date = end_date
        self.balance = balance
        self.datetime_filtered_list = pd.Series()

        
        ### 종가 기준가 저장용 데이터베이스 설정
        self.database = sqlite3.connect('stock_price(day).db')

        ### 종목 보유 로그 기록
        self.stock_basket = pd.DataFrame(
            columns=['Date', 'Code', 'Trade', 'Start_price', 'End_price']
        )

        ### 계좌 잔고 기록
        self.account_log = pd.DataFrame(
            columns=['Date', 'basket_amount', 'Stock', 'Stock_weight', 'Cash', 'Cash_weight', 'Start_asset_total', 'End_asset_total']
        )
    
    
    ## df.apply 전용 함수
    def get_price(date, code, point):
        c = database.cursor()
        sql = "SELECT %s FROM A%s" %(point, code)

        price = pd.read_sql(sql, con = self.database).loc[self.price_data[date] == date].values
        return price

    ## 거래 날짜 리스트 획득
    ## 이 날짜를 기반으로 트레이딩을 실시.
    def get_trade_date_list(self):
        c = database.cursor()
        sql = "SELECT date FROM A069500" 

        datetime_raw_list = pd.read_sql(sql, con = self.database)
        self.datetime_filtered_list = datetime_raw_list.loc[(self.price_data['date'] > self.start_date) | (self.price_data['date'] < self.end_date)]        

        return self.datetime_filtered_list

    ## 매수로그 추가
    def add_buy(self, date, stock_code, buy_price):
        end_price = self.get_price(date, stock_code, 'close')
        temp_basket = pd.DataFrame({'Date': date, 'Code':stock_code, 'Trade':'Buy', 'Start_price':buy_price, 'End_price':end_price})

        temp_basket =  temp_basket[['Date', 'Code', 'Trade', 'Start_price', 'End_price']]

        self.stock_basket = pd.concat([self.stock_basket, temp_basket])

        return True

    ## 매도로그 추가
    def add_sell(self, date, stock_code, sell_price):
        start_price = self.get_price(date, stock_code, 'open')
        temp_basket = pd.DataFrame({'Date': date, 'Code':stock_code, 'Trade':'Sell', 'Start_price':start_price, 'End_price':sell_price})

        temp_basket =  temp_basket[['Date', 'Code', 'Trade', 'Start_price', 'End_price']]

        self.stock_basket = pd.concat([self.stock_basket, temp_basket])

        return True

    ## 홀드로그 추가
    def add_hold(self, today):
        yesterday = self.datetime_filtered_list[self.datetime_filtered_list == today].index[-1]

        buy_stock_list = self.stock_basket.loc[(self.stock_basket['date'] == yesterday) & (self.stock_basket['Trade'] == 'Buy'), 'Code']
        sell_stock_list  = self.stock_basket.loc[(self.stock_basket['date'] == today) & (self.stock_basket['Trade'] == 'Sell'), 'Code']

        hold_stock_list = pd.concat([buy_stock_list, sell_stock_list]).drop_duplicates(keep=False)
        hold_stock_list['Date'] = today
        hold_stock_list['Trade'] = 'Hold'
        hold_stock_list['Start_Price'] = hold_stock_list.apply(lambda x : self.get_price(x['Date'], x['Code'], 'open'))
        hold_stock_list['End_Price'] = hold_stock_list.apply(lambda x : self.get_price(x['Date'], x['Code'], 'close'))

        hold_stock_list = hold_stock_list[['Date', 'Code', 'Trade', 'Start_price', 'End_price']]

        self.stock_basket = pd.concat([self.stock_basket, temp_basket])

        return True

    ## 금일 결산내역 계산 - 종가기준
    def add_account_log(self, date):

        ## 종가 기준으로 일일 잔고 산출
        buy_stock_list = self.stock_basket.loc[(self.stock_basket['Trade'] == 'Buy')]
        hold_stock_list = self.stock_basket.loc[(self.stock_basket['Trade'] == 'Hold')]
        
        basket_amount = buy_stock_list.index + hold_stock_list.index  ## 금일 종가 기준 보유 종목 갯수 선정

        ['Date', 'basket_amount', 'Stock', 'Stock_weight', 'Cash', 'Cash_weight', 'Start_asset_total', 'End_asset_total']

'''