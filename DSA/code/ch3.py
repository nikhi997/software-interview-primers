def two_sum_sorted_brute(nums, target):
    for first in range(len(nums)):
        for second in range(first+1, len(nums)):
            if nums[first] + nums[second] == target:
                return [first, second]
    return []

def two_sum_sorted(nums, target):
    left, right =0, len(nums)-1
    while left <right:
        pair_sum =nums[left] +nums[right]
        if pair_sum == target:
            return [left, right]
        elif pair_sum<target:
            left+=1
        else:
            right-=1
    return []

def is_palindrome(word):
    left, right = 0, len(word)-1
    while left<right:
        if word[left]== word[right]:
            left, right = left+1, right-1
        else:
            return False
    return True

def is_palindrome_recursive(word):
    if len(word) <=1:
        return True
    if word[0] != word[-1]:
        return False
    return is_palindrome_recursive(word[1:-1])

def remove_duplicates_in_place(nums):
    if not nums:
        return 0
    write = 0
    for read in range(1, len(nums)):
        if nums[read] != nums[write]:
            write += 1
            nums[write] = nums[read]
    return write + 1


# Rung 1 (naive): every triple, O(n^3) -- and it emits duplicate triples.
def three_sum_brute(nums):
    count = len(nums)
    triples = []
    for first in range(count):
        for second in range(first + 1, count):
            for third in range(second + 1, count):
                if nums[first] + nums[second] + nums[third] == 0:
                    triples.append(sorted([nums[first], nums[second], nums[third]]))
    return triples

print(three_sum_brute([-1, 0, 1, 2, -1, -4]))     # [-1, 0, 1] shows up twice


# Rung 2 (fast, still duplicating): sort + fix-anchor + two-pointer, O(n^2).
def three_sum_two_pointer(nums):
    nums.sort()
    triples = []
    for anchor in range(len(nums)):
        left, right = anchor + 1, len(nums) - 1
        while left < right:
            triple_sum = nums[anchor] + nums[left] + nums[right]
            if triple_sum == 0:
                triples.append([nums[anchor], nums[left], nums[right]])
                left += 1
                right -= 1
            elif triple_sum < 0:
                left += 1
            else:
                right -= 1
    return triples

print(three_sum_two_pointer([-1, 0, 1, 2, -1, -4]))   # duplicates are still here


# Rung 3 (patch): dump every triple into a set so copies collapse.
def three_sum_dedup_with_set(nums):
    nums.sort()
    triples = set()
    for anchor in range(len(nums)):
        left, right = anchor + 1, len(nums) - 1
        while left < right:
            triple_sum = nums[anchor] + nums[left] + nums[right]
            if triple_sum == 0:
                triples.add((nums[anchor], nums[left], nums[right]))
                left += 1
                right -= 1
            elif triple_sum < 0:
                left += 1
            else:
                right -= 1
    return [list(triple) for triple in triples]

print(three_sum_dedup_with_set([-1, 0, 1, 2, -1, -4]))


# Rung 4 (optimized): never generate a repeat, so no set is needed. O(1) extra space.
def three_sum(nums):
    nums.sort()
    triples = []
    for anchor in range(len(nums)):
        if anchor > 0 and nums[anchor] == nums[anchor - 1]:
            continue                                      # this anchor value already did its work
        left, right = anchor + 1, len(nums) - 1
        while left < right:
            triple_sum = nums[anchor] + nums[left] + nums[right]
            if triple_sum == 0:
                triples.append([nums[anchor], nums[left], nums[right]])
                left += 1
                while left < right and nums[left] == nums[left - 1]:
                    left += 1                             # skip repeated left values
            elif triple_sum < 0:
                left += 1
            else:
                right -= 1
    return triples

print(three_sum([-1, 0, 1, 2, -1, -4]))
