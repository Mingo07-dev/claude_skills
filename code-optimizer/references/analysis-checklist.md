# Analysis checklist and output format

## Domain A: Performance and algorithmic complexity

- Nested loops where O(n log n) or O(n) is possible
- N+1 queries (loop issuing DB queries per item)
- Repeated linear lookups on non-indexed data
- Redundant expensive recalculation
- Missing memoization or caching

I/O and async:
- Sequential async work that should be parallelized
- Synchronous file I/O in high concurrency paths
- Waterfall API calls that should be batched
- Inefficient polling vs event-driven

Data structures:
- Arrays used for lookups that should be Map/Set/dict
- Unnecessary object copies vs references
- Serialization in hot paths
- String concatenation in loops (prefer join/buffer)

## Domain B: Memory leaks and resource management

Event listeners/subscriptions:
- addEventListener without remove
- Subscribe without unsubscribe
- setInterval/setTimeout without clear
- Listeners registered inside loops or repeated calls

Closures and references:
- Closures capturing large objects
- Circular references preventing GC
- Unbounded caches (no size limit or TTL)
- Global objects that grow over time

External resources:
- DB connections not closed
- File descriptors not closed
- Streams not ended on errors
- Connection pools not released

Frontend (if applicable):
- useEffect without cleanup
- State updates on unmounted components
- Refs holding detached DOM nodes
- Context providers that rerender excessively

## Domain C: Bugs and edge cases

Null and boundary cases:
- Missing null/undefined checks
- Empty arrays not handled
- Division by zero
- Counter overflow
- Float comparisons with == instead of epsilon

Error handling:
- Silent catch blocks
- Unhandled promise rejections
- Errors rethrown without stack
- Missing fallbacks

Concurrency:
- Non-atomic updates to shared state
- Race conditions in async flows
- TOCTOU on files/resources
- Missing locks in multi-threaded contexts

Input validation:
- Unsanitized user input
- Implicit assumptions about types or formats
- Unchecked ranges or indices
- Encoding/decoding issues

## Output format (write /tmp/code-analysis.md)

```
### [ID] - Problem title
Category: PERFORMANCE | MEMORY_LEAK | BUG | EDGE_CASE
Severity: CRITICAL | HIGH | MEDIUM | LOW
File: path/to/file.ext
Lines: 42-67
Impact: concrete impact (slowdown, crash, leak, wrong behavior)

Problematic code:
```lang
// snippet (5-15 lines)
```

Analysis:
[Why this is a problem]

Trigger scenario:
[When it manifests]
```

Summary at end:

```
## Analysis summary
- Total issues: N
- CRITICAL: N | HIGH: N | MEDIUM: N | LOW: N
- By category: PERFORMANCE: N | MEMORY_LEAK: N | BUG: N | EDGE_CASE: N
- Most critical files: [top 3]
```
