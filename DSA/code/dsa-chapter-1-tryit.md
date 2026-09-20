# Chapter 1: How slow is slow? — Try it

*Answers for the Try it questions in [dsa-chapter-1.md](../dsa-chapter-1.md).*

1. State the time and space complexity of each, in your own words:
   - a single loop summing a list -  O(n) time and O(1) space for s
   - two nested loops over the same list - O(n²) time and O(1) space
   - a loop that halves a number until it reaches 1 (`while n > 1: n //= 2`) - O(log n) time and O(1) space



2. For `n = 1,000,000`, roughly how many steps is `O(n)`, `O(n log n)`, and `O(n²)`? Which are feasible in an interview's "instant"?
O(n) = 1,000,000 steps
O(n log n) = 1,000,000 * log(1,000,000) ≈ 1,000,000 * 20 ≈ 20,000,000 steps
O(n²) = 1,000,000² = 1,000,000,000,000 steps


3. Write the brute-force solution to: *"given a list, does it contain any duplicate?"* State its Big-O. Then describe (don't code yet) what waste a hash set would remove and the new complexity.

Brute-force solution:
```python
def has_duplicates(nums):
    for first in range(len(nums)):
        for second in range(first + 1, len(nums)):
            if nums[first] == nums[second]:
                return True
    return False
```
Big-O: O(n²) time, O(1) space

Using a hash set would remove the repeated comparisons by storing seen elements. The new complexity would be O(n) time and O(n) space.

def has_duplicates_using_set(nums):
      seen= set()
      for num in nums:
            if num in seen:
               return True
            seen.add(num)
      return False

4. Explain "space-for-time" using the two `has_sum_pair` functions above: what extra memory did the fast version use, and what work did it buy back?

we use extra space in the form of hash set to store seen elements, which allows to see complements in O(1) time instead of scanning the entire list for each element. This trade-off reduces the time complexity from O(n²) to O(n), while using O(n) additional space for the hash set.
