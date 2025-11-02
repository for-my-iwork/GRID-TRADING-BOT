# thread_safe.py
"""
Thread-safe примитивы для многопоточной работы
"""

import threading
from typing import Any, List, Dict
from functools import wraps

class ThreadSafeManager:
    """Менеджер потокобезопасности"""
    
    def __init__(self):
        self._lock = threading.RLock()
        
    def synchronized(self, func):
        """Декоратор для синхронизации методов"""
        @wraps(func)
        def wrapper(*args, **kwargs):
            with self._lock:
                return func(*args, **kwargs)
        return wrapper

class SafeList:
    """Потокобезопасный список"""
    
    def __init__(self):
        self._lock = threading.RLock()
        self._data: List[Any] = []
        
    def append(self, item: Any):
        with self._lock:
            self._data.append(item)
            
    def extend(self, items: List[Any]):
        with self._lock:
            self._data.extend(items)
            
    def pop(self, index: int = -1) -> Any:
        with self._lock:
            return self._data.pop(index)
            
    def clear(self):
        with self._lock:
            self._data.clear()
            
    def __getitem__(self, index: int) -> Any:
        with self._lock:
            return self._data[index]
            
    def __len__(self) -> int:
        with self._lock:
            return len(self._data)
            
    def copy(self) -> List[Any]:
        with self._lock:
            return self._data.copy()

class AtomicCounter:
    """Атомарный счетчик"""
    
    def __init__(self, initial_value: int = 0):
        self._lock = threading.RLock()
        self._value = initial_value
        
    def increment(self, amount: int = 1) -> int:
        with self._lock:
            self._value += amount
            return self._value
            
    def decrement(self, amount: int = 1) -> int:
        with self._lock:
            self._value -= amount
            return self._value
            
    def get(self) -> int:
        with self._lock:
            return self._value
            
    def set(self, value: int):
        with self._lock:
            self._value = value

class SafeDict:
    """Потокобезопасный словарь"""
    
    def __init__(self):
        self._lock = threading.RLock()
        self._data: Dict[Any, Any] = {}
        
    def get(self, key: Any, default: Any = None) -> Any:
        with self._lock:
            return self._data.get(key, default)
            
    def set(self, key: Any, value: Any):
        with self._lock:
            self._data[key] = value
            
    def delete(self, key: Any) -> bool:
        with self._lock:
            if key in self._data:
                del self._data[key]
                return True
            return False
            
    def keys(self) -> List[Any]:
        with self._lock:
            return list(self._data.keys())
            
    def values(self) -> List[Any]:
        with self._lock:
            return list(self._data.values())
            
    def items(self) -> List[tuple]:
        with self._lock:
            return list(self._data.items())
            
    def clear(self):
        with self._lock:
            self._data.clear()

# Глобальный менеджер синхронизации
sync_manager = ThreadSafeManager()

# Декоратор для синхронизации
def synchronized(func):
    return sync_manager.synchronized(func)
