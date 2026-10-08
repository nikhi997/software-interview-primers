# Repository Guidelines

## Purpose and teaching style

- Treat this repository as an interview curriculum, not an exhaustive textbook or framework tutorial.
- Preserve the shared teaching sequence: begin with the simplest working approach, expose the specific pain, waste, bottleneck, signal, or mechanism, and only then introduce the fix.
- Prefer durable concepts and transferable reasoning over product announcements, vendor syntax, and trend-driven coverage.
- Match the conversational tone, terminology, depth, and chapter structure of adjacent material.

## Content changes

- Read the track README, adjacent chapters, appendix, and relevant companions before editing a chapter.
- Extend an existing chapter when the topic fits its learning outcome; add a chapter only when the topic needs its own progression and exercises.
- Keep track navigation, chapter counts, root documentation, appendices, glossaries, interview questions, and companion exercises consistent with content changes.
- State prerequisites, tradeoffs, failure modes, and boundaries explicitly. Do not present one design or tool as universally correct.
- Use runnable, dependency-free examples where practical. Keep code focused on the concept being taught rather than production boilerplate.

## Accuracy and freshness

- Use primary or authoritative sources for time-sensitive technical claims.
- Distinguish durable concepts from volatile implementation details. Date claims about current products, providers, model capabilities, limits, benchmarks, and APIs.
- Never invent citations, benchmark results, performance numbers, product behavior, or interview expectations.
- Avoid copying source language; explain concepts in the repository's own structure and examples and preserve required attribution.

## Validation

- Run `python3 scripts/validate_content.py` after changing Markdown, chapter structure, navigation, or Python examples.
- Fix validation failures caused by the change. Do not silently remove checks or weaken expected chapter coverage.
- Keep changes focused and preserve unrelated contributor work.
