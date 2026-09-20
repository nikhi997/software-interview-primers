# Chapter 2: Trading space for time — Try it

*Answers for the Try it questions in [dsa-chapter-2.md](../dsa-chapter-2.md).*

1. *Contains Duplicate within distance k:* given `nums` and `k`, return True if there are two equal values whose indices differ by at most `k`. State the brute force and its Big-O, then remove the waste with a hash structure. (Hint: a set of the last `k` values, or a map of value→last index.)

def contains_duplicate_at_distance_K_brute(nums,k):
    for i in range(len(nums)):
        for j in range(k,len(nums)):
            if nums[i]== nums[j]:
                return True
    return False
Big-O: O(n*k) time, O(1) space

def contains_duplicate_at_distance_k_hash(nums,k):
    seen = {}
    for index, num in enumerate(nums):
        if num in seen and index-seen[num] <=k:
            return True
        seen[num]= index
    return False
Big-O: O(n) time, O(n) space


2. *Valid Anagram:* are two strings anagrams? Solve it two ways — sorting, and a count map — and compare their complexities.

def are_anagrams_sorting(string1, string2):
    return sorted(string1) == sorted(string2)

Big-O: O(n log n) time, O(n) space

def are_anagrams_using_count_map(string1, string2):
    if len(string1) != len(string2):
        return False
    count_map1 = {}
    count_map2 = {}
    for char in string1:
        count_map1[char] = count_map1.get(char, 0) +1
    for char in string2:
        count_map2[char] = count_map2.get(char, 0) +1
    return count_map1 == count_map2

3. *First Unique Character:* return the index of the first non-repeating character in a string. Which of the three hash-map shapes is this?

def first_unique_char(string):
    count_map ={}
    for char in string:
        count_map[char] =count_map.get(char,0)+1
    for index, char in enumerate(string):
        if count_map[char] == 1:
            return index
    return -1
This is a key→count map.

4. Explain in one sentence why two-sum on a *sorted* array doesn't need a hash map at all. (You'll prove it next chapter.)
Because a hash map exists to answer "have I already seen the complement?" without scanning, and in a sorted array we don't need to remember — the ordering tells us exactly where to look, so two pointers can find the pair directly.

5. What's the space cost of the hash-map two-sum, and when might an interviewer push you to avoid it?
space cost is O(n) for hash map and interviewer would push to avoid it when the input is sorted or when space is a constraint and we can use two pointers instead.
