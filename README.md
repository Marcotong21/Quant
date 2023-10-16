# Quant
量化研报
# 20230412_中泰证券_“均线”才是绝对收益利器-ICU均线下的择时策略
这篇貌似比较水，回测结果貌似也是不真实/过拟合的

**关键词：处理离群值，稳健回归（重复中位数回归）**

CTA背景：<br>
由于在资产配置组合中，CTA 策略通常与其他策略都保持着极低的相关性，所以这类产品有着很强的配置工具价值。在 2000~2002 年全球股票熊市以及 2008 年全球次贷危机时期，巴莱克 CTA 基金指数（全球CTA具有代表性的行业基准）不仅没有下跌还实现了正收益，当股票市场和债券市场发生危机时，CTA 可以提供强劲的收益。<br>
总体来看，CTA 策略在整个交易市场上，趋势策略占比约 70%，均值回归策略占 25%左右，反趋势或趋势反转占 5%左右。

均线策略：<br>
普通均线的问题来自于，普通均线反应较慢，底部反弹很久后才出信号，顶部反转一段时间后才出现卖出信号。这是由于其对于极值或者异常值处理不够稳健，容易受到异常值的影响<br>
改进：稳健回归，对于异常值有很好的鲁棒性。文章选用其中一种重复中位数回归（Repeated Median Regression）方法。该方法通过多轮的中位数调整，逐步减小数据中的离群点对结果的影响。重复中位数的优点在于不需要对数据进行正态分布等假设，并且对于离群点比较鲁棒
![1696873994283](https://github.com/Marcotong21/Quant/assets/125079176/fa78f1e0-75e9-4921-9eda-1605d1501e69)

ICU 均线策略（名字是作者自己起的）的优点就是简单、稳健，模型参数很少，也不存在过拟合的问题，而且策略以中短期为主，回撤可控，且无需高频交易，可用于机构的实战投资。 

# 20170501-光大证券-择时系列报告之一：基于阻力支撑相对强度（RSRS）的市场择时
支撑位即是指标的价格在下跌时可能遇到的支撑，是交易者认为买方力量开始反超卖方使得价格在此止跌或反弹上涨的价位；阻力位则是指在标的价格上涨时可能遇到的压力，是交易者认为卖方力量开始反超买方而使得价格难以继续上涨或就此回调下跌的价位。

包括均线策略、布林带策略在内，这些策略都是讲支撑位与阻力位视为定值。其优点是在大趋势中能获得很好的收益，缺点是在震荡行情中会出现滞后性。

现将阻力位与支撑位视为一个变量。阻力位与支撑位实质上反应了交易者对目前市场状态顶底的一种预期判断。从直觉上看，如果这种预期判断极易改变，则表明支撑位或阻力位的强度小，有效性弱；而如果众多交易者预期较为一致、变动不大，则表明支撑位或阻力位强度高，有效性强。

如果支撑位的强度小，作用弱于阻力位，则表明市场参与者对于支撑位的分歧大于对于阻力位的分歧，市场接下来更倾向于向熊市转变。而如果支撑位的强度大，作用强于阻力位，则表示市场参与者对于支撑位的认可度更高于对于阻力位的认可度，市场更倾向于在牛市转变。   **（why？）**

每日的最高价与最低价就是一种阻力位与支撑位，它是当日全体市场参与者的交易行为所认可的阻力与支撑。**（好精彩的想法！）**这里我们并非用支撑位与阻力位作突破或反转交易的阈值，而是更关注市场参与者们对于阻力位与支撑位的定位一致性。当日最高价与最低价能迅速反应近期市场对于阻力位与支撑位态度的性质，是我们使用最高价与最低价的最重要原因。

我们用相对位置变化强度来描述阻力支撑相对强度。考虑对近N个数据点限定回归来得到信噪比较高的相对变化强度，得到：high = alpha + beta*low + epsilon， epsilon ~ N(0,sigma)

这里beta就是需要的斜率。其中 N 的取法不能太小，不然不能过滤掉足够多的噪音；但也不能太大，因为我们希望得到的是体现目前市场的支撑阻力相对强度，若取值太大，则滞后性太高。

当斜率值很大时->最高价变动更加迅速->支撑强度强于阻力强度。
![1696905268320](https://github.com/Marcotong21/Quant/assets/125079176/4139d367-ab1d-4175-9a79-0ce70315b9db)
上图分别代表继续走强的上涨牛市，以及下跌势头渐止的下跌熊市。（最低价变动缓慢->支撑点更加稳固->上涨趋势）
![1696905569444](https://github.com/Marcotong21/Quant/assets/125079176/9cccb37b-41b6-449f-85d3-6aadc16b7b48)
这两张图则相反，代表有下跌倾向的牛熊市。

总的来说，斜率beta越大，越有上涨趋势; beta越小，越有下跌趋势。

构建RSRS指标<br>
斜率指标与标准分指标，比较后发现后者效果更好（标准分指标增加了两个自由度，周期M和阈值S）。标准分指标策略如下：<br>
1.取前M日（例如M=600）的序列，计算当日的标准分z
2.对近N日（例如N=18）的标准分z线性回归，得到当日的斜率标准分
3.如果斜率标准分大于S（例如S=0.7）则买入，小于-S则卖出
观察到无论是斜率指标还是标准分指标都在09年至14年的震荡区间净值较稳定增长，这正是RSRS 指标优秀左侧预测能力的体现。

敏感性测试：<br>
当数据个数N选用为20时，策略效果有一个明显的下跌。可能的原因是：20是许多技术指标（如均线计算）的默认常用参数，因此当大量交易者按照以20 这个周期计算的技术指标进行交易，就会影响到 20 这个周期的最高价最低价数据信息分布。

优化：<br>
我们将标准分值与线性拟合的R方值相乘得到修正的标准分。以此降低绝对值很大，但实际拟合效果很差的标准分对策略的影响。修正的标准分在偏度上有明显的向正态修正的效果。然而修正标准分对策略收益的提升并不高。可能原因如下：<br>
1.研究标准分分布对未来市场收益的预测性。得到结果是，右侧标准分（z>0）与收益率有尚可的正相关性，是较好的牛市预测指标。而在左侧几乎失去任何预测性。如左图所示。<br>
2.研究修正标准分与未来市场收益的预测性，发现整体相关性得到了改善，尤其是左侧标准分的表现。如右图所示。<br>
由于在一般的股票策略中，只考虑做多策略，因此左侧标准分的预测能力对于择时策略没有很大的帮助。标准分和修正标准分这两者对于右侧的预测能力没有较大区别，因此二者的收益也相差不大。<br>

<img src="(images/1697421950649.png)" width="300" height="200">

<img src="(https://github.com/Marcotong21/Quant/assets/125079176/a02f9113-615c-40aa-bf88-48c2a91405bd)" width="300" height="200">

观察指标值域的改变，一个大胆的想法是，是否右侧数据值域越广，其对未来收益率的预测越好？是否左侧数据值域越窄越好？能否通过改变标准分的分布来达到改善整体指标预测性的目的？<br>
改进：右偏标准分=修正标准分x斜率 (斜率本身几乎一定是正值，故无偏分布x右偏分布为右偏）



