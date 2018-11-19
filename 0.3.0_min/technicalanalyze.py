'''
기술적 분석 라이브러리
'''

import pandas as pd  
import math as m
import numpy as np

#Moving Average  
def MA(df, day):  
    MA = pd.Series(df.rolling(day).mean(), name = 'MA_' + str(day))  
    return MA


#Exponential Moving Average  
def EMA(df, day):  
    EMA = pd.Series(df.ewm(df['Close'], span = day, min_periods = day - 1).mean(), name = 'EMA_' + str(day))  
    return EMA


#Momentum  
def Momentum(df, day):  
    Momentum = pd.Series(df['Close'].diff(day), name = 'Momentum_' + str(day))  
    return Momentum


#Average True Range  
def ATR(df, day):  
    i = 0  
    TR_l = [0]  
    while i < df.index[-1]:  
        TR = max(df.at(i + 1, 'High'), df.at(i, 'Close')) - min(df.at(i + 1, 'Low'), df.at(i, 'Close'))  
        TR_l.append(TR)  
        i = i + 1  
    TR_s = pd.Series(TR_l)  
    ATR = pd.Series(pd.DataFrame.ewm(TR_s, span = day, min_periods = day).mean(), name = 'ATR_' + str(day))  
       
    return ATR


#Bollinger Bands  
def BBANDS(df, n):  
    MA = pd.Series(df['Close'].rolling(n).mean())  
    MSD = pd.Series(df['Close'].rolling(n).std())  
    b1 = 4 * MSD / MA  
    B1 = pd.Series(b1, name = 'BollingerB_' + str(n))  
    df = df.join(B1)  
    b2 = (df['Close'] - MA + 2 * MSD) / (4 * MSD)  
    B2 = pd.Series(b2, name = 'Bollinger%b_' + str(n))  
    df = df.join(B2)  
    return df


#Stochastic oscillator %K  
def STOK(df):  
    SOk = pd.Series((df['Close'] - df['Low']) / (df['High'] - df['Low']), name = 'SO%k')  
    return SOk


# Stochastic Oscillator, EMA smoothing, nS = slowing (1 if no slowing)  
def STO_EMA(df,  nK, nD, nS=1):  
    SOk = pd.Series((df['Close'] - df['Low'].rolling(nK).min()) / (df['High'].rolling(nK).max() - df['Low'].rolling(nK).min()), name = 'SO%k'+str(nK))  
    SOd = pd.Series(SOk.ewm(ignore_na=False, span=nD, min_periods=nD-1, adjust=True).mean(), name = 'SO%d'+str(nD))  
    SOk = SOk.ewm(ignore_na=False, span=nS, min_periods=nS-1, adjust=True).mean()  
    SOd = SOd.ewm(ignore_na=False, span=nS, min_periods=nS-1, adjust=True).mean()  
    df = df.join(SOk)  
    df = df.join(SOd)  
    return df  


# Stochastic Oscillator, SMA smoothing, nS = slowing (1 if no slowing)  
def STO_SMA(df, nK, nD,  nS=1):  
    SOk = pd.Series((df['Close'] - df['Low'].rolling(nK).min()) / (df['High'].rolling(nK).max() - df['Low'].rolling(nK).min()), name = 'SO%k'+str(nK))  
    SOd = pd.Series(SOk.rolling(window=nD, center=False).mean(), name = 'SO%d'+str(nD))  
    SOk = SOk.rolling(window=nS, center=False).mean()  
    SOd = SOd.rolling(window=nS, center=False).mean()  
    df = df.join(SOk)  
    df = df.join(SOd)  
    return df  


#MACD, MACD Signal and MACD difference  
def MACD(df, n_fast, n_slow):  
    EMAfast = pd.Series(pd.DataFrame.ewma(df['Close'], span = n_fast, min_periods = n_slow - 1))  
    EMAslow = pd.Series(pd.DataFrame.ewma(df['Close'], span = n_slow, min_periods = n_slow - 1))  
    MACD = pd.Series(EMAfast - EMAslow, name = 'MACD_' + str(n_fast) + '_' + str(n_slow))  
    MACDsign = pd.Series(pd.DataFrame.ewma(MACD, span = 9, min_periods = 8), name = 'MACDsign_' + str(n_fast) + '_' + str(n_slow))  
    MACDdiff = pd.Series(MACD - MACDsign, name = 'MACDdiff_' + str(n_fast) + '_' + str(n_slow))  
    df = df.join(MACD)  
    df = df.join(MACDsign)  
    df = df.join(MACDdiff)  
    return df


#Relative Strength Index  
def RSI(df, day):
    U = np.where(df.diff(1) > 0, df.diff(1), 0)
    D = np.where(df.diff(1) < 0, df.diff(1) *(-1), 0)

    AU = pd.DataFrame(U).rolling(window=day, min_periods=day).mean()
    AD = pd.DataFrame(D).rolling(window=day, min_periods=day).mean()
    RSI = AU.div(AD+AU) * 100

    print(RSI)

    return RSI


#True Strength Index  
def TSI(df, r, s):  
    M = pd.Series(df.diff(1))  
    aM = abs(M)  
    EMA1 = pd.Series(pd.DataFrame.ewm(M, span = r, min_periods = r - 1).mean())  
    aEMA1 = pd.Series(pd.DataFrame.ewm(aM, span = r, min_periods = r - 1).mean())  
    EMA2 = pd.Series(pd.DataFrame.ewm(EMA1, span = s, min_periods = s - 1).mean())  
    aEMA2 = pd.Series(pd.DataFrame.ewm(aEMA1, span = s, min_periods = s - 1).mean())  
    TSI = pd.Series(EMA2 / aEMA2, name = 'TSI_' + str(r) + '_' + str(s))  

    return TSI


