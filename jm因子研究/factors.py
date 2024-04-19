import pandas as pd
import numpy as np


def midpriceRtn(data0, order, factor_index):
    """
        范例因子A
    :param data0:完整的、未剔除过的数据。考虑因子计算可能需要滑动时间窗，因此还是需要将完整的数据传入
    :param order:最优价前十笔委托，不过本因子未使用
    :param factor_index: 因子计算的index范围（也就是剔除最开始和最后15秒之后的index）
    :return: mid_price return因子值
    """
    # 创建copy，确保不修改原数据
    data = data0.copy()

    # 因子值
    midprice = (data['BidPrice1'] + data['AskPrice1'])/2
    midprice_return = midprice.diff()
    midprice_return = midprice_return.loc[factor_index]
    return midprice_return


# 范例因子B
def orderImbalance(data0, order, factor_index):
    """
        范例因子B
    :param data0:同因子A
    :param order:最优价前十笔委托，不过本因子未使用
    :param factor_index: 同因子A
    :return: orderbook imbalance因子值
    """
    # 创建copy，确保不修改原数据
    data = data0.copy()
    # 因子值
    imbalance =  np.log(data['BidVolume1']/data['AskVolume1'])
    imbalance = imbalance.loc[factor_index]
    return imbalance


# 因子C
def pricejump(data0, order, factor_index):
    """
        计算当前midprice与过去时间窗口(如20个tick)之内的midprice的最大值的差异，
        再进行EMA与shift。
    :param data0:同因子A
    :param order:最优价前十笔委托，不过本因子未使用
    :param factor_index:同因子A
    :return: pricejump因子值
    """
    # 创建copy，确保不修改原数据
    data = data0.copy()

    midprice = (data['BidPrice1'] + data['AskPrice1']) / 2
    data['pricejump'] = midprice - midprice.rolling(window=15).max()
    # 计算EMA
    data['Price Jump EMA'] = data['pricejump'].ewm(span=10).mean()
    data['Price Jump EMA shift'] = data['Price Jump EMA'].shift(1)
    result = data['Price Jump EMA shift'].loc[factor_index]
    return result

    # 上面这个因子在单日的表现已经足够优秀，有些日期能达到0.09，但是回测所有时间段的话ic就降到了0.01
    # 于是尝试用移动平均来平滑因子，以增加因子的稳定性
    # 1.一开始尝试做了一个n=5移动平均的平滑，IC能到0.3以上，相关性也很低，但quantile的头尾差异不明显；
    # 2.改为span=10的EMA，IC能到0.3以上，quantile的差异相对显著，不过相关性有所增加（和midpiceRtn有0.58），
    #   应该是EMA在上一个tick的权重较大造成的 （或许可以正交化试试？）
    # 3.改为span=15的EMA再进行shift(1)，也就是用上一个tick的因子值作为这个tick的因子值，这样就不使用当前tick的数据，可以降低corr。
    #   事实确实如此，IC上升到了0.41，corr非常低（几乎和midpiceRtn正交），quantile表现也还不错


def max_portion(data0, order, factor_index):
    """
        计算最优价前十笔委中最大的一单占总quantity的比重，得到Bid Max Order Proportion以及Ask Max Order Proportion
        然后再log(Bid/Ask)
        注：此因子后续还有正交化的版本，详见报告
    :param data0:同因子A
    :param order:最优价前十笔委托
    :param factor_index:同因子A
    :return: max_portion因子值
    """
    # 创建copy，确保不修改原数据
    data = data0.copy()
    df = order.copy()
    # 最大单占比
    df['Bid Max Order Proportion'] = df.filter(like='BidOrderQty').max(axis=1) / df.filter(like='BidOrderQty').sum(
        axis=1)
    df['Ask Max Order Proportion'] = df.filter(like='AskOrderQty').max(axis=1) / df.filter(like='AskOrderQty').sum(
        axis=1)
    df['max portion'] = np.log(df['Bid Max Order Proportion']/df['Ask Max Order Proportion'])
    data['max portion'] = df['max portion']
    # order中有些tick在data中没有，因此这些tick没有因子值；向前填充补全因子值
    data['max portion'] = data['max portion'].fillna(method='ffill')
    return data['max portion'].loc[factor_index]


