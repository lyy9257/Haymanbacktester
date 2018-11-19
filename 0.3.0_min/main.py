import config
import trade_simulation
import show_strategy_result

import sqlite3
import pandas as pd

import time


if __name__ == '__main__':

    '''
    유니버스 설정시 유의 사항
    백테스팅 기간은 맨 첫번째에 있는 종목의 상장기간으로 설정됩니다.
    '''

    ## 시작 시간
    backtesting_start = time.time()

    ## 결과 출력
    show_result_strategy = show_strategy_result.show_result()
    show_result_strategy.show_strategy_result()
    ellapsed = time.time() - backtesting_start

    ## 백테스팅 소요 시간 측정
    print("소요 시간 : %.2f sec" %ellapsed)
    show_result_strategy.show_asset_growth_graph()