#Accumulation/Distribution  
def ACCDIST(df, n):  
    ad = (2 * df['Close'] - df['High'] - df['Low']) / (df['High'] - df['Low']) * df['TradeVolume']  
    M = ad.diff(n - 1)  
    N = ad.shift(n - 1)  
    ROC = M / N  
    AD = pd.Series(ROC, name = 'Acc/Dist_ROC_' + str(n))  

    return AD


#Chaikin Oscillator  
def Chaikin(df):  
    ad = (2 * df['Close'] - df['High'] - df['Low']) / (df['High'] - df['Low']) * df['TradeVolume']  
    Chaikin = pd.Series(pd.DataFrame.ewm(ad, span = 3, min_periods = 2).mean() - pd.DataFrame.ewm(ad, span = 10, min_periods = 9).mean(), name = 'Chaikin').mean()  

    return Chaikin


#Money Flow Index and Ratio  
def MFI(df, n):
    """Calculate Money Flow Index and Ratio for given data.
    
    :param df: pandas.DataFrame
    :param n: 
    :return: pandas.DataFrame
    """
    PP = (df['High'] + df['Low'] + df['Close']) / 3
    i = 0
    PosMF = [0]
    while i < len(df.index) - 1:
        if PP[i + 1] > PP[i]:
            PosMF.append(PP[i + 1] * df.loc[i + 1, 'TradeVolume'])
        else:
            PosMF.append(0)
        i = i + 1
    PosMF = pd.Series(PosMF)
    TotMF = PP * df['TradeVolume']
    MFR = pd.Series(PosMF / TotMF)
    MFI = pd.Series(MFR.rolling(n, min_periods=n).mean(), name='MFI_' + str(n))

    return MFI


#On-balance TradeVolume  
def OBV(df, n):  
    i = 0  
    OBV = [0]  
    while i < df.index[-1]:  
        if df.at(i + 1, 'Close') - df.at(i, 'Close') > 0:  
            OBV.append(df.at(i + 1, 'TradeVolume'))  
        if df.at(i + 1, 'Close') - df.at(i, 'Close') == 0:  
            OBV.append(0)  
        if df.at(i + 1, 'Close') - df.at(i, 'Close') < 0:  
            OBV.append(-df.at(i + 1, 'TradeVolume'))  
        i = i + 1  
    OBV = pd.Series(OBV)  
    OBV_ma = pd.Series(pd.rolling(OBV, n).mean(), name = 'OBV_' + str(n))  

    return OBV_ma


#Force Index  
def FORCE(df, n):  
    F = pd.Series(df['Close'].diff(n) * df['TradeVolume'].diff(n), name = 'Force_' + str(n))  
    
    return F


#Ease of Movement  
def EOM(df, n):  
    EoM = (df['High'].diff(1) + df['Low'].diff(1)) * (df['High'] - df['Low']) / (2 * df['TradeVolume'])  
    Eom_ma = pd.Series(pd.rolling_mean(EoM, n), name = 'EoM_' + str(n))  
    df = df.join(Eom_ma)  
    return df


#Commodity Channel Index  
def CCI(df, n):  
    PP = (df['High'] + df['Low'] + df['Close']) / 3  
    CCI = pd.Series((PP - pd.rolling(PP, n).mean()) / pd.rolling(PP, n).std(), name = 'CCI_' + str(n))  
    
    return CCI

#Keltner Channel  
def KELCH(df, n):
    kel_m = pd.DataFrame((df['High'] + df['Low'] + df['Close']) / 3)
    kel_u = pd.DataFrame((4 * df['High'] - 2 * df['Low'] + df['Close']) / 3)
    kel_d = pd.DataFrame((-2 * df['High'] + 4 * df['Low'] + df['Close']) / 3)

    KelChM = pd.Series(kel_m.rolling(n).mean(), name = 'KelChM_' + str(n))  
    KelChU = pd.Series(kel_u.rolling(n).mean(), name = 'KelChU_' + str(n))  
    KelChD = pd.Series(kel_d.rolling(n).mean(), name = 'KelChD_' + str(n))  

    df = df.join(KelChM)  
    df = df.join(KelChU)  
    df = df.join(KelChD)  

    return df


#Donchian Channel  
def DONCH(df, n):  
    i = 0  
    DC_l = []  
    while i < n - 1:  
        DC_l.append(0)  
        i = i + 1  
    i = 0  
    while i + n - 1 < df.index[-1]:  
        DC = max(df['High'].ix[i:i + n - 1]) - min(df['Low'].ix[i:i + n - 1])  
        DC_l.append(DC)  
        i = i + 1  
    DonCh = pd.Series(DC_l, name = 'Donchian_' + str(n))  
    DonCh = DonCh.shift(n - 1)  

    df = df.join(DonCh)
    return df


def PCH(df, n):

    KelChM = pd.Series(df['Close'].rolling(n).max(), name = 'PCH_H_' + str(n))  
    KelChU = pd.Series(df['Close'].rolling(n).max(), name = 'PCH_L_' + str(n))  

    df = df.join(KelChM)  
    df = df.join(KelChU)  

    return df