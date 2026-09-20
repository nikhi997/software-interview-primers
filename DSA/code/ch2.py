from collections import Counter


def two_sum(nums,target):
    seen = {}
    for index, num in enumerate(nums):
        complement = target-num
        if complement in seen:
            return [seen[complement], index]
        seen[num] = index
    return []

def most_common_char(word):
    counts ={}
    for char in word:
        if char in counts:
            counts[char] += 1
        else:
            counts[char] = 1

    best_char, best_count = None, 0
    for char, count in counts.items():
        if count > best_count:
            best_char, best_count = char, count
    return best_char

def most_common_character(word):
    counts = Counter(word)
    char, count = counts.most_common(1)[0]
    return char
