---
title: "The Missing Loop"
date: 2026-11-22
draft: true
tags: ["AI", "Claude Code"]
summary: "A model doesn't learn from its mistakes, but the files around it can - so I set out to build the loop that writes them."
---

*Part 1 of a series on building an agent graph that learns from its mistakes.*

This one started with a phrase I'd heard secondhand: that some engineers at Anthropic work with a "self-improving graph of agents." I didn't know what that meant, and it sounded like exactly the kind of thing I'd want, so I asked Claude.

The first thing it did was decline the premise: it couldn't verify that this was anybody's best practice, and said so. What it could do was explain what the idea would have to mean - which turned out to be more useful than a citation.

### The model doesn't learn

Here's the honest version. The model doesn't get better between my sessions. If a graph of agents is going to improve itself, the improvement has to live somewhere else: in the things the next run reads before it starts. That means `CLAUDE.md`, skills, memory, hooks, tests. The scaffolding learns; the model just shows up.

The second half matters more. An improvement only sticks where something can check it. Write "don't do X" into a file and you've written a hope. Write a test that fails when X happens and you've written a fact. And without a verifier in the loop, a graph of agents doesn't improve - it agrees with itself. One agent makes a mistake, the next one reads the result and confirms it, and the mistake gets more confident with every hop.

That rang true, partly because I'd already watched it play out. The [`hll` series](/posts/designing-a-language-for-a-machine-to-write/) was mostly me learning that the loop matters more than the grammar: a compiler that answers back did more for the agents writing my homelab config than anything I put in a spec.

### Trust is the bottleneck

There's a framing I've picked up at work that helped me place this. Teams move through roughly five steps in how they use AI: gated, then assisted (one person, one agent), then parallel (one person, something like ten agents in their own worktrees), then supervised autonomy, then AI-native.

Each step clears one bottleneck and exposes the next one. Past a certain point the bottleneck stops being tooling and becomes trust. If I can't trust what ten agents hand me, I'm reviewing ten agents' worth of output by hand, and I haven't gained anything except a backlog.

The same framing names two traps. One is green checks that share the code's wrong assumptions: a test written from the same misunderstanding as the code passes happily and looks like evidence. The other is adding more agents before the loop has earned trust. What's worth measuring is flow (review effort, escaped defects, lead time), not output. Lines of code are easy to come by now.

### The graph I already had

I wasn't starting from zero. At work I'd been using a tech-lead pattern for a while: a lead agent takes a task, breaks it down, and orchestrates implementer, test and review agents to carry it out. There's a bigger version of the idea, too - a dispatcher running many leads at once, each in its own worktree, pausing at checkpoints, with only the human approving plans and pushing.

That graph worked. What it didn't do was remember anything. The reviewer would catch something, the implementer would fix it, and the next task would make the same mistake again, because nothing in the graph wrote down that it had happened.

The funny part is that my homelab already had the loop, just done by hand. When something goes wrong there, a memory note gets written so the next session knows about it. My favourite: seven mutation-testing runs in parallel once took the home internet down. There's a note about that now, and heavy jobs run one at a time. That's the whole loop in miniature. It just depended on me noticing, and remembering to write it down.

### The design

So the question became how to make that loop part of the graph instead of a habit of mine.

**Run records.** Every run of the lead writes a record of every mistake any stage caught: what went wrong, which category it falls into, how bad it was and which agent caught it. Categories matter, because "the same mistake" has to mean something a script can count.

**A retro.** A separate skill reads those records (and my ordinary session transcripts) looking for what keeps going wrong, and proposes the cheapest rule that would stop each recurring mistake.

**A promotion ladder.** "Cheapest" is doing a lot of work in that sentence, so the rules climb a ladder:

- **note:** seen once. It stays in the run record and nothing else happens.
- **instruction:** seen twice, or once at critical severity. It becomes a line in `CLAUDE.md`, a skill or memory.
- **check:** it came back despite the instruction, needs judgment to spot, and can be written down as a repeatable procedure for a verifier to follow.
- **hook:** it came back and can be spotted mechanically, so a hook or a CI check blocks it.
- **test:** the mistake is about the code's behaviour rather than the process, so a test or evaluation fails on it.

Most things should stop at an instruction. Telling the agent is cheap, and it usually works.

**A rules ledger.** Every rule that lands gets an entry saying which category it targets, which rung it's on and how often that category showed up before the rule existed. That's what makes it a loop rather than a pile of advice.

**Verification by recurrence.** On each retro, every rule in the ledger is checked against one question: did its category stop recurring? And crucially, only escapes count against a rule. If a hook blocks the mistake, that's the hook firing, not the mistake recurring. If the mistake gets past the rule, the rule is `recurring` and the retro proposes the next rung up.

**Retirement.** A rule that's at least 90 days old, governing something nobody has touched in that time, is `dormant`, and the retro proposes retiring it. Otherwise `CLAUDE.md` turns into an archaeological dig that every agent pays to read.

**The human gate.** The retro never edits rules on the default branch. It writes its proposals on a new branch and stops. Nothing lands without me merging it, and the ledger entry goes in the same change as the rule, so merging the rule is what records it. A loop that rewrites its own instructions unsupervised is exactly the "agents confirming each other" problem from earlier, with extra steps.

### Where it all lives

The last decision was where any of this lives. There are three scopes:

- **Project:** rules that only make sense in one repo (its layout, its tools, its conventions) go in that repo's `CLAUDE.md`, skills, hooks and tests, with its ledger committed alongside.
- **User:** my own preferences and environment, across every repo, go in `~/.claude/` (that's where the mutation-testing note lives).
- **Framework:** improvements that would help anyone using the graph go back into the plugin itself - but only as a drafted proposal for me to take upstream, never filed automatically.

Nothing project-specific ever goes in the plugin, which is what let me make it public.

### Building it with itself

Which left the problem of how to build it. The answer was to use the graph to build the graph, before the graph existed. It caught more than I expected, starting with my carefully designed human gate. That's the next post.

---

*This post was written with the help of Claude, which also built most of the loop it describes.*
