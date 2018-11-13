import pandas as pd
import numpy as np
import sqlite3
import win32com.client
import time
from datetime import datetime

today = datetime.now()
todaystamp = today.year * 10000 + today.month * 100 + today.day 

class DataBase():
    def __init__(self, config_number):
        self.CpStockCode = win32com.client.Dispatch("CpUtil.CpStockCode")
        self.CpCodeMgr = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        self.StockChart = win32com.client.Dispatch("CpSysDib.StockChart")
        self.CpStatus = win32com.client.Dispatch("CpUtil.CpCybos")
        self.CpInvestorTrends = win32com.client.Dispatch("CpSysDib.CpSvr7254")
        
        ## 입력 컨픽 넘버에 따른 호출데이터 설정
        self.flag = int(config_number)
        self.data_array_bighand_trend = [0, 2, 3, 4, 5, 8, 9, 16, 17, 20, 21]
        self.data_array_price_volume = [0, 2, 3, 4, 5, 8, 9]

    def CallStockData(self, stock_code):
        fromDate = self.CpCodeMgr.GetStockListedDate(stock_code)

        self.StockChart.SetInputValue(0, stock_code)  # 종목코드
        self.StockChart.SetInputValue(1, ord('1'))  # 기간으로 받기
        self.StockChart.SetInputValue(2, todaystamp)  # To 날짜
        self.StockChart.SetInputValue(3, fromDate)  # From 날짜

        if self.flag == 1:
            self.StockChart.SetInputValue(5, self.data_array_price_volume)

        elif self.flag == 2:
            self.StockChart.SetInputValue(5, self.data_array_bighand_trend)

        else:
            return False
        '''
        호출 데이터
        날짜, OHLC 데이터, 거래량, 거래대금, 외국인보유수량, 외국인보유비율, 기관순매수, 기관누적선매수
        뒤에 주석처리한거는 외인기관동향 관련 자료. 2011년부터 로드되서 주석처리.
        '''
        self.StockChart.SetInputValue(6, ord('D'))    # 차트 구분 (일)
        self.StockChart.SetInputValue(9, ord('1'))  # 수정주가 사용

        ## 데이터 호출
        self.StockChart.BlockRequest()
        num = self.StockChart.GetHeaderValue(3)
        data=[]

        ## 상장일부터 프로그램 실행일까지 데이터 호출
        for i in range(num):
            tempData ={}
            tempData['Date'] = self.StockChart.GetDataValue(0, i)
            tempData['Open'] = self.StockChart.GetDataValue(1, i)
            tempData['High'] = self.StockChart.GetDataValue(2, i)
            tempData['Low'] = self.StockChart.GetDataValue(3, i)
            tempData['Close'] = self.StockChart.GetDataValue(4, i)
            tempData['TradeVolume'] = self.StockChart.GetDataValue(5, i)
            tempData['TradeAmount'] = self.StockChart.GetDataValue(6, i)

            if self.flag == 1:
                data.append(tempData)

            elif self.flag == 2:
                tempData['ForeginerVolume'] = self.StockChart.GetDataValue(7, i)
                tempData['Foreginerratio'] = self.StockChart.GetDataValue(8, i)
                tempData['CompanyVolume'] = self.StockChart.GetDataValue(9, i)
                tempData['CompanyVolumeTotal'] = self.StockChart.GetDataValue(10, i)
                data.append(tempData)

            else:
                return False

        ## 다만 호출한 데이터를 그대로 쓰게되면 날짜가 최신 -> 옛날순으로 가므로 리버스해서 역순에서 정순을 바꿔준다.
        data.reverse()

        if self.flag == 1:
            StockData =  pd.DataFrame(data, columns = ['Date','Open','High','Low','Close','TradeVolume','TradeAmount'])

        elif self.flag == 2:
            StockData =  pd.DataFrame(data, columns = ['Date','Open','High','Low','Close','TradeVolume','TradeAmount', 'Foreginerratio','CompanyVolume','CompanyVolumeTotal'])  

        else:
            return False

        return StockData

    ## 대기시간 체크(TR 제한이 15초에 30개이다)
    def checkRemainTime(self):
        remainTime = self.CpStatus.LimitRequestRemainTime
        remainCount = self.CpStatus.GetLimitRemainCount(1) # 시세 제한
 
        if remainCount <= 0:
                timeStart = time.time()
                while remainCount <= 0 :
                    time.sleep(remainTime/1000)
                    remainCount = self.CpStatus.GetLimitRemainCount(1)  # 시세 제한
                    remainTime = self.CpStatus.LimitRequestRemainTime   
                ellapsed = time.time() - timeStart
                print("시간 지연: %.2f" %ellapsed, "시간:", remainTime)

    ## 특정 종목코드에 대한 데이터 호출(Out : Dataframe)
    def importstockdata(stock_code):
        con = sqlite3.connect('kospi.db')
        stockdata = pd.read_sql("SELECT * FROM %s" %stock_code, con, index_col = None)
        return stockdata 

    ## Database 제작
    def MakeDatabase(self):
        kospi = self.CpCodeMgr.GetStockListByMarket(1) # 코스피
        kosdaq = self.CpCodeMgr.GetStockListByMarket(2) # 코스닥
        code_list = list(kospi + kosdaq) #종목 리스트로 합침

        con = sqlite3.connect('kospi.db')

        for i in range(len(code_list)):
            Stockdata = self.CallStockData(code_list[i])
            Stockdata.to_sql(str(code_list[i]), con, if_exists='replace')
            print("[%s / %s] %s 수집 완료" %(i+1, len(code_list), code_list[i]))
            self.checkRemainTime()
            i+=1
    
if __name__ == "__main__":
    print("종목 데이터 수집")
    config_num = input('1 - 가격, 거래량만 / 2 - 기관,외인 거래동향까지 : ')
    CreateData = DataBase(config_num)
    CreateData.MakeDatabase()
    print("DB 생성 완료")
