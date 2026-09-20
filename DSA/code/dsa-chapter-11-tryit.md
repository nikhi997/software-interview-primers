# Chapter 11: Everything is a graph — BFS and DFS — Try it

*Answers for the Try it questions in [dsa-chapter-11.md](../dsa-chapter-11.md).*

1. *Number of Islands:* you have the template — what marks a cell visited, and why does that avoid a separate visited set?



2. *Clone Graph:* deep-copy a graph. (Hint: BFS/DFS while keeping a map from original node → copy, to handle cycles.)



3. *Word Ladder:* fewest one-letter transformations from one word to another, each step a valid word. Why is this BFS, and what are the nodes and edges?



4. *Rotting Oranges:* minutes until all oranges rot, spreading to neighbors each minute. Why is *multi-source* BFS the right tool? (Start with all rotten oranges in the queue.)



5. Explain precisely why BFS finds shortest paths on unweighted graphs but fails when edges have different weights.
