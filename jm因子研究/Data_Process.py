import pandas as pd
import os

def read_data(folder_path):
    """
        遍历文件夹下的所有csv，读取后concat在一起
    :param folder_path:
    :return: 合并后的数据
    """
    files = os.listdir(folder_path)
    dataframes = []
    # 遍历文件名列表，筛选出CSV文件，并读取
    for file in files:
        if file.endswith('.csv'):
            file_path = os.path.join(folder_path, file)
            df = pd.read_csv(file_path)
            dataframes.append(df)
    # concat合并所有DataFrame
    combined_df = pd.concat(dataframes, ignore_index=True)
    return combined_df


def clean_l2_data(l2, order):
    """
        功能：
        1.合并日期和时间，并将index设置为datetime格式
        2.drop掉无用的列，加快数据处理速度
    :param l2: level2数据
    :param order: 最优十笔委托数据
    :return: 处理后的数据
    """
    # 合并日期与具体时间，形成一个完整的日期时间字符串，并将其设置为index
    l2['ActionDay'] = l2['ActionDay'].astype(str)
    l2['DateTime'] = l2['ActionDay'] + ' ' + l2['UpdateTime']
    l2.set_index('DateTime', inplace=True)
    l2.index = pd.to_datetime(l2.index)
    # 删除不需要的列,包括合并之前的时间、推导量、历史最高价、收盘价结算价等
    l2.drop(columns=['ActionDay', 'InstruID', 'UpdateTime', 'ClosePrice', 'SetPrice',
                     'PreSetPrice', 'PreCloPrice'] ,inplace=True)
    columns_to_drop = l2.filter(regex='Der|Life').columns
    l2.drop(columns_to_drop, axis=1, inplace=True)
    # 防止多个csv在concat时打乱顺序的情况
    l2_sorted = l2.sort_index()
    # 后向填充处理nan值。实际上nan值都出现在开盘的前几个tick中，我在因子计算的index已经过滤了这些。
    # 这里只是为了计算不报错而填充了nan，不会影响实际因子值
    l2_sorted['BidVolume1'] = l2_sorted['BidVolume1'].fillna(method='bfill')
    l2_sorted['AskVolume1'] = l2_sorted['AskVolume1'].fillna(method='bfill')
    l2_sorted['BidPrice1'] = l2_sorted['BidPrice1'].fillna(method='bfill')
    l2_sorted['AskPrice1'] = l2_sorted['AskPrice1'].fillna(method='bfill')

    # 对最优十笔委托处理同上
    order['ActionDay'] = order['ActionDay'].astype(str)
    order['DateTime'] = order['ActionDay'] + ' ' + order['UpdateTime']
    order.set_index('DateTime', inplace=True)
    order.index = pd.to_datetime(order.index)
    order.drop(columns=['ActionDay', 'InstruID', 'UpdateTime'], inplace=True)
    order_sorted = order.sort_index()
    return l2_sorted, order_sorted


def factor_time_range(index, n):
    """
        过滤因子计算的index范围：例如剔除开盘的前n=15秒，收盘前的最后15秒
    :param index: 数据的index，为datetime格式
    :param n: 剔除的秒数，例如剔除开盘的n=15秒、收盘的最后15秒
    :return: 剔除过后的index，这些index可以用于计算因子
    """
    # 夜盘
    night_start = '21:00:00'
    night_end = '23:00:00'
    # 早盘1
    morning_start = '09:00:00'
    morning_end = '10:15:00'
    # 早盘2
    late_morning_start = '10:30:00'
    late_morning_end = '11:30:00'
    # 下午
    afternoon_start = '13:30:00'
    afternoon_end = '15:00:00'

    # 定义n=15秒的 timedelta 对象
    n_seconds = pd.to_timedelta(f'{n} seconds')

    # 构建过滤条件 保留满足条件的index，也就是保留：开盘15秒开始，到收盘前的15秒
    conditions_to_keep = (
            ((index.time >= (pd.to_datetime(night_start) + n_seconds).time()) &
             (index.time <= (pd.to_datetime(night_end) - n_seconds).time())) |
            ((index.time >= (pd.to_datetime(morning_start) + n_seconds).time()) &
             (index.time <= (pd.to_datetime(morning_end) - n_seconds).time())) |
            ((index.time >= (pd.to_datetime(late_morning_start) + n_seconds).time()) &
             (index.time <= (pd.to_datetime(late_morning_end) - n_seconds).time())) |
            ((index.time >= (pd.to_datetime(afternoon_start) + n_seconds).time()) &
             (index.time <= (pd.to_datetime(afternoon_end) - n_seconds).time()))
    )
    # 应用过滤条件
    index_filtered = index[conditions_to_keep]
    return index_filtered




