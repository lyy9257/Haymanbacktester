import config
import overnight_basket
import swing_basket
import show_strategy_result

import sqlite3
import pandas as pd

## 백테스팅 유니버스 정렬
## 상장기한이 가장 짧은 종목이 맨 앞에 들어서게 됨.

def sort_backtest_universe(basket):
    con = sqlite3.connect('kospi.db')
    
    if len(basket) > 1:
        for i in range(1, len(basket)): # 리스트의 크기만큼 반복
            for j in range(0, len(basket)-1): # 각 회전당 정렬이 끝나지 않은 종목들을 위해 반복
                now_len = pd.read_sql("SELECT COUNT(*) FROM %s" %basket[j], con, index_col=None).at[0,'COUNT(*)']
                next_len = pd.read_sql("SELECT COUNT(*) FROM %s" %basket[j+1], con, index_col=None).at[0,'COUNT(*)']

                if now_len > next_len: # 현재 인덱스의 값이 다음 인덱스의 값보다 크면 실행
                   basket[j+1], basket[j] = basket[j], basket[j+1] # swap해서 위치 바꾸기
              
        return basket

    else:
        return basket


if __name__ == '__main__':

    '''
    유니버스 설정시 유의 사항
    백테스팅 기간은 맨 첫번째에 있는 종목의 상장기간으로 설정됩니다.
    '''

    ## 백테스팅 종목 호출
    etf_universe = sort_backtest_universe(config.basket_universe)
  
    ## 백테스팅 실시
    ## overnight_basket를 swing_basket로 수정해서 사용할 수 있음.
    backtesting = swing_basket.Core(etf_universe, config.optmizize_1)
    trading_data = backtesting.calculate_account_data()
    print(trading_data)

    ## 결과 출력
    show_strategy_result = show_strategy_result.show_result_strategy(trading_data)

    show_strategy_result.show_strategy_result()
    show_strategy_result.show_asset_growth_graph()

