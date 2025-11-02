# thread_safe.py
import threading
from functools import wraps
from typing import Any, Callable
import logging

class ThreadSafeManager:
    def __init__(self):
        self.main_lock = threading.RLock()  # Reentrant lock для гибкости
        self.order_lock = threading.Lock()  # Отдельный lock для ордеров
        self.trade_lock = threading.Lock()  # Lock для trade данных
        self.logger = logging.getLogger(__name__)
    
    def synchronized(self, lock_attr: str = 'main_lock'):
        """Декоратор для синхронизации методов"""
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(self, *args, **kwargs) -> Any:
                lock = getattr(self.thread_safe, lock_attr)
                with lock:
                    return func(self, *args, **kwargs)
            return wrapper
        return decorator

class AtomicCounter:
    """Потокобезопасный счетчик"""
    def __init__(self, initial_value: int = 0):
        self._value = initial_value
        self._lock = threading.Lock()
    
    def increment(self, amount: int = 1) -> int:
        with self._lock:
            self._value += amount
            return self._value
    
    def decrement(self, amount: int = 1) -> int:
        with self._lock:
            self._value -= amount
            return self._value
    
    @property
    def value(self) -> int:
        with self._lock:
            return self._value

# Thread-safe коллекции
class SafeList:
    def __init__(self):
        self._items = []
        self._lock = threading.RLock()
    
    def append(self, item):
        with self._lock:
            self._items.append(item)
    
    def remove(self, item):
        with self._lock:
            self._items.remove(item)
    
    def clear(self):
        with self._lock:
            self._items.clear()
    
    def __len__(self):
        with self._lock:
            return len(self._items)
    
    def __getitem__(self, index):
        with self._lock:
            return self._items[index]
    
    def copy(self):
        with self._lock:
            return self._items.copy()
