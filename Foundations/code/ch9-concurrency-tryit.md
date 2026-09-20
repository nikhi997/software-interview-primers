# Chapter 9: Async, event loops, and the question that decides everything — Try it

*Answers for the Try it questions in [ch9-concurrency.md](../4-putting-it-together/ch9-concurrency.md).*

1. Define I/O-bound and CPU-bound, and explain why this single distinction drives your choice of concurrency tool.


2. Describe how an event loop handles thousands of connections on one thread. What makes that possible?


3. What does `await` actually do at the moment it's hit? Why does async do nothing for CPU-bound work?


4. What is a thread pool and what problem does it solve versus spawning a thread per task?


5. Explain the GIL and its consequence: for CPU-bound Python work, why won't threads help, and what do you use instead?


6. A Python web service handles many slow database calls and feels sluggish under load. Is it likely I/O- or CPU-bound, and what would you reach for? What if instead it were resizing thousands of images?
