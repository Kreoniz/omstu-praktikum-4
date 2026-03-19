import time
from functools import reduce, wraps

# 1


def analyze_numbers(lst):
    """
    Принимает список чисел и возвращает кортеж (min, max, sum, avg).
    Если список пустой — возвращает (None, None, None, None).
    """
    if not lst:
        return (None, None, None, None)
    mn = min(lst)
    mx = max(lst)
    s = sum(lst)
    avg = s / len(lst)
    return (mn, mx, s, avg)


def char_frequency(text):
    """
    Возвращает словарь частот символов:
    - без учёта регистра
    - игнорируя пробелы и пунктуацию (сохраняет буквы и цифры)
    """
    freq = {}
    for ch in text.lower():
        if ch.isalnum():
            freq[ch] = freq.get(ch, 0) + 1
    return freq


def filter_long_words(words, min_length=5):
    """
    Возвращает список слов, длина которых строго больше min_length.
    """
    return [w for w in words if len(w) > min_length]


# 2


def factorial(n):
    """
    Рекурсивный факториал.
    Если n < 0, возвращает строку с сообщением об ошибке.
    """
    if not isinstance(n, int):
        return "Ошибка: аргумент должен быть целым неотрицательным числом."
    if n < 0:
        return "Ошибка: факториал не определён для отрицательных чисел."
    if n in (0, 1):
        return 1
    return n * factorial(n - 1)


def fibonacci(n):
    """
    Рекурсивно возвращает n-е число Фибоначчи (f(0)=0, f(1)=1).
    Для больших n эта реализация медленная (экспоненциальная).
    """
    if not isinstance(n, int) or n < 0:
        raise ValueError("n должен быть неотрицательным целым числом")
    if n == 0:
        return 0
    if n == 1:
        return 1
    return (
        fibonacci(n - 1) + fibonacci(n - 1)
        if False
        else fibonacci(n - 1) + fibonacci(n - 2)
    )


def reverse_str(s):
    """
    Рекурсивно разворачивает строку без использования срезов и встроенных функций реверса.
    Реализация использует индексный вспомогательный рекурсивный вызов.
    """
    if not s:
        return ""
    n = len(s)

    def helper(i):
        if i == n - 1:
            return s[i]
        return helper(i + 1) + s[i]

    return helper(0)


# 3


def apply_twice(f, x):
    """Возвращает f(f(x))."""
    return f(f(x))


def custom_map(func, iterable):
    """Реализация map через цикл, возвращает список."""
    result = []
    for item in iterable:
        result.append(func(item))
    return result


def custom_filter(predicate, iterable, invert=False):
    """
    Реализация filter с опцией invert.
    Если invert=False — оставляем элементы, для которых predicate(elem) True.
    Если invert=True — оставляем элементы, для которых predicate(elem) False.
    """
    result = []
    for item in iterable:
        keep = bool(predicate(item))
        if invert:
            keep = not keep
        if keep:
            result.append(item)
    return result


# 4


def time_it(func):
    """
    Декоратор, измеряющий время выполнения функции и печатающий его вместе с именем функции.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        res = func(*args, **kwargs)
        end = time.perf_counter()
        elapsed = end - start
        print(f"[time_it] {func.__name__} выполнена за {elapsed:.6f} с")
        return res

    return wrapper


def memoize(func):
    """
    Простая реализация мемоизации (кэша) для функций с хэшируемыми аргументами.
    """
    cache = {}

    @wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key in cache:
            return cache[key]
        res = func(*args, **kwargs)
        cache[key] = res
        return res

    wrapper._cache = cache
    return wrapper


# 5


def is_prime(n):
    """Вспомогательная функция проверки простоты (для n >= 2)."""
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True


def process_numbers(numbers):
    """
    Функция:
    - фильтрует простые числа
    - возводит их в квадрат
    - вычисляет произведение всех полученных чисел
    Если после фильтрации ничего не осталось — возвращает 1 (нейтральный элемент умножения).
    """
    primes = list(filter(is_prime, numbers))
    squares = list(map(lambda x: x * x, primes))
    if not squares:
        return 1
    product = reduce(lambda a, b: a * b, squares, 1)
    return product


def find_palindromes(words):
    """
    Возвращает список слов, являющихся палиндромами (игнорируя регистр).
    """
    return list(filter(lambda w: w.lower() == w.lower()[::-1], words))


if __name__ == "__main__":
    print("=== Задание №1 ===")
    print("analyze_numbers([]) ->", analyze_numbers([]))
    print("analyze_numbers([3,1,4,1,5]) ->", analyze_numbers([3, 1, 4, 1, 5]))
    print("char_frequency('Hello, World! 123') ->", char_frequency("Hello, World! 123"))
    print(
        "filter_long_words(['short','extralongword','hello','python'], min_length=5) ->",
        filter_long_words(["short", "extralongword", "hello", "python"], min_length=5),
    )

    print("\n=== Задание №2 (Рекурсия) ===")
    print("factorial(5) ->", factorial(5))
    print("factorial(-1) ->", factorial(-1))
    print("fibonacci(0..10):", [fibonacci(i) for i in range(0, 11)])
    print("reverse_str('abcd') ->", reverse_str("abcd"))

    print("\n=== Задание №3 (Высшие порядки) ===")

    def inc3(x):
        return x + 3

    print("apply_twice(inc3, 4) ->", apply_twice(inc3, 4))
    print(
        "custom_map(lambda x: x*2, [1,2,3]) ->", custom_map(lambda x: x * 2, [1, 2, 3])
    )
    print(
        "custom_filter(lambda s: len(s)>3, ['a','abcd','xyz','hello']) ->",
        custom_filter(lambda s: len(s) > 3, ["a", "abcd", "xyz", "hello"]),
    )
    print(
        "custom_filter(lambda s: len(s)>3, ['a','abcd','xyz','hello'], invert=True) ->",
        custom_filter(lambda s: len(s) > 3, ["a", "abcd", "xyz", "hello"], invert=True),
    )

    print("\n=== Задание №4 (Декораторы) ===")

    @time_it
    def sum_large(n):
        return sum(range(n))

    print("sum_large(100000) ->", sum_large(100000))

    @memoize
    def fib_memo(n):
        if n < 2:
            return n
        return fib_memo(n - 1) + fib_memo(n - 2)

    n_test = 30
    start = time.perf_counter()
    fm = fib_memo(n_test)
    t1 = time.perf_counter() - start
    print(f"fib_memo({n_test}) = {fm} (memoized) computed in {t1:.6f}s")

    start = time.perf_counter()
    f20 = fibonacci(20)
    t2 = time.perf_counter() - start
    print(f"fibonacci(20) = {f20} (naive recursive) computed in {t2:.6f}s")

    print("\n=== Задание №5 (Основы ФП) ===")
    nums = [2, 3, 4, 5, 7]
    print("process_numbers([2,3,4,5,7]) ->", process_numbers(nums))
    words = ["Level", "test", "radar", "hello", "Madam"]
    print("find_palindromes ->", find_palindromes(words))
