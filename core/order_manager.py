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
        # Выносим расчет цен в отдельные функции
        buy_prices, sell_prices = self._calculate_grid_prices(
            current_price, grid_levels, grid_spacing
        )
        # Выводим информацию о ценах
        self._print_price_levels(buy_prices, sell_prices)
        # Получаем баланс
        usdt_balance, btc_balance = self.api_client.get_balance()
        # Размещаем ордера на покупку и продажу
        buy_orders = self._place_buy_orders(
            symbol, order_size, buy_prices, usdt_balance
        )
        sell_orders = self._place_sell_orders(
            symbol, order_size, sell_prices, btc_balance
        )
        # Выводим статистику
        total_orders = buy_orders + sell_orders
        self._print_order_statistics(total_orders)
        return total_orders

    def _calculate_grid_prices(self, current_price, grid_levels, grid_spacing):
        """📊 РАСЧЕТ ЦЕН ДЛЯ СЕТКИ"""
        buy_prices = [
            round(current_price * (1 - i * grid_spacing), 1)
            for i in range(1, grid_levels + 1)
        ]
        sell_prices = [
            round(current_price * (1 + i * grid_spacing), 1)
            for i in range(1, grid_levels + 1)
        ]
        return buy_prices, sell_prices

    def _print_price_levels(self, buy_prices, sell_prices):
        """📋 ВЫВОД ИНФОРМАЦИИ О ЦЕНАХ"""
        print(f"📥 Уровни покупки: {[f'{p:,.1f}' for p in buy_prices]}")
        print(f"📤 Уровни продажи: {[f'{p:,.1f}' for p in sell_prices]}")

    def _place_buy_orders(self, symbol, order_size, buy_prices, usdt_balance):
        """📥 РАЗМЕЩЕНИЕ ОРДЕРОВ НА ПОКУПКУ"""
        orders_placed = 0
        for price in buy_prices:
            required_usdt = order_size * price * 1.1
            if usdt_balance > required_usdt:
                if self._place_single_order(symbol, "Buy", order_size, price):
                    orders_placed += 1
            else:
                print(f"⚠️ Недостаточно USDT для Buy ордера по {price:.1f}")
        return orders_placed

    def _place_sell_orders(self, symbol, order_size, sell_prices, btc_balance):
        """📤 РАЗМЕЩЕНИЕ ОРДЕРОВ НА ПРОДАЖУ"""
        orders_placed = 0
        for price in sell_prices:
            if btc_balance > order_size:
                if self._place_single_order(symbol, "Sell", order_size, price):
                    orders_placed += 1
            else:
                print(f"⚠️ Недостаточно BTC для Sell ордера по {price:.1f}")
        return orders_placed

    def _place_single_order(self, symbol, side, order_size, price):
        """🔄 РАЗМЕЩЕНИЕ ОДНОГО ОРДЕРА"""
        try:
            order = self.api_client.place_order(
                symbol=symbol,
                side=side,
                order_type="Limit",
                qty=order_size,
                price=price,
                time_in_force="GTC"
            )
            if order and 'result' in order and 'orderId' in order['result']:
                order_id = order['result']['orderId']
                self.active_order_ids.append(order_id)
                self.total_orders_created += 1
                # Учет комиссии
                commission = self.calculate_commission(order_size, price, side.upper())
                self.total_commission += commission
                print(f"✅ {side} ордер: {order_size} BTC по {price:.1f}")
                return True
            print(f"❌ Ошибка размещения {side} ордера")
            return False
        except (ConnectionError, TimeoutError, ValueError,
                TypeError, KeyError) as e:
            print(f"❌ Ошибка {side} ордера: {e}")
            return False

    def _print_order_statistics(self, orders_placed):
        """📊 ВЫВОД СТАТИСТИКИ ОРДЕРОВ"""
        print(f"📊 Размещено ордеров: {orders_placed}")
        print(f"📈 Всего ордеров создано: {self.total_orders_created}")

    def cancel_all_orders(self, symbol):
        """🛑 ОТМЕНА ВСЕХ ОРДЕРОВ"""
        try:
            self.api_client.cancel_all_orders(symbol)
            self.active_order_ids = []
            print("✅ Все ордера отменены")
            return True
        except (ConnectionError, TimeoutError, ValueError,
                TypeError, KeyError) as e:
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
        except (ConnectionError, TimeoutError, ValueError,
                TypeError, KeyError) as e:
            print(f"❌ Ошибка получения активных ордеров: {e}")
            return 0

    def calculate_commission(self, order_size, price, _side):
        """💸 РАСЧЕТ КОМИССИИ ЗА СДЕЛКУ"""
        commission_rate = 0.001  # 0.1% комиссия
        order_value = order_size * price
        commission = order_value * commission_rate
        # Логируем тип ордера для отладки (опционально)
        # print(f"💸 Комиссия для {side} ордера: {commission:.6f} USDT")
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