def voi(data0, order, factor_index):
    """
        中信建投-因子深度研究系列：高频量价选股因子初探
        衡量订单失衡
    :param data0:同因子A
    :param order:最优价前十笔委托，本因子未使用
    :param factor_index:同因子A
    :return:
    """
    # 创建copy，确保不修改原数据
    data = data0.copy()

    # # 对Volume加权
    # weights = [1 - (i - 1) / 5 for i in range(1, 6)]
    # data['VWB_t'] = sum(data[f'BidVolume{i}'] * weight for i, weight in enumerate(weights, start=1)) / sum(weights)
    # data['VWA_t'] = sum(data[f'AskVolume{i}'] * weight for i, weight in enumerate(weights, start=1)) / sum(weights)

    # BidPrice1、AskPrice1、BidVolume1、AskVolume1的diff
    bid_sub_price = data['BidPrice1'] - data['BidPrice1'].shift(1)
    ask_sub_price = data['AskPrice1'] - data['AskPrice1'].shift(1)
    bid_sub_volume = data['BidVolume1'] - data['BidVolume1'].shift(1) # data['VWB_t'] - data['VWB_t'].shift(1)
    ask_sub_volume = data['AskVolume1'] - data['AskVolume1'].shift(1) # data['VWA_t'] - data['VWA_t'].shift(1)
    bid_volume_change = bid_sub_volume
    ask_volume_change = ask_sub_volume
    # 对于bid_sub_volume的变化量，如果bid_sub_price上升，则不变；如果bid_sub_price下降或保持不变，则将其设为0。
    # ask_sub_volume同理
    bid_volume_change[bid_sub_price < 0] = 0
    bid_volume_change[bid_sub_price > 0] = data['BidVolume1'][bid_sub_price > 0]
    ask_volume_change[ask_sub_price < 0] = data['AskVolume1'][ask_sub_price < 0]
    ask_volume_change[ask_sub_price > 0] = 0
    tick_fac_data = (bid_volume_change - ask_volume_change) / data['Volume']
    return tick_fac_data.loc[factor_index]

def z(data0, order, factor_index):
    """
        市价偏离度因子，来源20130904-民生证券-指令单薄与指令单流——资金交易策略之四
        计算方法:log（Midprice - LastPrice）
    :param data0:同因子A
    :param order:最优价前十笔委托，本因子未使用
    :param factor_index:同因子A
    :return:z因子值
    """
    data = data0.copy()
    tick_fac_data =  np.log((data['BidPrice1'] + data['AskPrice1']) / 2) - np.log(data['LastPrice'])
    return tick_fac_data.loc[factor_index]


def test_factor123(data0, order, factor_index):
    # 创建copy，确保不修改原数据
    data = data0.copy()
    df = order.copy()

    # # 最大单位置
    # df['Bid Max Order Position'] = df.filter(like='BidOrderQty').idxmax(axis=1).str.replace('BidOrderQty', '').astype(
    #     int)
    # df['Ask Max Order Position'] = df.filter(like='AskOrderQty').idxmax(axis=1).str.replace('AskOrderQty', '').astype(
    #     int)

    # bid_columns = [col for col in df.columns if col.startswith('BidOrderQty')]
    # ask_columns = [col for col in df.columns if col.startswith('AskOrderQty')]
    # bid_positions = [int(col.replace('BidOrderQty', '')) for col in bid_columns]
    # ask_positions = [int(col.replace('AskOrderQty', '')) for col in ask_columns]
    # bid_weighted_avg_position = (df[bid_columns].multiply(bid_positions, axis=1)).sum(axis=1) \
    #                             / df[bid_columns].sum(axis=1)
    # ask_weighted_avg_position = (df[ask_columns].multiply(ask_positions, axis=1)).sum(axis=1) \
    #                             / df[ask_columns].sum(axis=1)
    # df['max portion'] = np.log(bid_weighted_avg_position/ask_weighted_avg_position)
    data['test'] = (data['AskPrice1'] - data['BidPrice1'])*(data['BidVolume1'] + data['AskVolume1']) \
                   / (data['BidVolume1'] + data['AskVolume1']).max()
    return data['test'].loc[factor_index]
