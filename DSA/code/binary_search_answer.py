"""
Chapter 5 — Binary search on the answer (Koko eating bananas).
Run:  python3 binary_search_answer.py
"""
import math


def min_eating_speed(piles, hours_available):
    def hours_needed(speed):
        hours = 0
        for pile in piles:
            hours += math.ceil(pile / speed)
        return hours

    def can_finish(speed):
        return hours_needed(speed) <= hours_available   # faster -> fewer hours

    low, high = 1, max(piles)
    while low < high:
        mid = (low + high) // 2
        if can_finish(mid):
            high = mid           # this speed works; try slower
        else:
            low = mid + 1        # too slow to finish; must eat faster
    return low


if __name__ == "__main__":
    print("min_eating_speed([3,6,7,11], 8) =", min_eating_speed([3, 6, 7, 11], 8))
    print("min_eating_speed([30,11,23,4,20], 5) =", min_eating_speed([30, 11, 23, 4, 20], 5))
    print("min_eating_speed([30,11,23,4,20], 6) =", min_eating_speed([30, 11, 23, 4, 20], 6))
