import pandas as pd
import os

# 导入三个py文件，分别为数据处理、因子生成、结果分析的模块
import Data_Process
import factors
import performance_analysis


######################### STEP1: 读取数据，并初步处理  ###################################

# 读取文件夹中的所有csv，并concat
l2 = Data_Process.read_data('jm2209')   # level1数据
order = Data_Process.read_data('jm2209_order')   # 最优十笔委托数据

# l2 = pd.read_csv('jm2209/20220817_jm2209.csv')  # 单日数据，用于测试
# order = pd.read_csv('jm2209_order/20220817_jm2209.csv')

# 数据处理，主要是删除不需要的columns，以及设置index
data, order = Data_Process.clean_l2_data(l2, order)
# 过滤因子计算的index范围：例如剔除开盘的前n=15秒，收盘前的最后15秒
factor_index = Data_Process.factor_time_range(data.index, n =15)  # (n可以修改)


######################### STEP2: 计算因子值 ###################################

# 因子值计算，解释详见factors.py
midprice_return = factors.midpriceRtn(data, order, factor_index)# 范例因子A
imbalance = factors.orderImbalance(data, order, factor_index)# 范例因子B
factor_voi=factors.voi(data, order, factor_index)
factor_z=factors.z(data, order, factor_index)
pricejump = factors.pricejump(data, order, factor_index)
maxportion = factors.max_portion(data, order, factor_index)

# max_portion和orderImbalance的相关性有0.52，因此考虑对该因子正交化
orthogonal_maxportion = performance_analysis.orthogonal(maxportion, imbalance)
# 计算y
y = performance_analysis.future_y(data, factor_index, n=10)

# 将因子值和y汇总到一个dataframe中，方便后续分析
factor_values = pd.DataFrame({
    'midpriceRtn': midprice_return,
    'orderImbalance': imbalance,
    'pricejump': pricejump,
    # 'max_portion':maxportion,
    'max_portion_orthogonal':orthogonal_maxportion,
    'voi':factor_voi,
    'z':factor_z,
    'y': y
})


######################### STEP3: 因子分析 ###################################


# 计算每个因子的ic值，以及因子之间的自相关系数，输出在result文件夹中
performance_analysis.IC_and_corr(factor_values)
# 因子头尾1%的对应的y均值
performance_analysis.quantile(factor_values)
# 每个因子的统计分布分析、自相关分析，输出在result/factor的文件夹中
performance_analysis.output(factor_values)


# 输出最后五天的因子值到CSV文件
sixth_last_day = factor_values.index[-1].normalize() - pd.Timedelta(days=5)
start_time = sixth_last_day + pd.Timedelta(hours=19)
last_five_days_data = factor_values.loc[factor_values.index > start_time, :]
last_five_days_data.to_csv('result/最后五天因子值.csv')




