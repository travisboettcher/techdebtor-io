---
title: "Building It With Itself"
date: 2026-11-22
draft: true
tags: ["AI", "Claude Code"]
summary: "I had Claude build the agent loop with a hand-run version of the loop, and its reviewer found that my human gate was only a sentence."
---

*Part 2 of a series on building an agent graph that learns from its mistakes.* [Part 1](/posts/the-missing-loop/)

[Last time](/posts/the-missing-loop/) I described a design: a tech-lead agent that records what went wrong in every run, and a retro that turns recurring mistakes into rules. The obvious way to test that plan was to build it with itself - or with a hand-run version of itself, since the real one didn't exist yet.

### Where it lives

The first decision wasn't about agents. Claude's first scoping was a marketplace for just this one framework, named after me. I wanted something else: a general marketplace for any reusable Claude Code plugins I end up writing, with this framework as the first one, under the techdebtor name. So it became [techdebtor-plugins](https://github.com/travisboettcher/techdebtor-plugins), and the marketplace is called `techdebtor`.

Both corrections went into the run record as findings, `scope-mismatch` and `naming`, caught by "human". I liked that the record opened with me changing my mind. It's for every mistake, including mine.

### Contract first

Claude acted as the tech lead for the build, and the first commit (at 05:48 on a Saturday, for the record) was a marketplace skeleton and a design contract: `DESIGN.md`, 111 lines covering the run record, the rules ledger, the promotion ladder and the human gate. No code yet.

Same move that worked for [`hll`](/posts/designing-a-language-for-a-machine-to-write/): say what the thing must do before anyone writes it, so the checking has something to check against.

With the contract in place, two implementer agents built the two halves in parallel: `lead`, the skill that runs the graph, and `retro`, the half that mines transcripts and run records for mistakes. The retro half arrived as about 2,000 lines, most of it a 919-line miner script and its tests. Both implementers reported gaps in the contract along the way, and the lead then merged the two into a single plugin, `agent-loop`, with the contract moved inside it so it ships with the code.

Then came a tester agent and a reviewer agent, and the rule that made the whole thing worth doing: the reviewer gets the diff and the acceptance criteria and nothing else. It never sees the implementers' reasoning. Three rounds at most, then it's done or it's my problem.

### What the reviewer caught

The first build ended with 18 findings. Here are the ones I keep thinking about.

**Secrets got through, twice.** The miner redacts session transcripts before reporting on them. The reviewer found tokens glued to an underscore, short prefixed tokens, and credentials on the command line passing straight through. Fixed. On the next pass it found credentials glued to `-u` (as in `curl -ualice:pw`) and quoted passwords with spaces still leaking. Two `redaction-gap` findings in one build, the second one *after* the fix for the first.

**A quote that hid a whole file.** The miner parses a small subset of YAML itself. An escaped quote followed by a `#` made it treat the rest of the line as a comment, and that made the entire run record unparseable. The nasty part: its findings silently vanished from ledger verification. A bug in the thing that checks whether rules work, hiding the evidence of whether rules work.

**A minute for 40 KB.** One redaction pattern started a fresh scan at every word boundary inside a long run of identifier characters. Feed it 40 KB of `ab.cd-` repeated and it took about a minute. Nobody had asked for a test like that. After the fix, every pattern starts its scan only at a fixed anchor, and 200 KB of adversarial input runs in under 0.3 seconds.

**The human gate was prose.** This one changed how I think about the project. The human gate from part 1 was written into the retro skill's instructions, in plain English. Meanwhile the same skill pre-approved `Write`, `Edit` and every `git` command, so writes and commits would never have reached a permission prompt. The gate was a sentence asking the agent to please stop.

It didn't stop at one. Removing that left a pre-approval for the miner script by a wildcard path, which would also have pre-approved a script of the same name planted in any repo I cloned. (That one wasn't the reviewer's catch; the record marks it `self`.) And the "read-only" `git diff`, `git log` and `git show` patterns allowed `--output=`, which writes files. Three separate `over-broad-pre-approval` findings in one build. The fix in each case was to pre-approve less and let the permission prompt do its job, because the prompt is the one gate an agent can't talk its way past.

### The lead's mistakes count too

The lead wrote the contract, and the contract had gaps (no outcome for "finished but not merged", no place to put rejected findings) and one outright self-contradiction: it defined `stage` as where a mistake was *made*, then its own example recorded review findings as stage `review`. The reviewer caught that one. When the lead fixed the miner's pre-approval itself, it left the contract and skill still claiming the miner was pre-approved - `doc-drift`, also caught by the reviewer.

The record's notes say it plainly: the plan-stage and doc-drift findings are the lead's own. Better that than a lead grading its own homework kindly.

### Four proposals and a point release

Two categories in those 18 findings came up more than once: `over-broad-pre-approval` three times and `redaction-gap` twice. That's exactly the signal the retro is meant to look for, so before the retro existed in working form, the lead wrote four framework proposals by hand:

- add values to `caught_by` for an implementer or the lead catching someone else's mistake (an implementer finding a hole in the contract had nowhere to go but "self");
- give the reviewer a standing least-privilege check for any diff that touches permissions;
- require a list of adversarial inputs - glued, quoted, prefixed, split, oversized, malformed - as acceptance criteria for anything handling untrusted input;
- have the tester time any new regex on long adversarial strings, since it was the reviewer, not the tester, that found the slow one.

All four went into [PR 2](https://github.com/travisboettcher/techdebtor-plugins/pull/2), agent-loop 0.1.1, along with CI. The last commit for it landed at 06:48, an hour after the contract. PR 2 was built with the graph too, and its reviewer applied the brand-new least-privilege check to the new CI workflow. It found nothing blocking, and three minor things, one of which is my favourite kind of irony: the example timing command for catching slow regexes had no time limit, so a truly slow regex would have hung the tester.

### Why the reviewer doesn't get the reasoning

The rule I'd keep if I could only keep one is the reviewer being independent - criteria and diff in, verdict out, no implementer reasoning. The design doc now says why in one line: the trap is green checks that share the code's own wrong assumptions.

An implementer who believes a redaction pattern covers `curl -u` will write a test that agrees with it. Show the reviewer that reasoning and it starts reading the code through the same belief, and now two agents are confident about the same gap. Every reviewer catch above came from an agent that didn't know what the implementer thought it had done, so it had to look at what the code actually did.

The reviewer is still Claude, with the same blind spots; independence only stops it being talked into believing what the implementer believed. Whether one reviewer is enough is another question, and the answer turned out to be a swarm of specialists. That's part 3.

---

*This post was written with the help of Claude. Some of the mistakes in it are Claude's own, quoted from the run record that caught them.*
