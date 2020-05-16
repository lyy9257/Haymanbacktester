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

class broker(self):

    def __init__(self, name, start_date, end_date, start_balance, fee):

        ### 시작일, 종료일, 시작잔고, 거래일 리스트 생성
        self.start_date = start_date
        self.end_date = end_date
        self.balance = balance
        self.datetime_filtered_list = pd.Series()

        self.fee = fee
        self.tax = 0.25

        ### 종가 기준가 저장용 데이터베이스 설정
        self.database = sqlite3.connect('stock_price(day).db')

        ### 종목 보유 로그 기록
        self.stock_basket = pd.DataFrame(
            columns=['Date', 'Code', 'Trade', 'Start_price', 'End_price', 'Predict_buyable_amount']
        )

        ### 계좌 잔고 기록
        self.account_log = pd.DataFrame(
            columns = ['Date', 'basket_amount', 'profit_day']
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
        end_price = self.get_price(date, stock_code, 'close') ### 종가(마감가)
        profit = (end_price / buy_price * (1 - self.fee/100) - 1) * 100 ### 매수 기준 수익률
        predict_buyable_amount = int(self.get_price(date, stock_code, 'volume') * 0.01) ### 예상 체결가능 수량 (매수타임 당시 거래량 1%)

        buy_basket = pd.DataFrame({
            'Date': date, 'Code':stock_code, 'Trade':'Buy', 'Start_price':buy_price, 'End_price':end_price,
            'Profit_day':profit, 'Predict_buyable_amount':predict_buyable_amount
        })

        buy_basket = temp_basket[['Date', 'Code', 'Trade', 'Start_price', 'End_price', 'Predict_buyable_amount']]

        self.stock_basket = pd.concat([self.stock_basket, buy_basket])

        return True

    ## 매도로그 추가
    def add_sell(self, date, stock_code, sell_price):
        start_price = self.get_price(date, stock_code, 'open') ### 시가(시작가)
        profit = (sell_price / start_price * (1 - self.fee/100 - self.tax/100) - 1) * 100 ### 매도 기준 수익률
        predict_sellable_amount = int(self.get_price(date, stock_code, 'volume') * 0.01) ### 예상 체결가능 수량 (매도타임 당시 거래량 1%)

        sell_basket = pd.DataFrame({
            'Date': date, 'Code':stock_code, 'Trade':'Sell', 'Start_price':start_price, 'End_price':sell_price,
            'Profit_day':profit, 'Predict_buyable_amount':predict_sellable_amount
        })

        sell_basket = temp_basket[['Date', 'Code', 'Trade', 'Start_price', 'End_price', 'Predict_buyable_amount']]

        self.stock_basket = pd.concat([self.stock_basket, sell_basket])

        return True

    ## 홀드로그 추가
    def add_hold(self, today):
        yesterday = self.datetime_filtered_list[self.datetime_filtered_list == today].index[-1]

        buy_stock_list = self.stock_basket.loc[(self.stock_basket['date'] == yesterday) & (self.stock_basket['Trade'] == 'Buy'), 'Code']
        sell_stock_list  = self.stock_basket.loc[(self.stock_basket['date'] == today) & (self.stock_basket['Trade'] == 'Sell'), 'Code']

        hold_basket = pd.concat([buy_stock_list, sell_stock_list]).drop_duplicates(keep=False)
        hold_basket['Date'] = today 
        hold_basket['Trade'] = 'Hold'
        hold_basket['Start_Price'] = hold_basket.apply(lambda x : self.get_price(x['Date'], x['Code'], 'open')) ### 시가(시작가)
        hold_basket['End_Price'] = hold_basket.apply(lambda x : self.get_price(x['Date'], x['Code'], 'close')) ### 종가(시작가)
        hold_basket['Profit_day'] = (hold_basket['End_Price'] / hold_basket['Start_Price'] - 1) * 100 ### 홀딩시 수익률
        hold_basket['Predict_buyable_amount'] = 0  ### 홀딩은 예상 체결가능 수량을 설정하지 않음.

        hold_basket = hold_basket[['Date', 'Code', 'Trade', 'Start_price', 'End_price', 'Profit_day', 'Predict_buyable_amount']]

        self.stock_basket = pd.concat([self.stock_basket, hold_basket])

        return True

    ## 금일 결산내역 계산 - 종가기준
    def add_account_log(self, date):

        ### 종가 기준으로 일일 잔고 산출
        ### 일일 총 수익률 산출 : 금일 매매한 종목의 전체 수익률합 / 거래한 종목 수량
        today_basket_list = self.stock_basket.loc[(self.stock_basket['Trade'] == 'Buy') | (self.stock_basket['Trade'] == 'Hold')] ### 종가기준 현재 보유중인 주식 정보 산출
        basket_amount = len(today_basket_list.index) ### 금일 종가 기준 보유 종목 갯수 산출
        profit_day = today_basket_list['profit'].sum()/basket_amount ### 일 수익률 산출
        
        today_account_log = pd.DataFrame({'Date':date, 'basket_amount':basket_amount, 'profit_day':profit_day]})

        self.account_log = pd.concat([self.account_log, today_account_log])

        return True

    ## 트레이딩 끝나면 종목보유 리스트, 계좌로그 반환
    def finish(self):
        return (self.stock_basket, self.account_log)




