# Chapter 9: Trees with rules — BST and trie — Try it

*Answers for the Try it questions in [dsa-chapter-9.md](../dsa-chapter-9.md).*

1. *Validate Binary Search Tree:* verify the BST rule holds everywhere. (Hint: pass down a valid `(low, high)` range; a node must fall inside it. Why isn't checking only immediate children enough?)



2. *Kth Smallest Element in a BST:* you've seen the iterative inorder above — explain why it stops in `O(height + k)`.



3. *Implement Trie (Insert/Search/StartsWith):* you have the template above — what's the difference between `search` and `starts_with`?



4. *Design Add and Search Words (with `.` wildcard):* support searching where `.` matches any character. Which traversal handles the wildcard branch?



5. Explain why a hash set can answer "exact word present?" but not "any word with this prefix?", and how a trie does both.
