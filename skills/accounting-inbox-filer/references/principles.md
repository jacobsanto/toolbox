# The 7 Principles

Every rule in this skill traces back to one of these. When a new edge case shows up and
you're tempted to improvise a fix, check it against this list first — the right answer is
usually already implied by one of them.

| # | Principle | What it means in practice |
|---|---|---|
| 1 | Determinism | The AI reads the document. The *system* decides, via explicit rules. Same file in → same result out, every time. |
| 2 | No guessing | Anything not solved by an explicit rule goes to a review folder for a human. Never "this is probably it." |
| 3 | No silent failure | Every file ends up in a visible, logged state. Nothing disappears. |
| 4 | Move-only | Never copy, never permanently delete. One file, one location at a time. |
| 5 | One tree | No parallel filing system, ever again. |
| 6 | Location is state | The folder a file sits in tells you what happened to it — you shouldn't need a database to know. |
| 7 | Progress lives in the Drive | If processing gets interrupted (session limit, crash, whatever), the next run picks up exactly where it left off, with nothing lost. |

A higher REVIEW rate is not a failure of the system — it's the system working correctly.
The goal was never "zero mistakes." It's "every mistake gets caught before it leaves the
system," which is a very different, and achievable, bar.
