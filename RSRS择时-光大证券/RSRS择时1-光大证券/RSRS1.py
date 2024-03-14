#复现光大证券的RSRS策略
import pandas as pd
import numpy as np
import statsmodels.api as sm
import scipy.stats as st
import matplotlib.pyplot as plt
import tushare as ts
import akshare as ak
import os


#data = ak.stock_zh_index_daily(symbol = "sh000300")
#data.to_csv('mydata.csv', index=False)
data = pd.read_csv('mydata.csv')
df = data.copy()

#计算MA(20)，用于后面的量价数据优化
def MA20():
    global MA_list
    MA_list = [np.nan] * 20
    for k in range(len(df) - 20):
        MA = df['close'][k : k + 20].mean()
        MA_list.append(MA)
    df['MA'] = MA_list
MA20()




def cal_RSRS(df, N):        #计算RSRS斜率
    global k_list
    global R2_list
    k_list = [np.nan] * N 
    R2_list = [np.nan] * N
    for row in  range(len(df) - N):
        y = df['high'][row:row + N]
        x = df['low'][row:row + N]
        k, res = np.polyfit(x, y ,1)
        predicted_y = k * x + res
        residuals = y - predicted_y
        ssr = np.sum(residuals**2)  
        sst = np.sum((y - np.mean(y))**2)
        R2 = 1 - (ssr / sst)   #计算回归的R2值，用于修正标准分的计算
        R2_list.append(R2)
        k_list.append(k)
    df['RSRS'] = k_list
    return df

RSRS_df = cal_RSRS(df, 18)

def cal_RSRS_score(df, N, M):   #计算RSRS标准分, M为算分数的时间窗口
    df['RSRS_1'] = df['RSRS'].fillna(0)
    score = (df['RSRS_1']-df['RSRS_1'].rolling(M).mean())/df['RSRS_1'].rolling(M).std()
    df['RSRS_score'] = score
    df = df.drop(columns = 'RSRS_1')
    return df

RSRS_Z = cal_RSRS_score(RSRS_df, 18, 600)

RSRS_right = cal_RSRS_score(RSRS_df, 16, 300)   #根据研报，此时的N和M取值有所变化

portfolio_RSRS = pd.DataFrame({'value':[0] * RSRS_Z.shape[0]})
portfolio_z = pd.DataFrame({'value':[0] * RSRS_Z.shape[0]})
portfolio_z_MA = pd.DataFrame({'value':[0] * RSRS_Z.shape[0]})
portfolio_xiuzheng = pd.DataFrame({'value':[0] * RSRS_Z.shape[0]})
portfolio_xiuzheng_MA = pd.DataFrame({'value':[0] * RSRS_Z.shape[0]})
portfolio_right = pd.DataFrame({'value':[0] * RSRS_Z.shape[0]})
portfolio_right_MA = pd.DataFrame({'value':[0] * RSRS_Z.shape[0]})

def RSRS_strategy(): #斜率策略
    cash = 100000
    stocks = 0
    mean_value = RSRS_df['RSRS'].mean()
    std_value = RSRS_df['RSRS'].std()
    for k in range(len(RSRS_Z)):
        if RSRS_df['RSRS'][k] > mean_value + std_value:
            stocks += cash // df['close'][k]
            cash = cash % df['close'][k]
        elif RSRS_df['RSRS'][k] < mean_value - std_value:
            if stocks > 0:
                cash += stocks * df['close'][k]
                stocks = 0
        portfolio_RSRS['value'][k] = cash + stocks * df['close'][k]

def RSRS_zscore_strategy(): #标准分
    cash = 100000
    stocks = 0
    for k in range(len(RSRS_Z)):
        if RSRS_Z['RSRS_score'][k] > 0.7: 
            if cash > 0:
                stocks += cash // RSRS_Z['close'][k]
                cash = cash % RSRS_Z['close'][k]
        elif RSRS_Z['RSRS_score'][k] < -0.7:
            if stocks > 0:
                cash += stocks * RSRS_Z['close'][k]
                stocks = 0
        portfolio_z['value'][k] = cash + stocks * RSRS_Z['close'][k]  

