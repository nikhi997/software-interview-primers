# Chapter 5: Throwing away half the answers — Try it

*Answers for the Try it questions in [dsa-chapter-5.md](../dsa-chapter-5.md).*

1. *Search Insert Position:* find where a target should be inserted in a sorted array to keep it sorted. Which predicate?



2. *Find First and Last Position:* return the range of a target's occurrences in a sorted array. (Two binary searches — different predicates.)



3. *Capacity to Ship Packages in D Days:* minimum ship capacity to ship all packages within `D` days. Identify the answer range and the monotonic feasibility test — it's binary-search-on-the-answer.



4. Write out the three classic binary-search bugs and how each is avoided.



5. Explain why "minimize the maximum X" is a tell for binary search on the answer, using the Koko example's structure.


def find_brute(nums, target):
    for i in range(len(nums)):
        if nums[i] >= target:
            return i
    return -1

def find_brute(nums, target):
    for index, num in enumerate(nums):
        if num >= target:
            return index
    return -1

def find_using_binary_search(nums, target):
    left, right = 0, len(nums) - 1
    while left <= right:
        mid = (left+right)// 2
        if nums[mid] == target:
            return mid
        elif nums[mid] < target:
            left = mid + 1
        else:
            right = mid -1
    return -1
