# core/order_manager.py
"""
🤖 УПРАВЛЕНИЕ ОРДЕРАМИ ДЛЯ GRID BOT
"""

class OrderManager:
    """🤖 УПРАВЛЕНИЕ ОРДЕРАМИ ДЛЯ GRID BOT"""
    def __init__(self, api_client):
        self.api_client = api_client
        self.active_order_ids = []
        self.total_orders_created = 0
        self.total_commission = 0

    def create_grid(self, symbol, grid_levels, order_size, grid_spacing, current_price):
        """🎯 СОЗДАНИЕ СЕТКИ ОРДЕРОВ"""
        buy_prices = [round(current_price * (1 - i * grid_spacing), 1) for i in range(1, grid_levels + 1)]
        sell_prices = [round(current_price * (1 + i * grid_spacing), 1) for i in range(1, grid_levels + 1)]
        print(f"📥 Уровни покупки: {[f'{p:,.1f}' for p in buy_prices]}")
        print(f"📤 Уровни продажи: {[f'{p:,.1f}' for p in sell_prices]}")
        orders_placed = 0
        self.active_order_ids = []
        usdt_balance, btc_balance = self.api_client.get_balance()
        # Размещаем ордера на покупку
        for price in buy_prices:
            required_usdt = order_size * price * 1.1
            if usdt_balance > required_usdt:
                try:
                    order = self.api_client.place_order(
                        symbol=symbol,
                        side="Buy",
                        order_type="Limit",
                        qty=order_size,
                        price=price,
                        time_in_force="GTC"
                    )
                    if order and 'result' in order and 'orderId' in order['result']:
                        order_id = order['result']['orderId']
                        self.active_order_ids.append(order_id)
                        orders_placed += 1
                        self.total_orders_created += 1
                        # Учет комиссии
                        commission = self.calculate_commission(order_size, price, 'BUY')
                        self.total_commission += commission
                        print(f"✅ Buy ордер: {order_size} BTC по {price:.1f}")
                    else:
                        print(f"❌ Ошибка размещения Buy ордера")
                except Exception as e:
                    print(f"❌ Ошибка Buy ордера: {e}")
            else:
                print(f"⚠️ Недостаточно USDT для Buy ордера по {price:.1f}")
        # Размещаем ордера на продажу
        for price in sell_prices:
            if btc_balance > order_size:
                try:
                    order = self.api_client.place_order(
                        symbol=symbol,
                        side="Sell",
                        order_type="Limit",
                        qty=order_size,
                        price=price,
                        time_in_force="GTC"
                    )
                    if order and 'result' in order and 'orderId' in order['result']:
                        order_id = order['result']['orderId']
                        self.active_order_ids.append(order_id)
                        orders_placed += 1
                        self.total_orders_created += 1
                        # Учет комиссии
                        commission = self.calculate_commission(order_size, price, 'SELL')
                        self.total_commission += commission
                        print(f"✅ Sell ордер: {order_size} BTC по {price:.1f}")
                    else:
                        print(f"❌ Ошибка размещения Sell ордера")
                except Exception as e:
                    print(f"❌ Ошибка Sell ордера: {e}")
            else:
                print(f"⚠️ Недостаточно BTC для Sell ордера по {price:.1f}")
        print(f"📊 Размещено ордеров: {orders_placed}")
        print(f"📈 Всего ордеров создано: {self.total_orders_created}")
        return orders_placed

    def cancel_all_orders(self, symbol):
        """🛑 ОТМЕНА ВСЕХ ОРДЕРОВ"""
        try:
            result = self.api_client.cancel_all_orders(symbol)
            self.active_order_ids = []
            print("✅ Все ордера отменены")
            return True
        except Exception as e:
            print(f"⚠️ Ошибка при отмене ордеров: {e}")
            return False

    def get_active_orders_count(self, symbol):
        """📋 ПОЛУЧЕНИЕ КОЛИЧЕСТВА АКТИВНЫХ ОРДЕРОВ"""
        try:
            orders = self.api_client.get_open_orders(symbol)
            if (orders and
                'result' in orders and 
                'list' in orders['result']):
                return len(orders['result']['list'])
            return 0
        except Exception as e:
            print(f"❌ Ошибка получения активных ордеров: {e}")
            return 0

    def calculate_commission(self, order_size, price, side):
        """💸 РАСЧЕТ КОМИССИИ ЗА СДЕЛКУ"""
        commission_rate = 0.001  # 0.1% комиссия
        order_value = order_size * price
        commission = order_value * commission_rate
        return commission

    def get_order_statistics(self):
        """📊 СТАТИСТИКА ОРДЕРОВ"""
        return {
            'total_orders_created': self.total_orders_created,
            'active_orders': len(self.active_order_ids),
            'total_commission': self.total_commission
        }

    def cleanup(self):
        """🧹 ОЧИСТКА РЕСУРСОВ"""
        self.active_order_ids = []
