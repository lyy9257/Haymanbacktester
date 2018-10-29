'''
백테스트 변수 설정
'''
strategy_name = 'Sample'

## 백테스팅용 종목 설정
## 원하는 종목의 코드를 입력하세요.
basket_universe = ['A233740']

trade_fee = 0.011 ## 거래 수수료
trade_tax = 0 ## 증권거래세

position_control = "liquid" ## 매매비중 조절 모드(fixed : 고정, liquid : 전략에 따른 분배)
position_size = 0.95 ## 주식 고정비중

trade_mode = 'overnight' ## 백테스팅 모드 설정

## Logic 내 변수 설정 
optmizize_1 = 5
