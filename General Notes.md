IC值(信息系数)：衡量一个因子预测能力，是因子值与未来一段时间收益之间的相关性系数。IC值的范围从-1到1，IC值接近0通常表示因子与未来收益之间没有显著的线性关系。评估IC值时，需要确定一个特定的时间框架，比如未来一个月或三个月的收益。不同的时间框架可能导致IC值的不同。

待整理内容

**OBV 能量潮**：<br>
OBV可以被看成是一个累积量，OBV的初始值为0，在第一根Bar的时候，若价格是上涨的，OBV则加上这根Bar的成交量VOL，即OBV=VOL，若第一根Bar是下跌的，OBV就减去这根Bar的成交量VOL，即OBV=-VOL。<br>
通俗地去理解OBV，它跟资金流很像，当价格上涨时，期间的成家量被认为是推动价格上涨的动力（类似于资金流当中的“流入”），因此OBV需要加上这部分成交量；当价格下跌的时候，期间成交量被认为是空方力量（类似于资金流当中的“流出”），因此OBV需要减去这部分成家量。OBV看绝对数量没有太大意义，各个品种间的OBV没有可比性，主要是看趋势走向，OBV持续走高，说明近期不断有资金流入，后市走强的概率也比较大。

**DMI 动向指标**：
```
    #tr是最高价与最低价的差值、最高价与前一天收盘价的差值、以及最低价与前一天收盘价的差值中的最大值。
    tr = pd.Series(np.vstack([df.high - df.low, (df.high - df.close.shift()).abs(),
                              (df.low - df.close.shift()).abs()]).max(axis=0), index=df.index)
    trz = tr.rolling(n).sum()
    _m = pd.DataFrame()
    #高点差和低点差
    _m['hd'] = df.high - df.high.shift()
    _m['ld'] = df.low.shift() - df.low
    # 正向和负向移动的总和
    _m['mp'] = _m.apply(lambda x: x.hd if x.hd > 0 and x.hd > x.ld else 0, axis=1)
    _m['mm'] = _m.apply(lambda x: x.ld if x.ld > 0 and x.hd < x.ld else 0, axis=1)
    _m['dmp'] = _m.mp.rolling(n).sum()
    _m['dmm'] = _m.mm.rolling(n).sum()
    _dmi = df.copy()
    # 正负向指示器，相应移动总和与平均真实范围的比例。
    _dmi['pdi'] = 100 * _m.dmp.div(trz)
    _dmi['mdi'] = 100 * _m.dmm.div(trz)
    # _dmi['adx'] = ((_dmi.mdi - _dmi.pdi).abs() / (_dmi.mdi + _dmi.pdi) * 100).rolling(m).mean()
    # _dmi['adxr'] = (_dmi.adx + _dmi.adx.shift(m)) / 2
    _dmi['pdi'] = _dmi['pdi'].fillna(0)
    _dmi['mdi'] = _dmi['mdi'].fillna(0)
    # dmi是pdi和mdi的差值, 表示正向和负向指示器之间的差异。
    _dmi['dmi'] = _dmi['pdi'] - _dmi['mdi']

    _dmi['side'] = 0
    c = len(_dmi)
    for i in range(c):
        if i > 1 and i + 1 < c:
            # 如果当前dmi值大于0且大于前一行的dmi值，买入信号
            if _dmi['dmi'].iloc[i] > 0 and _dmi['dmi'].iloc[i] > _dmi['dmi'].iloc[i - 1]:
                _dmi['side'].values[i] = 1
            # 如果当前dmi值小于0且小于前一行的dmi值，卖出信号
            if _dmi['dmi'].iloc[i] < 0 and _dmi['dmi'].iloc[i] < _dmi['dmi'].iloc[i - 1]:
                _dmi['side'].values[i] = 0

    _dmi['signal'] = _dmi['side'].shift(1).fillna(0)
```
**RSJ**:

**Chaikin_Oscillator 柴金震荡指标**：<br>
第一步：计算A/D<br>
类似OBV，算法如下： AC = 昨日AC + 资金流量乘数 * volume，其中： 资金流量乘数 = [(close- low) - (high - close)] / (high - low)<br>
第二步：从A/D的3日指数平均线EMA中减去10日EMA。<br>

Chaikin 震荡指标的核心是 A/D 线，它使用资产的收盘价相对于其高低范围，按其交易量加权，来确定资产是在积累（看涨）还是在分配（看跌）。与 MACD 一样，柴金震荡指标衡量两条移动平均线之间的距离。然而，柴金震荡指标不是收盘价，而是使用 A/D 线的两个指数移动平均线 (EMA) 计算的，通常为 3 和 10。<br>
由此产生的指标在零线上方和下方震荡。正值表示买入压力或积累，而负值表示卖出压力或分配。换句话说，当较快的 EMA 移动到较慢的 EMA 上方时，振荡器将变为正值。当较快的 EMA 穿过较慢的 EMA 下方时，它将显示为负值。

**LPPL模型(预测股灾)**<br>
https://zhuanlan.zhihu.com/p/22362112

**华泰证券 多因子指数增强**<br>
指数增强可以自上而下区分为仓位控制、行业轮动与选股。仓位控制是基于投资人在
宏观层面对市场宏观环境的判断，行业轮动是基于投资人在中观层面对于不同行业表现的
判断，选股是基于投资人在微观层面对于个股业绩的判断。<br>
仓位控制本质上就是中长线择时，其目的是预判大盘走势，在上涨时调高仓位，在下跌时降低仓位，调整频率一般在月频至年频。一般规定股票资产投资比例不低于基金资产的80%或90%<br>
多因子策略的构建大致分为“因子筛选——收益预测——风险预测——组合优化”四步。<br>
一般认为有效因子可以大致划分成两类——收益因子（Alpha 因子）和风险因子（Beta
因子）。能够长期稳定预测个股收益的因子是收益因子，能够对个股收益有强解释能力、但对收益预测正负方向不稳定的因子是风险因子。收益因子和风险因子的划分并不是一成不变的，根据市场有效性原理，当一个收益因子被广泛知晓之后，就会变成一个系统性行为因子，也即转化成为风险因子。在 2007～2016 年间，反转因子曾经是 A 股市场的收益
因子，2017 年之后开始转化成风险因子。

