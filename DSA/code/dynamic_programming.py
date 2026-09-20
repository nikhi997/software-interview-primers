"""
Chapter 14 — Dynamic programming: the same problem three ways, plus coin change.
Run:  python3 dynamic_programming.py
"""
import functools
import time


def fibonacci_brute_force(n):
    if n <= 1:
        return n
    return fibonacci_brute_force(n - 1) + fibonacci_brute_force(n - 2)   # O(2^n)


def fibonacci_top_down(n, cache=None):
    """Top-down: the same recursion, but remember each answer the first time."""
    if cache is None:
        cache = {}
    if n <= 1:
        return n
    if n in cache:
        return cache[n]
    cache[n] = fibonacci_top_down(n - 1, cache) + fibonacci_top_down(n - 2, cache)
    return cache[n]


# The shortcut: the same idea in one decorator — a built-in cache on a pure function.
@functools.lru_cache(None)
def fibonacci_top_down_cached(n):
    if n <= 1:
        return n
    return fibonacci_top_down_cached(n - 1) + fibonacci_top_down_cached(n - 2)


def fibonacci_bottom_up(n):
    """Bottom-up: fill the smallest answers first and build toward n."""
    if n <= 1:
        return n
    table = [0] * (n + 1)
    table[1] = 1
    for index in range(2, n + 1):
        table[index] = table[index - 1] + table[index - 2]
    return table[n]


def fewest_coins_for_topdown(coins, amount):
    """Top-down: the natural recursion, memoized. Same answer as the table version."""
    @functools.lru_cache(maxsize=None)
    def fewest(remaining):
        if remaining == 0:
            return 0                                    # base: 0 coins make amount 0
        if remaining < 0:
            return float("inf")                         # this path overshot -- dead end
        best = float("inf")
        for coin in coins:
            best = min(best, 1 + fewest(remaining - coin))
        return best
    result = fewest(amount)
    return result if result != float("inf") else -1


def fewest_coins_for(coins, amount):
    """Fewest coins that add up to `amount`, or -1 if no combination works."""
    unreachable = float("inf")
    fewest = [unreachable] * (amount + 1)
    fewest[0] = 0                                       # zero coins make amount 0
    for current_amount in range(1, amount + 1):
        for coin in coins:
            if coin <= current_amount:
                using_this_coin = fewest[current_amount - coin] + 1
                fewest[current_amount] = min(fewest[current_amount], using_this_coin)
    if fewest[amount] == unreachable:
        return -1
    return fewest[amount]


if __name__ == "__main__":
    n = 30
    started = time.time()
    print(f"fibonacci_brute_force({n}) =", fibonacci_brute_force(n), f"({time.time() - started:.3f}s, O(2^n))")
    started = time.time()
    print(f"fibonacci_top_down({n})   =", fibonacci_top_down(n), f"({time.time() - started:.6f}s, O(n))")
    print(f"fibonacci_bottom_up({n})  =", fibonacci_bottom_up(n), "(O(n) time, O(n) space)")
    print("fewest_coins_for_topdown([1,2,5], 11) =", fewest_coins_for_topdown([1, 2, 5], 11))   # 3  (5+5+1)
    print("fewest_coins_for([1,2,5], 11) =", fewest_coins_for([1, 2, 5], 11))   # 3  (5+5+1)
    print("fewest_coins_for([2], 3) =", fewest_coins_for([2], 3))               # -1
