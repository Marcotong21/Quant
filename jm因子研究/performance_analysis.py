import pandas as pd
import matplotlib.pyplot as plt
from statsmodels.graphics.tsaplots import plot_acf
import os
import numpy as np
from multiprocessing import Pool

def future_y(data0, factor_index, n):
    """
        计算未来n=10个tick的收益率
    :param data0: 原始数据
    :param factor_index: 因子计算的index范围，y也要与其一致
    :param n: n=10个tick
    :return: y的Series
    """
    data = data0.copy()
    data['BidPrice1'] = data['BidPrice1'].fillna(method='bfill')
    data['AskPrice1'] = data['AskPrice1'].fillna(method='bfill')
    midprice = (data['BidPrice1'] + data['AskPrice1'])/2
    # 未来n(n=10)个tick的价格
    future_midprice = midprice.shift(-n)
    # 计算未来10个tick内涨跌幅
    y = future_midprice/midprice - 1
    y = y.loc[factor_index]
    return y


def IC_and_corr(factor_values):
    """
        计算各个因子的IC值
    :param factor_values: 包含了各个因子值与y值的dataframe
    :return:输出每个因子的IC值，以及因子的自相关系数的txt到result中
    """
    # 计算整个DataFrame的相关性矩阵
    correlation_matrix = factor_values.corr()
    # 提取与'y'列相关的相关系数（删除'y'与自身），就是IC值
    ic_values = correlation_matrix['y'].drop('y')
    # 删除相关性矩阵中的'y'列和'y'行后，得到因子间的自相关矩阵
    factor_correlation_matrix = correlation_matrix.drop('y', axis=0).drop('y', axis=1)

    # 输出结果到result文件夹
    ic_path = os.path.join('result', 'IC_values.txt')
    with open(ic_path, 'w') as file:
        ic_values.to_string(file)
    corr_matrix_path = os.path.join('result', 'Correlation_matrix.txt')
    with open(corr_matrix_path, 'w') as file:
        factor_correlation_matrix.to_string(file)
    return


def quantile(data):
    """
        计算每个因子头部1% quantile以及尾部1% quantile样本点对应的y的均值
    :param data: 也就是factor_values，同上面的函数
    :return: 输出txt结果到result中
    """
    # 存储结果的DataFrame
    results = pd.DataFrame(columns=['Factor', 'Top 1% Mean y', 'Bottom 1% Mean y'])
    # 获取除了'y'外的所有列
    factor_columns = data.columns.difference(['y'])
    for factor in factor_columns:
        # 计算1%和99%分位数
        q_low = data[factor].quantile(0.01)
        q_high = data[factor].quantile(0.99)
        # 筛选出对应于这两个分位数的'y'值
        top_1_percent_y = data[data[factor] >= q_high]['y']
        bottom_1_percent_y = data[data[factor] <= q_low]['y']
        # 计算均值
        top_mean = top_1_percent_y.mean()
        bottom_mean = bottom_1_percent_y.mean()

        results = results.append({'Factor': factor,
                                  'Top 1% Mean y': top_mean,
                                  'Bottom 1% Mean y': bottom_mean},
                                 ignore_index=True)
    # 输出结果到result文件夹
    quantile_path = os.path.join('result', 'quantile均值.txt')
    with open(quantile_path, 'w') as file:
        results.to_string(file)



def output(data):
    """
        单因子自相关和统计分布分析，图表输出在result文件夹中
    :param data: 也就是factor_values，同上面的函数
    :return: 输出图表到result中
    """
    # 获取除了 'y' 外的所有列
    factor_columns = data.columns.difference(['y'])

    for factor in factor_columns:
        # 为每个因子创建一个文件夹
        factor_dir = os.path.join('result', factor)
        if not os.path.exists(factor_dir):
            os.makedirs(factor_dir)
        #绘制ACF
        fig, ax = plt.subplots(figsize=(10, 4))
        plot_acf(data[factor].iloc[:150000], ax=ax, lags=20, title=f'Autocorrelation for {factor}')
        acf_path = os.path.join(factor_dir, f'{factor}-ACF.png')
        plt.savefig(acf_path)
        plt.close(fig)

        # 计算直方图的bins和counts
        counts, bin_edges = np.histogram(data[factor], bins=20, density=True)
        bin_centers = 0.5 * (bin_edges[1:] + bin_edges[:-1])

        # 绘制直方图的折线图并保存
        plt.figure(figsize=(10, 6))
        plt.plot(bin_centers, counts, linestyle='-', marker='o', color='b')
        plt.title(f'Probability Density Function - {factor}')
        plt.xlabel('Factor Value')
        plt.ylabel('Density')
        plt.grid(True)
        distribution_path = os.path.join(factor_dir, f'{factor}-统计分布.png')
        plt.savefig(distribution_path)
        plt.close()


    return


def orthogonal(factor1, factor2):
    """
        以factor2作为参照，对factor1正交化。返回正交化后的factor1
    :param factor1: 需要正交化的因子
    :param factor2: 参照因子
    :return:
    """
    # 计算参照因子的均值和方差
    mean_factor2 = np.mean(factor2)
    var_factor2 = np.var(factor2)
    # 计算因子1与参照因子的协方差
    cov_factor1_factor2 = np.cov(factor1, factor2)[0, 1]
    # 计算正交化后的因子1
    orthogonal_factor1 = factor1 - (cov_factor1_factor2 / var_factor2) * factor2
    return orthogonal_factor1




