# Chapter 3: Walking from both ends — Try it

*Answers for the Try it questions in [dsa-chapter-3.md](../dsa-chapter-3.md).*

1. *Valid Palindrome (alphanumeric only):* check if a string reads the same forwards and backwards, ignoring non-letters and case. Use opposite-end pointers.


def is_palindrome(string):
    left, right = 0, len(string) - 1
    while left < right:
        while left < right and not string[left].isalnum():
            left += 1
        while left < right and not string[right].isalnum():
            right -= 1

        if string[left].lower() != string[right].lower():
            return False

        left += 1
        right -= 1

    return True

def _is_palindrome(string):
    left, right = 0, len(string)-1
    while left< right:
       if string[left]== string[right]:
              left+=1
              right-=1
         else:
              return False
    return True

2. *Move Zeroes:* push all zeros to the end of an array in place, keeping the order of non-zeros. Which flavor (slow/fast or converging)?

slow/fast pointer: the slow pointer tracks where the next non-zero should go, and the fast pointer scans through the array.

```python
def move_zeroes(nums):
    slow = 0
    for fast in range(len(nums)):
        if nums[fast] != 0:
            nums[slow], nums[fast] = nums[fast], nums[slow]
            slow += 1
    return nums


3. *Container With Most Water:* given heights, two lines form a container; maximize the water area. Start with pointers at both ends — which one do you move, and why? (Hint: move the *shorter* line inward.)

```python
def max_area(height):
    left, right = 0, len(height)-1
    max_area =0
    while left <right:
        width =right - left
        current_area = min(height[left], height[right]) * width
        max_area = max(max_area, current_area)
        if height[left] < height[right]:
            left +=1
        else:
            right -=1
    return max_area


4. State the exact tradeoff between the hash-map and two-pointer solutions to pair-sum, in terms of both time and space, including the cost of sorting.
The hash-map solution is O(n) time and O(n) space, while the two-pointer solution is O(n) time and O(1) space, but requires sorting the input array first, which takes O(n log n) time. Therefore, the two-pointer solution is more space-efficient but may be slower due to the sorting step, especially for large datasets.


5. Why does two pointers *require* sorted (or monotonic) data to be correct? What breaks if the array is unsorted?

Because it relies on the order of the elements to make decisions about which pointer to move. if unsorted ,comparison wouldnt give information about the other pointer's position, leading to incorrect results.

def two_sum_sorted_brute(nums, target):
    for first in range (len(nums)):
        for second in range(first+1, len(nums)):
            if nums[first] + nums[second] == target:
                return [first, second]
    return []

def two_sum_sorted_two_pointers(nums,target):
    left , right = 0, len(nums)-1
    while left< right:
        current_sum = nums[left] +nums[right]
        if current_sum == target:
            return [left, right]
        elif current_sum<target:
            left+=1
        else:
            right-=1
    return []


def two_sum_sorted_all_pairs(nums, target):
    left, right = 0, len(nums) - 1
    pairs = []

    while left < right:
        s = nums[left] + nums[right]

        if s == target:
            pairs.append((left, right))
            left += 1
            right -= 1

            while left < right and nums[left] == nums[left - 1]:
                left += 1
            while left < right and nums[right] == nums[right + 1]:
                right -= 1

        elif s < target:
            left += 1
        else:
            right -= 1

    return pairs


def two_sum_sorted_all_pairs(nums, target):
    left, right = 0, len(nums) - 1
    pairs = []
    while left < right:
        current_sum = nums[left] + nums[right]
        if current_sum == target:
            pairs.append([nums[left], nums[right]])
            left += 1
            right -= 1
            while left < right:                   # skip duplicate lefts
                if nums[left] == nums[left - 1]:
                    left += 1
                else:
                    break
            while left < right:                   # skip duplicate rights
                if nums[right] == nums[right + 1]:
                    right -= 1
                else:
                    break
        elif current_sum < target:
            left += 1
        else:
            right -= 1
    return pairs

def remove_duplicates(nums):
    if not nums:
        return 0
    write_index = 1
    for read_index in range(1, len(nums)):
        if nums[read_index] != nums[write_index - 1]:
            nums[write_index] = nums[read_index]
            write_index += 1
    return write_index

def three_sum_brute(nums):
    count = len(nums)
    triples = set()
    for first in range(count):
        for second in range(first+1, count):
            for third in range(second+1, count):
                if nums[first] +nums[second] + nums[third] ==0:
                    triple = tuple(sorted([nums[first], nums[second], nums[third]]))
                    triples.add(triple)
    return [list(triple) for triple in triples]

def three_sum(nums):
    nums.sort()
    triples = []
    for anchor in range(len(nums)):
        if anchor > 0 and nums[anchor] == nums[anchor-1]:
            continue
        left, right = anchor+1, len(nums)-1
        while left<right:
            triple_sum = nums[anchor]>
