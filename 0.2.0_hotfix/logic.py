## 백테스팅용 로직 설정
import sqlite3
import pandas as pd

import config
import technicalanalyze


## 기술적 분석 데이터 추가
def add_technical_analyze_data(stock_code):

    ## DB에서 원하는 종목 데이터 호출
    stock_raw_data = 'stock_data_%s.db' %config.backtesting_time_peroid ## 코스피 DB 파일
    con = sqlite3.connect(stock_raw_data) 
    stock_data = pd.read_sql("SELECT * FROM %s" %stock_code, con, index_col=None)

    ## 기술적 분석 데이터 출력
    stock_data = technicalanalyze.MA(stock_data['Close'], config.optmizize_1)  

    return stock_data


## logic 함수의 결과에 따른 매수 포지션 설정
def set_position(stock_data):

    ## 첫날에는 매수를 실시하지 않는다. 
    ## 어제 오늘 데이터를 비교하기 때문에 어제 데이터가 없으므로 하지않음.
    position_array = ['Hold'] * len(stock_data.index)
    today = 1

    ## 전체 포지션 설정
    for i in range(len(stock_data.index)-1):

        ## 조건에 맞으면 Buy Position
        if logic(stock_data, today) == 1 :
            position_array[i+1] = 'Buy'

        ## 조건에 맞지 않으면 Hold Position
        else:    
            position_array[i+1] = 'Hold'
        
        today += 1    
    
    return position_array



## 매매 로직 설정
## 현재 주석처리 되어있는 코드는 어제보다 오늘 시가가 높을 경우 매수포지션
def buy_logic(stock_data, today):
    yesterday = today - 1
    if (stock_data.at[today, "indicator_1"] > stock_data.at[today, "indicator_2"]
    ):
        return 1

    else:
        return 0

def sell_logic(stock_data, today):
    yesterday = today - 1
    if (stock_data.at[today, "indicator_1"] > stock_data.at[today, "indicator_2"]
    ):
        return 1

    else:
        return 0

def logic(stock_data, today):
    yesterday = today - 1
    if (stock_data.at[yesterday, "Close"] < stock_data.at[today, "Close"]
    ):
        return 1

    else:
        return 0

## 매매 포지션 사이즈 설정
## 포지션 사이즈 : 리퀴드 모드일때만 작동
def control_position_size(today):
    position_size = 0.95
    return position_size