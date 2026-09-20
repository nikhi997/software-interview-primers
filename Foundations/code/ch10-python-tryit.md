# Chapter 10: The Python you're assumed to know — data and iteration — Try it

*Answers for the Try it questions in [ch10-python.md](../4-putting-it-together/ch10-python.md).*

1. You have a loop that starts with an empty `result` list, walks `users`, and for each `u` that is `u.active` appends `u.email.lower()`. Rewrite it as a single comprehension — then say when you'd *refuse* to collapse a loop this way.


2. You have a 50 GB log file and need the count of lines containing `"ERROR"`. Write it so memory stays flat regardless of file size. Which idiom makes that possible, and what would the naive version do?


3. Build a dict that maps each value in `nums` to its index in one line. Then clamp a list of numbers so negatives become `0` — and explain why one `if` goes at the *end* of the comprehension and the other goes in the *middle*.


4. Write a `rows × cols` grid of zeros you can safely mutate one cell of. Show the version that *looks* right but corrupts every row, and explain in one sentence why it breaks.


5. A function returns `(min(nums), max(nums))`. Show how the caller names both results without indexing, and give the one-line swap `a, b = b, a` — what makes both work?


6. You're grouping a list of `(department, employee)` pairs into `{department: [employees]}`. Show the `defaultdict` version and explain what bookkeeping line it removes versus a plain dict.
