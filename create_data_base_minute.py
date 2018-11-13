import pandas as pd
import sqlite3
import win32com.client
import time
from datetime import datetime

today = datetime.now()
todaystamp = today.year * 10000 + today.month * 100 + today.day 

## 종목 데이터 호출 Class
class StockChart:
    def __init__(self, stock_code):
        self.CpCodeMgr = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        self.StockChart = win32com.client.Dispatch("CpSysDib.StockChart")
        self.CpStatus = win32com.client.Dispatch("CpUtil.CpCybos")

        '''
        파라미터 종류
        stock_code : 종목코드
        flag : 호출 데이터(거래대금까지, 매매동향까지)
        '''

        self.stock_code = stock_code

        ## 입력 변수에 따른 호출데이터 설정
        self.start_date = self.CpCodeMgr.GetstockListedDate(stock_code)


    ## 데이터 호출 후 대기 시간 확인용
    def checkRemainTime(self):
        remainTime = self.CpStatus.LimitRequestRemainTime
        remainCount = self.CpStatus.GetLimitRemainCount(1) # 시세 제한 갯수
 
        if remainCount <= 0:
                timeStart = time.time()
                while remainCount <= 0 :
                    time.sleep(remainTime/1000)
                    remainCount = self.CpStatus.GetLimitRemainCount(1)  # 시세 제한
                    remainTime = self.CpStatus.LimitRequestRemainTime   
                ellapsed = time.time() - timeStart
                print("수신 대기: %.2f 초" %ellapsed)


    ## 분, 틱 데이터 호출 Method
    def call_stock_data_minute_tick(self, peroid, todaystamp=0):

        fromDate = self.CpCodeMgr.GetstockListedDate(self.stock_code)        
        count = 9999999
        data_array_price_volume = [0, 1, 2, 3, 4, 5, 8]

        self.StockChart.SetInputValue(0, self.stock_code)  # 종목코드
        self.StockChart.SetInputValue(1, ord('2'))  # 갯수로 받기
        self.StockChart.SetInputValue(4, count)  # 갯수
        self.StockChart.SetInputValue(5, data_array_price_volume) # 호출 데이터
        self.StockChart.SetInputValue(6, ord('m')) # 차트 구분 (분)
        self.StockChart.SetInputValue(7, peroid) # 분봉 단위
        self.StockChart.SetInputValue(9, ord('1'))  # 수정주가 사용

        raw_data_column = ('Date', 'Time', 'Open', 'High', 'Low', 'Close', 'TradeVolume')

        stock_raw_data = []
        receive_data = {} ## 딕셔너리 형태

        for col in raw_data_column:
            receive_data[col] = []

        receive_count = 0

        while count > receive_count:
            self.StockChart.BlockRequest()  # 요청 후 응답 대기
            self.checkRemainTime()

            receive_batch_len = self.StockChart.GetHeaderValue(3)  # 받아온 데이터 개수
            receive_batch_len = min(receive_batch_len, count - receive_count) # 정확히 count 개수만큼 받기 위함

            ## 데이터 수신하여 딕셔너리에 저장
            for i in range(receive_batch_len):
                for col_idx, col in enumerate(raw_data_column):
                    receive_data[col].append(self.StockChart.GetDataValue(col_idx, i))

            receive_count += receive_batch_len
            ## print('{} / {}'.format(receive_count, count))

            # 서버가 가진 모든 데이터를 요청한 경우 break.
            if not self.StockChart.Continue:
                break

        ## 날짜와 분봉의 합치
        receive_data['Date'] = list(map(lambda x, y: int('{}{:04}'.format(x, y)), receive_data['Date'], receive_data['Time']))
        del receive_data['Time']

        ## 데이터프레임 형태로 변환
        ## 다만 호출한 데이터를 그대로 쓰게되면 날짜가 최신 -> 옛날순으로 가므로 리버스해서 역순에서 정순을 바꿔준다.
        stock_raw_data = pd.DataFrame(receive_data, columns = ['Date', 'Open', 'High', 'Low', 'Close', 'TradeVolume'])

        return stock_raw_data


## 호출한 주가 데이터를 DB 파일로 저장
class ExportDatabase:
    def __init__(self, peroid):
        self.CpCodeMgr = win32com.client.Dispatch("CpUtil.CpCodeMgr")
        self.peroid = peroid

    ## 데이터 수신하여 DB파일에 저장
    def MakeDatabase(self):

        ## 분봉 데이터 저장(분단위 별로 나누어 저장)
        kospi = self.CpCodeMgr.GetstockListByMarket(1) # 코스피
        kosdaq = self.CpCodeMgr.GetstockListByMarket(2) # 코스닥
        code_list = ['A233740','A229200','A251340']

        ## 분봉 데이터 저장(분단위 별로 나누어 저장)
        if type(self.peroid) is int:
            print('%s분봉 데이터 수집' %self.peroid)
            con = sqlite3.connect('stock_data_%sminute.db' %self.peroid)

            for i in range(len(code_list)):
                stockchart = StockChart(code_list[i])
                stock_raw_data = stockchart.call_stock_data_minute_tick(self.peroid)
                stock_raw_data.to_sql(str(code_list[i]), con, if_exists='replace')
                print("[%s / %s] %s 수집 완료" %(i+1, len(code_list), code_list[i]))
                i += 1

        else:
            con = sqlite3.connect('stock_data_%s.db' %self.peroid)
            for i in range(len(code_list)):
                stockchart = StockChart(code_list[i])
                stock_raw_data = stockchart.call_stock_data_minute_tick(self.peroid)
                stock_raw_data.to_sql(str(code_list[i]), con, if_exists='replace')
                print("[%s / %s] %s 수집 완료" %(i+1, len(code_list), code_list[i]))
                i += 1            


if __name__ == '__main__':

    ## 데이터베이스 제작 시간간격
    calender_peroid = ['day', 'month', 'year']
    ## time_peroid = [1, 3, 5, 10, 30, 60, 180]
    time_peroid = [10]
    ## 분봉 데이터베이스 제작
    for i in range(len(time_peroid)):
        MakeDataBase = ExportDatabase(time_peroid[i])
        MakeDataBase.MakeDatabase()

