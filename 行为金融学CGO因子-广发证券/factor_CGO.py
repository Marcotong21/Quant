import pandas as pd
import numpy as np


def CGO(df):
    """
        计算CGO指标
    :param df:输入数据,index为日期
    :return: cgo:指标的值
    """
    # 数据预处理
    # 计算VWAP，并处理可能存在的NaN值
    df['vwap'] = df['amount'] / df['vol']
    df['vwap'].fillna(method='ffill', inplace=True)
    df['vwap'].fillna(method='bfill', inplace=True)
    # 前向填充和后向填充关闭价和换手率，以处理NaN值
    df['close'].fillna(method='ffill', inplace=True)
    df['close'].fillna(method='bfill', inplace=True)
    df['turnover_rate'].fillna(method='ffill', inplace=True)
    df['turnover_rate'].fillna(method='bfill', inplace=True)

    # 创建一个空的DataFrame rp，索引与df相同
    rp = pd.DataFrame(index=df.index, columns=['rp'])

    # 遍历DataFrame来计算rp
    for i in range(100, len(df)):
        turnover_window = df['turnover_rate'].iloc[i - 100:i].values
        vwap_window = df['vwap'].iloc[i - 100:i].values
        # 初始化权重数组
        weights = np.zeros(100)
        # 计算权重
        for j in range(100):
            product = np.prod(1 - turnover_window[j + 1:])  # 从 j+1 到末尾的累积乘积
            weights[j] = turnover_window[j] * product

        # 标准化权重
        sum_weights = weights.sum()
        if sum_weights == 0:
            continue
        normalized_weights = weights / sum_weights
        # 计算rp
        rp_value = np.dot(normalized_weights, vwap_window)
        rp.at[df.index[i], 'rp'] = rp_value

    # 替换rp中的NaN值
    rp.fillna(method='ffill', inplace=True)

    # 计算CGO值
    cgo = df['close'] / rp['rp'] - 1
    return cgo


def CGO_signal(df):
    """
        计算CGO指标，对其进行排序，并选择前10%的股票作为卖出信号，后10%作为买入信号
        （输入为一支股票数据，实现的是择时信号；未测试多股票的选股功能）
    :param df:输入数据,index为日期，columns = ['turnover_rate','close','vol','amount']
    :return: 买-1卖1的信号
    """
    cgo = CGO(df)
    # 输出cgo的结果
    # cgo.dropna().to_csv("./result/cgo计算结果.csv")
    signal = pd.Series(0, index=cgo.index, dtype=int)
    # 对CGO因子进行排序，并选择前10%的股票作为卖出信号，最小的10%买入信号
    big_threshold = cgo.quantile(0.9)  # 获取前10%的阈值
    small_threshold = cgo.quantile(0.1) # 获取后10%的阈值
    signal[cgo >= big_threshold] = 1  # 卖出信号
    signal[cgo <= small_threshold] = -1  # 买入信号
    return signal
