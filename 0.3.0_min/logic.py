'''
백테스팅용 로직 설정
'''

import sqlite3
import pandas as pd

import trade_simulation
import config
import technicalanalyze


## 기술적 분석 데이터 추가
def add_technical_analyze_data(stock_data):
    ## print(stock_data)

    stock_data = technicalanalyze.PCH(stock_data, config.optmizize_list[0])
    stock_data = technicalanalyze.PCH(stock_data, config.optmizize_list[1])
    
    return stock_data

class logic():

    ## 기술적 분석 실시한 데이터 추가
    def __init__(self, stock_data):
        self.stock_data = add_technical_analyze_data(stock_data)

    ## 매수 규칙 설정
    def buy_logic(self, i):

        ## 사용자가 규칙 설정하는 부분
        ## 아래는 예제 규칙임

        if (self.stock_data.at[i, 'PCH_H_3'] < self.stock_data.at[i, 'PCH_H_3']
            ):
            return 1

        else:
            return 0

    ## 매도(현금보유) 규칙 설정
    def sell_logic(self, i):

        ## 사용자가 규칙 설정하는 부분
        ## 아래는 예제 규칙임

        if (self.stock_data.at[i, 'PCH_L_3'] > self.stock_data.at[i, 'PCH_L_3']
            ):
            return 1

        else:
            return 0

    ## 매매 포지션 사이즈 설정
    ## 포지션 사이즈 : 리퀴드 모드일때만 작동
    def control_position_size(self, today):
        position_size = 0.95
        return position_size

