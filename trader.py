from typing import Dict, List
from datamodel import OrderDepth, TradingState, Order
import numpy as np
mid_banana = [] #high score 591
mid_pearl = [] #high score 852
mid_coco = []
class Trader:
    profit = 0
    limit = 20
    coco_limit = 600
    banana_bal = 0
    ema = 5000
    last_trend = 0
    crits = [{'price':7990,'state':'sell'}]
    def run(self, state: TradingState) -> Dict[str, List[Order]]:
        # Initialize the method output dict as an empty dict
        result = {}

        pearl_position = state.position.get('PEARLS', 0)
        banana_position = state.position.get('BANANAS', 0)
        coco_position = state.position.get('COCONUTS', 0)
        for product in state.order_depths.keys():
            if product == 'PEARLS':
                order_depth: OrderDepth = state.order_depths[product]
                orders: list[Order] = []
                asks = []
                bids = []
                while len(order_depth.sell_orders) > 0:
                    asks.append({'price': min(order_depth.sell_orders.keys()),
                                 'vol': order_depth.sell_orders[min(order_depth.sell_orders.keys())]})
                    del order_depth.sell_orders[min(order_depth.sell_orders.keys())]
                while len(order_depth.buy_orders) != 0:
                    bids.append({'price': max(order_depth.buy_orders.keys()),
                                 'vol': order_depth.buy_orders[max(order_depth.buy_orders.keys())]})
                    del order_depth.buy_orders[max(order_depth.buy_orders.keys())]
                if len(asks) != 0:
                    if asks[0]['price'] < 10000 or (asks[0]['price'] == 10000 and pearl_position < -2):
                        if pearl_position - asks[0]['vol'] > Trader.limit:
                            asks[0]['vol'] = -(Trader.limit - pearl_position)
                            print('missed full trade')
                        orders.append(Order(product, asks[0]['price'], -asks[0]['vol']))
                        pearl_position -= asks[0]['vol']
                        print("BUY", str(-asks[0]['vol']) + "x", asks[0]['price'], 'pearl_positions:',
                              pearl_position)
                    elif bids[0]['price'] > 10000 or (bids[0]['price'] == 10000 and pearl_position > -5):
                        if pearl_position - bids[0]['vol'] < -Trader.limit:
                            bids[0]['vol'] = pearl_position + Trader.limit
                            print('missed full trade')
                        orders.append(Order(product, bids[0]['price'], -bids[0]['vol']))
                        pearl_position -= bids[0]['vol']
                        print("SELL", str(bids[0]['vol']) + "x", bids[0]['price'], 'pearl_positions:',
                              pearl_position)
                    elif pearl_position > 15:
                        orders.append(Order(product, 10002, -10))
                    elif pearl_position < -15:
                        orders.append(Order(product, 9998, 10))
                    elif pearl_position > 0:
                        # orders.append(Order(product, 10002, -(Trader.limit-pearl_position)))
                        orders.append(Order(product, 10004, -10))
                        orders.append(Order(product, 9996, 5))
                    else:
                        orders.append(Order(product, 10004, -5))
                        orders.append(Order(product, 9996, 10))
                        # orders.append(Order(product, 9998, pearl_position + Trader.limit))

                    print(pearl_position)
                result[product] = orders
            if product == 'BANANAS':
                order_depth: OrderDepth = state.order_depths[product]
                if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                    mid_banana.append((max(order_depth.buy_orders.keys())+min(order_depth.sell_orders.keys()))/2)
                orders: list[Order] = []
                asks = []
                bids = []
                spread = min(order_depth.sell_orders.keys()) - max(order_depth.buy_orders.keys())
                while len(order_depth.sell_orders) > 0:
                    asks.append({'price': min(order_depth.sell_orders.keys()),
                                'vol': order_depth.sell_orders[min(order_depth.sell_orders.keys())]})
                    del order_depth.sell_orders[min(order_depth.sell_orders.keys())]
                while len(order_depth.buy_orders) != 0:
                    bids.append({'price': max(order_depth.buy_orders.keys()),
                                'vol': order_depth.buy_orders[max(order_depth.buy_orders.keys())]})
                    del order_depth.buy_orders[max(order_depth.buy_orders.keys())]
                avg_window = 5
                acceptable_price = np.mean(mid_banana[-avg_window:])
                a10 = np.mean(mid_banana[-50:])
                a100 = np.mean(mid_banana[-200:])
                std = np.std(mid_banana[-avg_window:])
                buy = (a10 - a100) >0
                factor = int(0.1*spread)
                if state.timestamp<600:
                    break
                if asks[0]['price'] < acceptable_price or (asks[0]['price'] == acceptable_price and banana_position < -2):
                    if banana_position - asks[0]['vol'] > Trader.limit:
                        asks[0]['vol'] = -(Trader.limit - banana_position)
                        print('missed full trade')
                    orders.append(Order(product, asks[0]['price'], -asks[0]['vol']))
                    banana_position -= asks[0]['vol']
                    print("BUY", str(-asks[0]['vol']) + "x", asks[0]['price'], 'banana_positions:',banana_position)
                elif bids[0]['price'] > acceptable_price or (bids[0]['price'] == acceptable_price and banana_position > -5):
                    if banana_position - bids[0]['vol'] < -Trader.limit:
                        bids[0]['vol'] = banana_position + Trader.limit
                        print('missed full trade')
                    orders.append(Order(product, bids[0]['price'], -bids[0]['vol']))
                    banana_position -= bids[0]['vol']
                    print("SELL", str(bids[0]['vol']) + "x", bids[0]['price'], 'banana_positions:',
                        banana_position)
                elif banana_position > 0:
                    # orders.append(Order(product, 10002, -(Trader.limit-pearl_position)))
                    orders.append(Order(product, acceptable_price+factor, -18))
                    orders.append(Order(product, acceptable_price-factor, 9))
                else:
                    orders.append(Order(product, acceptable_price+factor, -9))
                    orders.append(Order(product, acceptable_price-factor, 18))
                result[product] = orders
                """elif banana_position > 10 or not buy:
                    orders.append(Order(product, acceptable_price+factor/2, -10))
                    orders.append(Order(product, acceptable_price - factor, 5))
                elif banana_position < -10:
                    orders.append(Order(product, acceptable_price + factor, -5))
                    orders.append(Order(product, acceptable_price-factor/2, 10))"""
            if product == 'COCONUTS':
                order_depth: OrderDepth = state.order_depths[product]
                if len(order_depth.sell_orders) > 0 and len(order_depth.buy_orders) > 0:
                    mid_coco.append((max(order_depth.buy_orders.keys())+min(order_depth.sell_orders.keys()))/2)
                orders: list[Order] = []
                asks = []
                bids = []
                spread = min(order_depth.sell_orders.keys()) - max(order_depth.buy_orders.keys())
                while len(order_depth.sell_orders) > 0:
                    asks.append({'price': min(order_depth.sell_orders.keys()),
                                'vol': order_depth.sell_orders[min(order_depth.sell_orders.keys())]})
                    del order_depth.sell_orders[min(order_depth.sell_orders.keys())]
                while len(order_depth.buy_orders) != 0:
                    bids.append({'price': max(order_depth.buy_orders.keys()),
                                'vol': order_depth.buy_orders[max(order_depth.buy_orders.keys())]})
                    del order_depth.buy_orders[max(order_depth.buy_orders.keys())]
                avg_window = 50
                acceptable_price = np.mean(mid_coco[-avg_window:])
                factor = int(3 * spread)
                a50 = np.mean(mid_coco[-50:])
                a100 = np.mean(mid_coco[-100:])
                trend = a50-a100
                """a10 = np.mean(mid_coco[-50:])
                a100 = np.mean(mid_coco[-200:])
                std = np.std(mid_coco[-avg_window:])
                buy = (a10 - a100) >0
                if buy:
                    print('buy')
                else:
                    print('sell')
                
                print('factor:',factor)
                if state.timestamp<600:
                    break
                if asks[0]['price'] < acceptable_price or (asks[0]['price'] == acceptable_price and coco_position < -2):
                    if coco_position - asks[0]['vol'] > Trader.limit:
                        asks[0]['vol'] = -(Trader.limit - coco_position)
                        print('missed full trade')
                    orders.append(Order(product, asks[0]['price'], -asks[0]['vol']))
                    coco_position -= asks[0]['vol']
                    print("BUY", str(-asks[0]['vol']) + "x", asks[0]['price'], 'coco_positions:',coco_position)
                elif bids[0]['price'] > acceptable_price or (bids[0]['price'] == acceptable_price and coco_position > -5):
                    if coco_position - bids[0]['vol'] < -Trader.limit:
                        bids[0]['vol'] = coco_position + Trader.limit
                        print('missed full trade')
                    orders.append(Order(product, bids[0]['price'], -bids[0]['vol']))
                    coco_position -= bids[0]['vol']
                    print("SELL", str(bids[0]['vol']) + "x", bids[0]['price'], 'coco_positions:',
                        coco_position)"""
                if abs(trend)<0.5 and abs(Trader.last_trend)>0.5:
                    print('critical point at',mid_coco[-1])
                    if mid_coco[-1]>Trader.crits[-1]['price']:
                        Trader.crits.append({'price':mid_coco[-1],'state':'sell'})
                        #orders.append(Order(product, mid_coco[-1], -coco_position))
                    else:
                        Trader.crits.append({'price':mid_coco[-1],'state':'buy'})
                    print(Trader.crits)
                elif abs(trend)<0.5:
                    print(Trader.crits[-1]['state'],'at',Trader.crits[-1]['price'],'ask:',asks[0]['price'],'bid:',bids[0]['price'])
                    if Trader.crits[-1]['state']=='buy':
                        if asks[0]['price'] < Trader.crits[-1]['price']:
                            orders.append(Order(product, asks[0]['price'], -asks[0]['vol']))
                            print('coco',coco_position)
                        else:
                            orders.append(Order(product, Trader.crits[-1]['price'], 20))
                            print('coco', coco_position)
                    else:
                        if asks[0]['price'] > Trader.crits[-1]['price']:
                            orders.append(Order(product, bids[0]['price'], -bids[0]['vol']))
                            print('coco', coco_position)
                        else:
                            orders.append(Order(product, Trader.crits[-1]['price'], -20))
                            print('coco', coco_position)
                elif asks[0]['price']<Trader.crits[-1]['price']-2:
                    orders.append(Order(product, mid_coco[-1], -asks[0]['vol']))
                    print('buy coco at',asks[0]['price'],'coco', coco_position)
                elif bids[0]['price']>Trader.crits[-1]['price']+2:
                    orders.append(Order(product, mid_coco[-1], -bids[0]['vol']))
                    print('sell coco at',bids[0]['price'],'coco', coco_position)
                Trader.last_trend=trend
                result[product] = orders
        return result