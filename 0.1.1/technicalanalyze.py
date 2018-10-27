import pandas as pd  
import math as m
import numpy as np

#Moving Average  
def MA(df, day):  
    MA = pd.Series(df.rolling(day).mean(), name = 'MA_' + str(day))  
    return MA
