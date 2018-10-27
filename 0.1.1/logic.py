## 백테스팅용 로직 설정
import sqlite3
import pandas as pd

import config
import technicalanalyze

## 기술적 분석 데이터 추가
def add_technical_analyze_data(stock_code):

    stockdata = 'kospi.db' ## 코스피 DB 파일
    con = sqlite3.connect(stockdata) 

    param_1 = config.optmizize_1 ## 기술적 분석에 사용되는 파라미터 1
    param_2 = config.optmizize_2 ## 기술적 분석에 사용되는 파라미터 2

    ## DB에서 원하는 종목 데이터 호출
    stock_data = pd.read_sql("SELECT * FROM %s" %stock_code, con, index_col=None)

    RSI_Short = technicalanalyze.RSI(stock_data['Low'], param_1)
    RSI_Long = technicalanalyze.RSI(stock_data['Low'], param_2)
  
    stock_data.insert(len(stock_data.columns), "RSI_Short", RSI_Short)      
    stock_data.insert(len(stock_data.columns), "RSI_Long", RSI_Long)

    return stock_data


## logic 함수의 결과에 따른 매수 포지션 설정
def set_position(stock_data):

    position_array = ['Hold']
    ## 첫날에는 매수를 실시하지 않는다. 
    ## 어제 오늘 데이터를 비교하기 때문에 어제 데이터가 없으므로 하지않음.

    today = 1

    ## 전체 포지션 설정 
    while today < len(stock_data.index):

        ## 조건에 맞으면 Buy Position
        if logic(stock_data, today) == 1 :
            position_array.append('Buy')

        ## 조건에 맞지 않으면 Hold Position
        else:    
            position_array.append('Hold')
        
        today += 1    

    return position_array


## 매매 로직 설정
## 현재 주석처리 되어있는 코드는 어제보다 오늘 시가가 높을 경우 매수포지션
def logic(stock_data, today):
    yesterday = today - 1
    if (stock_data.at[today, "RSI_Long"] <= stock_data.at[today, "RSI_Short"] and
        stock_data.at[yesterday, "Low"] < stock_data.at[today, "Low"]
    ):
        return 1

    else:
        return 0
