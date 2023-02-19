"""
All buy and sell order responses have the same output format.

:example output:

    {
        'symbol': 'BTCUSDT',
        'orderId': 123456789,
        'orderListId': -1,
        'clientOrderId': 'abc123',
        'transactTime': 1645097712889,
        'price': '50000.00',
        'origQty': '1.00',
        'executedQty': '0.00',
        'cummulativeQuoteQty': '0.00',
        'status': 'NEW',
        'timeInForce': 'GTC',
        'type': 'LIMIT',
        'side': 'BUY',
        'fills': []
    }
"""
import logging
import os
import time
from typing import Dict

from get_client import get_client
import db

CLIENT = get_client()
WAIT_UNTIL_FILLED_POLL_TIME = float(os.environ.get("WAIT_UNTIL_FILLED_POLL_TIME", "0.5"))
TRADING_STOP_LOSS_POLL_TIME = float(os.environ.get("TRADING_STOP_LOSS_POLL_TIME", "0.5"))

log = logging.getLogger()


def limit_buy(symbol: str, quantity: float, purchase_price: float) -> Dict:
    """
    Create a limit buy order for the specified symbol, quantity, and purchase price.

    :param symbol: The symbol of the cryptocurrency to buy (e.g. "BTCUSDT").
    :param quantity: The quantity of the cryptocurrency to buy.
    :param purchase_price: The maximum price to pay for each unit of the cryptocurrency.
    :return: The response from the Binance API containing information about the created buy order.
    """
    # Create a new limit buy order with the specified parameters.
    buy_order = CLIENT.create_order(
        symbol=symbol,
        side='BUY',
        type='LIMIT',
        timeInForce='GTC',
        quantity=quantity,
        price=str(purchase_price),
        newOrderRespType='FULL'
    )
    log.info(f'buy_order: {buy_order}')
    return buy_order


def stop_loss_sell(symbol: str, quantity: float, stop_price: float) -> Dict:
    """
    Create a stop loss sell order for the specified symbol and quantity at the specified stop price.

    :param symbol: The symbol of the cryptocurrency to sell (e.g. "BTCUSDT").
    :param quantity: The quantity of the cryptocurrency to sell.
    :param stop_price: The stop price at which to trigger the sell order.
    :return: The response from the Binance API containing information about the created stop loss order.
    """
    # Create a stop loss sell order for the specified symbol, quantity, and stop price
    stop_loss_order = CLIENT.create_order(
        symbol=symbol,
        side='SELL',
        type='STOP_LOSS',
        timeInForce='GTC',
        quantity=quantity,
        price=str(stop_price),
        stopPrice=str(stop_price),
        newOrderRespType='FULL'
    )
    log.info(f'stop_loss_order: {stop_loss_order}')
    return stop_loss_order


def cancel_order(order: Dict) -> Dict:
    """
    Cancels a Binance order.

    :example output:

    {
        'symbol': 'BTCUSDT',
        'origClientOrderId': 'x4c4pJCSsaRt62GJtZGBgS',
        'orderId': 1071494812,
        'orderListId': -1,
        'clientOrderId': 'pDWcoZmzGecFvth47Yxnkl',
        'price': '0.00000000',
        'origQty': '0.01000000',
        'executedQty': '0.00000000',
        'cummulativeQuoteQty': '0.00000000',
        'status': 'CANCELED',
        'timeInForce': 'GTC',
        'type': 'LIMIT',
        'side': 'BUY',
        'stopPrice': '0.00000000',
        'icebergQty': '0.00000000',
        'time': 1645580999689,
        'updateTime': 1645581001266,
        'isWorking': True,
        'origQuoteOrderQty': '0.00000000'
    }

    :param order: A dictionary containing the order details, such as the symbol and order ID.
    :return: A dictionary containing the details of the canceled order.
    """
    # Call the `cancel_order()` method provided by the Python-Binance library
    # to cancel the order.
    canceled_order = CLIENT.cancel_order(
        symbol=order['symbol'],
        orderId=order['orderId']
    )
    log.info(f'canceled_order: {canceled_order}')
    return canceled_order


def is_filled(order: Dict) -> bool:
    """
    Check if an order has been filled.

    :param order: A dictionary containing order details (symbol and orderId).
    :return: A boolean indicating whether the order has been filled.
    """
    # retrieve order status from the client API
    order_status = CLIENT.get_order(
        symbol=order['symbol'],
        orderId=order['orderId']
    )
    # check if the order is filled
    return order_status['status'] == 'FILLED'


def wait_until_filled(order: dict, timeout: float = 60):
    """
    Wait for an order to be filled before proceeding.

    :param order: A dictionary containing order details (symbol and orderId).
    :param timeout: The maximum amount of time (in seconds) to wait for the order to be filled.
    """
    log.debug(f'Waiting for filled: {order}')
    start_time = time.time()
    while not is_filled(order) and time.time() - start_time <= timeout:
        time.sleep(WAIT_UNTIL_FILLED_POLL_TIME)
    log.debug(f'Is filled: {order}')


def trailing_stop_loss(symbol: str, stop_percentage: float, quantity: float):
    """
    Trailing stop loss function that protects a position by placing a stop loss order and adjusting it
    based on the current price.

    :param symbol: The symbol of the cryptocurrency to be traded.
    :param stop_percentage: The percentage at which the stop loss price should be set.
    :param quantity: The amount of the cryptocurrency to be traded.
    """
    # Retrieve the current price of the cryptocurrency from a database
    current_price = db.get_current_price(symbol)

    # Calculate the initial purchase price and stop price
    stop_price = current_price - (current_price * stop_percentage / 100)
    log.info(
        (
            f'Starting trailing stop - '
            f'symbol: {symbol}, '
            f'quantity: {quantity}, '
            f'current_price: {current_price}, '
            f'stop_price: {stop_price}, '
        )
    )

    # Place a stop loss order to protect the position
    stop_loss_order = stop_loss_sell(symbol, quantity, stop_price)

    # Start a loop to check the current price and adjust the stop loss order
    while True:
        # Wait for a short period of time
        time.sleep(TRADING_STOP_LOSS_POLL_TIME)

        # Get the current price of the cryptocurrency
        current_price = db.get_current_price(symbol)

        # If the current price is higher than the previous stop price,
        # cancel the previous stop loss order and place a new one with a higher stop price
        if current_price > stop_price:
            # Cancel the previous stop loss order
            cancel_order(stop_loss_order)

            # Calculate the new stop price
            stop_price = current_price - (current_price * stop_percentage / 100)

            # Place a new stop loss order with the new stop price
            stop_loss_order = stop_loss_sell(symbol, quantity, stop_price)

        # If the current price is less than or equal to the stop price and the stop loss order is filled, exit the loop
        if current_price <= stop_price:
            wait_until_filled(stop_loss_order)
            break
    log.info(
        (
            f'Finished trailing stop - '
            f'symbol: {symbol}, '
            f'quantity: {quantity}, '
            f'current_price: {current_price}, '
            f'stop_price: {stop_price}, '
        )
    )