def RSRS_zscore_strategy_MA(): #加入MA优化的标准分
    cash = 100000
    stocks = 0
    for k in range(len(RSRS_Z)):
        if RSRS_Z['RSRS_score'][k] > 0.7: 
            if cash > 0 and MA_list[k-1] > MA_list[k-3]:
                stocks += cash // RSRS_Z['close'][k]
                cash = cash % RSRS_Z['close'][k]
        elif RSRS_Z['RSRS_score'][k] < -0.7:
            if stocks > 0:
                cash += stocks * RSRS_Z['close'][k]
                stocks = 0
        portfolio_z_MA['value'][k] = cash + stocks * RSRS_Z['close'][k]  

def RSRS_xiuzheng(): #修正标准分
    cash = 100000
    stocks = 0
    for k in range(len(RSRS_Z)):
        if RSRS_Z['RSRS_score'][k] * R2_list[k] > 0.7:
            if cash > 0:
                stocks += cash // RSRS_Z['close'][k]
                cash = cash % RSRS_Z['close'][k]
        elif RSRS_Z['RSRS_score'][k] * R2_list[k]< -0.7:
            if stocks > 0:
                cash += stocks * RSRS_Z['close'][k]
                stocks = 0
        portfolio_xiuzheng['value'][k] = cash + stocks * RSRS_Z['close'][k]  

def RSRS_xiuzheng_MA():  #加入MA优化的修正标准分
    cash = 100000
    stocks = 0
    for k in range(len(RSRS_Z)):
        if RSRS_Z['RSRS_score'][k] * R2_list[k] > 0.7:
            if cash > 0 and MA_list[k-1] > MA_list[k-3]:
                stocks += cash // RSRS_Z['close'][k]
                cash = cash % RSRS_Z['close'][k]
        elif RSRS_Z['RSRS_score'][k] * R2_list[k]< -0.7:
            if stocks > 0:
                cash += stocks * RSRS_Z['close'][k]
                stocks = 0
        portfolio_xiuzheng_MA['value'][k] = cash + stocks * RSRS_Z['close'][k]

def RSRS_right_strategy(): #右偏标准分
    cash = 100000
    stocks = 0
    for k in range(len(RSRS_right)):
        if RSRS_right['RSRS_score'][k] * R2_list[k] * k_list[k] > 0.7:
            if cash > 0:
                stocks += cash // RSRS_right['close'][k]
                cash = cash % RSRS_right['close'][k]
        elif RSRS_right['RSRS_score'][k] * R2_list[k] * k_list[k] < -0.7:
            if stocks > 0:
                cash += stocks * RSRS_right['close'][k]
                stocks = 0
        portfolio_right['value'][k] = cash + stocks * RSRS_right['close'][k]  

def RSRS_right_strategy_MA(): #加入MA优化的右偏标准分
    cash = 100000
    stocks = 0
    for k in range(len(RSRS_right)):
        if RSRS_right['RSRS_score'][k] * R2_list[k] * k_list[k] > 0.7:
            if cash > 0 and MA_list[k-1] > MA_list[k-3]:
                stocks += cash // RSRS_right['close'][k]
                cash = cash % RSRS_right['close'][k]
        elif RSRS_right['RSRS_score'][k] * R2_list[k] * k_list[k] < -0.7:
            if stocks > 0:
                cash += stocks * RSRS_right['close'][k]
                stocks = 0
        portfolio_right_MA['value'][k] = cash + stocks * RSRS_right['close'][k]  

#RSRS_zscore_strategy_MA()
#RSRS_zscore_strategy()
#RSRS_xiuzheng()
#RSRS_xiuzheng_MA()
RSRS_right_strategy()
RSRS_right_strategy_MA()
n = 100000 // data['close'][0]
r = 100000 % data['close'][0]
#plt.plot(df['date'], portfolio_RSRS['value'], color='red', label='RSRS')

#plt.plot(df['date'], portfolio_z['value'], color='blue', label='RSRS z-score')
#plt.plot(df['date'], portfolio_z_MA['value'], color='red', label='RSRS_z_MA')

#plt.plot(df['date'], portfolio_xiuzheng['value'], color='blue', label='RSRS_xiuzheng')
#plt.plot(df['date'], portfolio_xiuzheng_MA['value'], color='red', label='RSRS_xiuzheng_MA')

plt.plot(df['date'], portfolio_right['value'], color='blue', label='RSRS-right score')
plt.plot(df['date'], portfolio_right_MA['value'], color='red', label='RSRS-right score_MA')

plt.plot(df['date'], data['close'] * n + r, color='green', label='HuShen300')
plt.legend()
plt.show()

