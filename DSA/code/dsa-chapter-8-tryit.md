# Chapter 8: When pointers branch — trees and traversal — Try it

*Answers for the Try it questions in [dsa-chapter-8.md](../dsa-chapter-8.md).*

1. *Invert a Binary Tree:* swap every node's left and right child. One line of recursion plus a base case — write it.



2. *Diameter of a Binary Tree:* the longest path between any two nodes. (Hint: at each node, the path *through* it is `leftHeight + rightHeight`; track a global max while returning height.)



3. *Binary Tree Right Side View:* the values visible from the right. BFS, and take the last node of each level — why the last?



4. *Validate a BST:* return whether a tree is a valid binary search tree. What contract should your recursion return so you can verify it in one pass?



5. State, in one sentence each, what `solve(node)` returns for: max depth, is-balanced, and diameter.
