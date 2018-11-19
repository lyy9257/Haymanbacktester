'''
전략 성과 사용자에게 표시
'''

import trade_simulation
import config

import time 
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from datetime import datetime


class show_result():

    def __init__(self):
        call_raw_data_from_database = trade_simulation.call_raw_data()
        stock_raw_data = call_raw_data_from_database.call_stock_raw_data()

        run_buy_and_hold = trade_simulation.run_simulation_buy_and_hold(stock_raw_data)
        run_strategy = trade_simulation.run_simulation_strategy(stock_raw_data)
    
        self.index_trade_data = run_buy_and_hold.make_index_trade_data()
        self.strategy_trade_data = run_strategy.make_strategy_account_data()


    ## 주요 성과지표 출력
    def show_strategy_result(self):
        
        ## 백테스트 시작, 종료일자 출력
        start_date = str(self.strategy_trade_data.at[0, 'Date'])
        end_date = str(self.strategy_trade_data.at[len(self.strategy_trade_data.index) - 1, 'Date'])

        ## 주요 성과지표 계산
        total_return = self.strategy_trade_data.at[len(self.strategy_trade_data.index) - 1, 'account_strategy'] / self.strategy_trade_data.at[0, 'account_strategy']
        ## profit_day = round(((total_return)**(1/int(len(self.strategy_trade_data.index)/9)) - 1), 4) * 100 -> 구현 중
        max_draw_down = round(abs(pd.Series.min(self.strategy_trade_data["max_draw_down"])) * 100, 2)

        ## 성과지표 출력
        print('Strategy : %s' %config.strategy_name)
        print('start : %s-%s-%s' %(start_date[:4], start_date[4:6],start_date[6:8]))
        print('end   : %s-%s-%s' %(end_date[:4], end_date[4:6], end_date[6:8]))
        print('----------------------')
        print('Total Return : %.2f %%' %(total_return * 100 - 100))
        ## print('Earn Per Day  : %.2f %%' %profit_day) -> 구현 중
        print('MDD   : %.2f %%' %max_draw_down)


    ## 그래프 출력
    def show_asset_growth_graph(self):

        fig = plt.figure(figsize=(16, 9))

        top_axes = plt.subplot2grid((4,4), (0,0), rowspan=3, colspan=4)
        bottom_axes = plt.subplot2grid((4,4), (3,0), rowspan=1, colspan=4)

        ## 단순 바이앤 홀딩 및 전략 수익률 출력
        top_axes.plot(self.strategy_trade_data.index, self.strategy_trade_data['account_strategy'], label='Strategy')
        top_axes.plot(self.strategy_trade_data.index, self.index_trade_data['account_buy_and_hold'], label='Buy and Hold')

        bottom_axes.plot(self.strategy_trade_data.index, self.strategy_trade_data["daily_drawdown"], label="daily_drawdown")
        bottom_axes.plot(self.strategy_trade_data.index, self.strategy_trade_data["max_draw_down"], label="max_draw_down")

        top_axes.legend(loc='best')

        plt.savefig("./graph.png", dpi=240)       
        plt.title('Asset Growth, Max Draw Down Graph')
        plt.tight_layout()
        plt.show()
        plt.close(fig)

if __name__ == "__main__":

    ## 시작 시간
    backtesting_start = time.time()

    ## 결과 출력
    show_result_strategy = show_result()
    show_result_strategy.show_strategy_result()
    ellapsed = time.time() - backtesting_start

    ## 백테스팅 소요 시간 측정
    print("소요 시간 : %.2f sec" %ellapsed)
    show_result_strategy.show_asset_growth_graph()





