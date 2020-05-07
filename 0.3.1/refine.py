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

class end_timing_betting():
    def __init__(self, code):
        self.code = code
        self.database = sqlite3.connect('stock_price(5min).db')
        self.price_data = pd.DataFrame()

    def import_database(self):
        c = self.database.cursor()
        sql = "SELECT date, close, volume FROM %s" %self.code
        self.price_data = pd.read_sql(sql, con = self.database)

        return self.price_data

    def refine(self):

        self.price_data['time'] = self.price_data['date'].astype(str).str.slice(start=-4).astype(int)
        self.price_data['date'] = self.price_data['date'].astype(str).str.slice(stop=-4).astype(int)
        self.price_data = self.price_data[(self.price_data['time'] >= 1500) | (self.price_data['time'] <= 930)]
        self.price_data = self.price_data.reset_index(drop=True)          

        print(self.price_data)

    def calculate(self):
        end_data = self.price_data[(self.price_data['time'] >= 1500) | (self.price_data['time'] <= 1510)]
        ovn_data = self.price_data[self.price_data['time'] <= 930]

        end_data['profit_0900'] = self.

    def run(self):
        self.import_database()
        self.calculate()

        return True

if __name__ == '__main__':
    analyze = end_timing_betting('A233740')
    analyze.refine()
