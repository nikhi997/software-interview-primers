# Chapter 4: The window that slides instead of restarting — Try it

*Answers for the Try it questions in [dsa-chapter-4.md](../dsa-chapter-4.md).*

1. *Minimum Size Subarray Sum:* shortest contiguous subarray with sum ≥ target. Which of the three template parts differ from the "longest" version, and where does the answer update?

the three template parts that differ from the "longest" version are:
1. **What state describes the window?** A running sum of the elements in the current window.
2. **What makes it invalid?** The running sum is less than the target.
3. **What are you optimizing?** The shortest window (update right after expanding, then shrink greedily).


def min_subarray_len(target, nums):
    left = 0
    window_sum = 0
    shortest = float('inf')
    for right in range(len(nums)):
        window_sum+= nums[right]
        while window_sum >= target:
            shortest = min(shortest, right - left +1)
            window_sum -= nums[left]
            left +=1
    return shortest if shortest != float('inf') else 0


```python
def min_subarray_len(target, nums):
    left = 0
    window_sum = 0
    shortest = float('inf')
    for right in range(len(nums)):
        window_sum += nums[right]
        while window_sum >= target:          # valid now — shrink to find a shorter one
            shortest = min(shortest, right - left + 1)
            window_sum -= nums[left]
            left += 1
    return shortest if shortest != float('inf') else 0
```


2. *Longest Substring with At Most K Distinct Characters:* what's the window state, and what makes it invalid? (Hint: a char→count map; invalid when `len(map) > k`.)
the window state is a character→count map that keeps track of the number of distinct characters in the current window. The window is invalid when the number of distinct characters exceeds `k`, i.e., when `len(map) > k`.


def longest_with_k_distinct(text, k):
    counts = {}
    left = 0
    longest = 0
    for right in range(len(text)):
        entering = text[right]
        counts[entering] = counts.get(entering, 0) + 1
        while len(counts) > k:
            leaving = text[left]
            counts[leaving] -= 1
            if counts[leaving] == 0:
                del counts[leaving]
            left += 1
        longest = max(longest, right - left + 1)
    return longest




```python
def longest_with_k_distinct(text, k):
    counts = {}
    left = 0
    longest = 0
    for right in range(len(text)):
        entering = text[right]
        counts[entering] = counts.get(entering, 0) + 1
        while len(counts) > k:               # too many distinct — shrink from the left
            leaving = text[left]
            counts[leaving] -= 1
            if counts[leaving] == 0:
                del counts[leaving]
            left += 1
        longest = max(longest, right - left + 1)
    return longest
```


3. *Maximum Average Subarray (size k):* a fixed-size window. Write the slide step.
the slide step for a fixed-size window of size `k` is:
1. Add the next element to the window (expand the window to the right).
2. Remove the element that falls out of the window (shrink the window from the left).


4. Explain, in amortized terms, why the variable-window solution with a nested `while` is `O(n)` and not `O(n²)`.
because each element is added to the window once and removed from the window once, the total number of operations is proportional to the number of elements in the input array. The nested `while` loop only runs when the window is invalid, and it will only run as many times as there are elements in the array. Therefore, the overall time complexity is O(n), where n is the number of elements in the input array.


5. Why is "longest subsequence" (gaps allowed) usually *not* a sliding-window problem? What changes when the chunk doesn't have to be contiguous?
because the elements in a subsequence do not have to be contiguous, the sliding-window technique is not applicable. The sliding-window technique relies on the fact that the elements in the window are contiguous, allowing for efficient updates as the window slides. When gaps are allowed, the problem becomes more complex and often requires different techniques, such as dynamic programming or backtracking, to find the longest subsequence.



def max_sum_window(nums,k):
    window_sum =sum(nums[:k])
    max_sum = window_sum
    for i in range(k, len(nums)):
        window_sum = window_sum + nums[i] - nums[i-k]
        max_sum = max(max_sum, window_sum)
    return max_sum
