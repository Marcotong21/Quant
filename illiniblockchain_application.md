# Part 1
Actually I did a market making strategy project last semester in FIN556. The link for the report is at:

https://gitlab.engr.illinois.edu/fin556_algo_market_micro_fall_2023/fin556_algo_fall_2023_group_05/group_05_project/-/blob/main/Final_Report/final_report.md

In that project, we have some problem at backtesting part, so our backtesting result might not look good. But I believe the strategy itself is generally good and logical.

![1](https://github.com/Marcotong21/Quant/assets/125079176/8b56fa62-cda0-4d63-98da-47ebcede429b)
![2](https://github.com/Marcotong21/Quant/assets/125079176/27e0096f-3b6d-4f77-9513-8038256725ab)




And luckily, one of my teammates have written the psedocode for the strategy. I made some changes based on your functions:
```
def get_market_info():
    order_book = GetOrderBook()
    best_bid = order_book["bids"][0]["price"]
    best_ask = order_book["asks"][0]["price"]
    market_info = {"best_bid": best_bid, "best_ask": best_ask}
    return market_info

def get_orders(market_info, inventory):
    mid_price = (market_info["best_bid"] + market_info["best_ask"]) / 2
    
    bid_price = mid_price - spread / 2 - inventory["percentage"] * target_spread
    ask_price = mid_price + spread / 2 - inventory["percentage"] * target_spread
    open_orders = get_open_orders()
    net_quantity = 0
    for order in open_orders:
        if order["side"] == "sell":
            net_quantity -= order["quantity"]
        else:
            net_quantity += order["quantity"]
    dynamic_quantity = inventory["quantity"] + net_quantity
    if dynamic_quantity > 0:
        ask_quantity = base_quantity + abs(dynamic_quantity)
        bid_quantity = base_quantity
    elif dynamic_quantity < 0:
        bid_quantity = base_quantity + abs(dynamic_quantity)
        ask_quantity = base_quantity
    PlaceOrder(bid_price, bid_quantity, buy)
    PlaceOrder(ask_price, ask_quantity, sell)
    return

def adjust_inventory(inventory):
    if inventory > max_position:
        PlaceOrder(GetRealTimePrice(), inventory, sell)
    elif inventory < -max_position:
        PlaceOrder(GetRealTimePrice(), -inventory, buy)


while trading:
  market_info = get_market_info()
  get_orders(market_info, inventory)
  
  # Update the inventory
  inventory = fetch_position()
  adjust_inventory(inventory)
```

And **More detailed explanations:** <br>
**1.** <br>
Basicly, we do market making at every time, tring to profit from spread at every time.
(At first my idea was we open position when there is a large spread, and Zhicheng suggested we can do market making of all time first. I think that's a good idea, and we might can try other signals later if we have Version 1 or 2)<br>
 We set our basic_spread $`S = x \cdot \tau`$ , where τ is the tick size, x is a parameter. <br>
Here S is simply fixed, but we can also make it dynamic in Version 1. For example, S can be several stds from the mean of the spread for the past day.<br>
**2. Bid and ask price:** <br>
We define our bid and ask price as <br>
$bid_price = min(best\_ask -\epsilon,   mid\_price - \frac{S}{2})$ <br>
$ask\_price = max(best\_bid +\epsilon,   mid\_price + \frac{S}{2})$ <br>
**3.Inventory Adjustment:** <br>
Considering some of our quotes might not be executed because of the shift of price, we might have inventory position. Inventory is the thing a market maker do not want to see, so we need to adjust our quotes according to our inventory. Assume our inventory position is δ%, then the updated bid and ask price is:<br>
$bid\_price = min(best\_bid -\epsilon,   mid\_price - \frac{S}{2} - c * τ * δ\%)$ <br>
$ask\_price = max(best\_ask +\epsilon,   mid\_price + \frac{S}{2} - c * τ * δ\%)$ <br>
Here the term $- c * τ * δ\%$ means "If we have positive inventory position, our bid/ask price will shift down to have a more competitive ask\_price and less competitive bid\_price. If negative position, our price will shift up." c is a parameter we need to optimize, and tick size τ is used to normalize scale.<br> 
**4.Quantity:** <br> 
The quantity of our quotes are basicly symmetric, but also depend on the inventory position. First we have a fixed base quantity y% of the maximum. (maximum money we have) Then at each position opening, we need to check our inventory position, and try to make the inventory position as close to 0 as possible. For example, if we have 1 Bitcoin remaining in our inventory position, and we want to do market making now. Then what we can do is placing an order to buy 1 bitcoin and an order to sell 2 bitcoins. In this case we will make the inventory close to 0.<br>
**5.Handle_data:** <br>
This part is mainly concerning how to deal with unexecuted orders. Me and Zhicheng thought about a lot of ways, and at last we still agreed that the GTD (Good Till Date) is the best way. We can set a lifetime N for each order and automatically cancel the order when it is not executed after the time. This is a good way to reduce the risk of long-term inventory position accumulation.<br>
**6.Inventory risk:** <br> 
This part is mainly concerning how to deal with large inventory position. Although we have developed dynamic quotes and quantities to make inventory position as close to 0 as possible, there are still extreme cases that occur. For example, when Bitcoin rises rapidly, our ask order will be executed while the bid order will remain unexecuteed. No matter how much we adjust our quotes and volume ratios, extreme up markets make it almost impossible to ever fill our buy orders. So we would have accumulated a large short inventory position. This is what a market maker do not want to see, so we need to also set a threshold for this. We can set a threshold $I\%$, and we will gradualy close our position whenever the ratio of our inventory position exceeds $I\%$.


# Part 2
1. Increasing Volatility:

**Adjustment:** Widen the target_spread or decrease quote quantity

**Reasoning:** Widen the spread will make more potential profit, which can lower the potential risk caused by volatility. Or just decrease/stop market making at this time.

2. Low Liquidity

**Adjustment:** Reduce the target_spread or increase quote quantity

**Reasoning:** Just opposite the last scenario, market makers can set smaller quote spreads and increase quote quantity and attract more trades with relatively low risk.

3. News Event and 4. One-sided Market:   Decrease quote quantity

**Adjustment:**: Widen the target spread and reduce order sizes.

**Reasoning:**: A one-sided market can cause quotes on one side to go unfilled, resulting in an inventory position. So we should try to avoid this scenario.

6. Price difference across exchanges

**Adjustment:**: Arbitrage, not sure about the specific adjustment.

6. Technical Glitch

**Adjustment:**: Reduce order sizes or even pause algorithm.

**Reasoning:**: This would be the most unpredicable and risky cause, we should definitely try to avoid it.

# Part 3
 I might use LSTM, which is highly suited for predicting stock or cryptocurrency prices due to their specialized structure for handling sequential data. LSTM is adept at learning long-term dependencies in data, a crucial feature for financial time series where past information often influences future trends. 
 Additionally, LSTM can retain relevant historical information and filter out the noise, a key aspect when dealing with the volatile nature of financial markets. This ability to process and remember significant events over lengthy periods makes it particularly effective in capturing complex patterns that are characteristic of stock and cryptocurrency price movements. 

 By the way, I also have some thoughts:
 personally I don't like to use only ML models to predict stock prices. ML is not very interpretable, and I think interpretability is a very important part of financial markets.ML is like a little black box, it may produce good predictability in the short term (although even that may not always be possible) but we don't know when it will suddenly fail. We can hardly afford such risk and uncertainty in real markets. So I think ML can be used as part of a strategy, for example when combining features, optimizing parameters.
 
