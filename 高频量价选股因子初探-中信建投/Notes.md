# 20200709-中信建投-因子深度研究系列：高频量价选股因子初探
来源: https://bigquant.com/wiki/doc/20200709-gYLf5LSvmq
(oir因子类似voi，mpb因子未写)
### voi因子(订单簿失衡)：
```
def voi(data0):
    """
        衡量订单失衡
    :param data0:level1数据
    :return:
    """
    # 创建copy，确保不修改原数据
    data = data0.copy()
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
    return tick_fac_data
```
研报中还提到了
"传统VOI计算只考虑了第一档的盘口数据，这将遗漏掉很多有价值的信息，为充分利用盘口数据信息，我们对VOI因子进行了改进,即利用衰减加权的方法对委托量加权"。不过拿jm数据回测后发现加权后的Volume反而ic值降低了很多。不确定是否是股票与期货之间的差异造成的


高频因子转低频：需要对各股票进行截面标准化以剔除市场对个股的影响
![1713569761742](https://github.com/Marcotong21/Quant/assets/125079176/f38e1d19-4af3-45d4-af15-e7799fd1ae9a)

VOI、OIR因子在高频中都与未来收益率呈现正相关，然而降到低频因子则表现为负，可能原因：

VOI因子为量相关的因子，而量的信息在高频结构上会出现欺骗性的现象。1.从散户来看，在短期内散户容易存在追高杀跌行为。短期追高，价格上涨，但随着时间的累积，价格会逐渐处于高位，长期来看价格会回落。
2.从主力的角度，主力对市场的短时操纵造成了价格的涨跌。强的买卖压力一般是大单交易造成的，大单交易很可能是主力的“对倒”行为，其目的主要是吸引散户，此时高频因子与收益率呈正相关。但从长期来看，市场价格则会回落，因此造成了低频上因子与收益率呈反向关系。

（这似乎也解释了开源证券W式切割得出的结论）
