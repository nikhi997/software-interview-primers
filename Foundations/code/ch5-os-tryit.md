# Chapter 5: Processes, threads, and the trouble with sharing — Try it

*Answers for the Try it questions in [ch5-os.md](../2-operating-systems/ch5-os.md).*

1. State the difference between a process and a thread in one sentence, and explain why the "threads share memory" part is what makes concurrency hard.


2. Walk through how two threads running `counter += 1` can lose an update. At which step does the context switch cause the problem?


3. What's a race condition, and why are they so hard to debug compared to ordinary bugs?


4. What does a mutex do, and what's the downside of holding locks for too large a section of code?


5. Describe a deadlock with the two-lock example, then name the four conditions required for one.


6. Your service occasionally hangs under load with no error. Two locks are involved. What do you suspect, and what's the simplest design rule that would prevent it?
