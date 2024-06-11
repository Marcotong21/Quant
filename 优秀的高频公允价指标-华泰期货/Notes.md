对于期货做市商而言，为期货合约确定**公允价**是非常重要的。传统衡量公允价的方法包括mid、vwap。

### mid
mid的问题在于，其变化具有高度的自相关性，且其信号相对更加低频。此外，它并没有使用volume的信息，缺少有效的信息。

### vwap
vwap的计算公式为 
$$vwap= \frac{Ask1*BidVolume1 +Bid1*AskVolume1}{BidVolume1+AskVolume1}
$$

其中卖价用买单加权，买价用卖单加权，是因为市场合理的价格应更偏向挂单更少的那一侧。vwap的缺陷是其存在跟多的噪音，以及有时计算会更加反直觉。

### Micro price：更优的公允价
