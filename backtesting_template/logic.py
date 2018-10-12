## 백테스팅용 로직 설정
## logic 함수를 수정하시기 바랍니다.


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

    if (
        stock_data.at[yesterday, "Open"] < stock_data.at[today, "Open"]
    ):
        return 1

    else:
        return 0
