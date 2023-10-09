# Quant
量化研报
# 20230412_中泰证券_“均线”才是绝对收益利器-ICU均线下的择时策略
**关键词：处理离群值，稳健回归**

CTA背景：<br>
由于在资产配置组合中，CTA 策略通常与其他策略都保持着极低的相关性，所以这类产品有着很强的配置工具价值。在 2000~2002 年全球股票熊市以及 2008 年全球次贷危机时期，巴莱克 CTA 基金指数（全球CTA具有代表性的行业基准）不仅没有下跌还实现了正收益，当股票市场和债券市场发生危机时，CTA 可以提供强劲的收益。<br>
总体来看，CTA 策略在整个交易市场上，趋势策略占比约 70%，均值回归策略占 25%左右，反趋势或趋势反转占 5%左右。

均线策略：<br>
普通均线的问题来自于，普通均线反应较慢，底部反弹很久后才出信号，顶部反转一段时间后才出现卖出信号。这是由于其对于极值或者异常值处理不够稳健，容易受到异常值的影响<br>
改进：稳健回归，对于异常值有很好的鲁棒性。文章选用其中一种重复中位数回归（Repeated Median Regression）方法。该方法通过多轮的中位数调整，逐步减小数据中的离群点对结果的影响。重复中位数的优点在于不需要对数据进行正态分布等假设，并且对于离群点比较鲁棒
![1696873994283](https://github.com/Marcotong21/Quant/assets/125079176/fa78f1e0-75e9-4921-9eda-1605d1501e69)

ICU 均线策略（名字是作者自己起的）的优点就是简单、稳健，模型参数很少，也不存在过拟合的问题，而且策略以中短期为主，回撤可控，且无需高频交易，可用于机构的实战投资。 
