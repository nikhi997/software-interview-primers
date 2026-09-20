# Chapter 6: Memory — stack, heap, and leaks — Try it

*Answers for the Try it questions in [ch6-os.md](../2-operating-systems/ch6-os.md).*

1. Fill in the contrast: stack vs heap on speed, management, lifetime, and what holds what.


2. What is a stack overflow, and what common programming mistake causes it?


3. Explain garbage collection using the idea of "reachability." What gets collected and what doesn't?


4. Your Java service's memory climbs all day and the box OOM-crashes every night, yet it's garbage collected. How is that possible, and where would you look?


5. Give a concrete code pattern that causes a memory leak in a GC language.


6. You pass a list to a function and the function appends to it; the caller sees the change. You pass an integer and increment it; the caller doesn't. Explain why in terms of value vs reference.
