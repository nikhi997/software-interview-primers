"""
Chapter 4 — Sliding window: fixed and variable size.
Run:  python3 sliding_window.py
"""


def highest_window_sum(nums, k):
    window_sum = sum(nums[:k])
    max_sum = window_sum
    for entering in range(k, len(nums)):
        window_sum += nums[entering] - nums[entering - k]   # add entering, drop leaving
        max_sum = max(max_sum, window_sum)
    return max_sum


def longest_substring_without_repeat(text):
    seen = set()
    left = 0
    longest = 0
    for right in range(len(text)):
        while text[right] in seen:    # shrink from the left until the repeat is gone
            seen.remove(text[left])
            left += 1
        seen.add(text[right])
        longest = max(longest, right - left + 1)
    return longest


if __name__ == "__main__":
    print("highest_window_sum([2,1,5,1,3,2], 3) =", highest_window_sum([2, 1, 5, 1, 3, 2], 3))
    print("longest_substring_without_repeat('abcabcbb') =", longest_substring_without_repeat("abcabcbb"))
    print("longest_substring_without_repeat('bbbbb') =", longest_substring_without_repeat("bbbbb"))
    print("longest_substring_without_repeat('pwwkew') =", longest_substring_without_repeat("pwwkew"))
