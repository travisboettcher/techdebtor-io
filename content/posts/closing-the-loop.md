---
title: "Closing the Loop"
date: 2026-11-22
draft: true
tags: ["AI", "Claude Code"]
summary: "The first real retro on the agent graph's own repo: what it promoted, what it left as a note, what it threw away, and what it couldn't see."
---

*Part 5 of a series on building an agent graph that learns from its mistakes.* [Part 1](/posts/the-missing-loop/) · [Part 2](/posts/building-it-with-itself/) · [Part 3](/posts/who-checks-the-checkers/) · [Part 4](/posts/is-the-repo-ready-for-agents/)

Everything so far has been construction: a design, a graph that built itself, a swarm of reviewers, an audit for whether a repo is ready for any of it. What I hadn't done was the thing the whole project exists for: run a retro and see whether the loop actually closes.

So on Sunday morning I pointed `/agent-loop:retro` at the repo it lives in, [techdebtor-plugins](https://github.com/travisboettcher/techdebtor-plugins).

### Not much to read

A retro starts by mining transcripts from past sessions, plus the run records each build leaves behind. It found no transcripts at all: the sessions that built this repo didn't run on the machine I ran the retro on.

That left the two run records from the first day, the original build from [part 2](/posts/building-it-with-itself/) and the later build-out. Between them, 30 findings. Neither had any specialist selections or test levels, because both builds came before the swarm existed. Fine. It's a first retro.

### A ledger that starts with what I already had

There was no rules ledger yet, so nothing to verify. But the retro noticed that five rules in `CLAUDE.md` had been written on day one, after both records and in answer to them: least privilege, linear-time parsing, no contradictions across files, shipped files stay generic, namespaced names.

Rather than stack new rules on top, it put those five in the new ledger as they stood, each with a `baseline` (the count from the records before the rule existed: four for over-broad pre-approval, for example) and an empty history. No recorded run has happened since, so every one sits at zero with no verdict. That's the honest answer. A rule written yesterday hasn't had a chance to fail yet.

### Two instructions and a note

Two categories cleared the bar for the `instruction` rung.

**`unhandled-input`**, four findings, one critical. Fun detail: the records never used that name. The agents had filed them as `crash-on-malformed-input` and `yaml-parse`, neither of which is in the category catalog, so the retro mapped them onto the catalog's own category. The evidence: malformed transcripts crashing the miner, an escaped quote making a whole run record unparseable, the gate crashing on signed commits, and the critical one, the readiness scanner from [part 4](/posts/is-the-repo-ready-for-agents/) crashing on deeply nested JSON from a repo it was auditing. The linear-time rule covers speed, not crashes, so the new line sits right after it: skip and report a malformed item, with a test for each shape. "One bad file must not hide every other result."

**`contract-gap`**, six findings plus one self-contradiction: holes in `DESIGN.md` rules that review caught. An approval gate that flagged trunk merges. A review gate that trusted a stage list the agent wrote about itself. Verdicts that counted a rule's own catches as recurrences. The new rule: before you add or change a contract rule, list the cases that could break it and say what the rule does with each. It ends with a slightly damning sentence: "Review found a hole of this kind in most contract changes so far."

And then the one I like best, because of what the retro *didn't* do. `unsafe-git-default` is the work branch from [part 3](/posts/who-checks-the-checkers/) that silently tracked `main`, so a bare `git push` could have gone straight to it. It's the scariest story in this series. It also happened once, and `--no-track` already fixed it. So it stays a note, no rule. The ladder exists so one vivid incident doesn't become a permanent line every future agent has to read, and it held on its first real run.

### Throwing out my own proposals

On day one, the first run record produced four hand-written "framework proposals". The retro dropped all four, because each had already shipped somewhere between 0.1.1 and 0.3.0: the least-privilege check became the permissions reviewer, the regex timing check is the `fuzzer`'s floor for anything tagged `regex`, and so on. A retro that re-proposes finished work is noise.

It drafted one new proposal of its own, a category called `over-broad-cleanup`, from the moment in the stack build when an implementer tried to clean up with `pkill` by name pattern and Claude Code's permission classifier stopped it. The fix: remove only what you started, by the ID you noted when you started it (a PID, a container ID, a worktree path), never by pattern. It's framework-wide because dispatcher mode runs several leads on one machine, and one lead's pattern kill could stop another lead's heavy job, or mine. I'm in favour.

The ledger and the two rules are three local commits on a `retro/2026-11-22` branch, and the framework proposal is a draft in a local file for me to take upstream or not. Nothing pushed, no changes to my user settings. None of it is live until I review and merge it, and as I write this I haven't. That's the human gate from part 1 doing what it said it would.

### What the loop can't see

Here's the uncomfortable part. After those two run records came 109 more commits: the whole `agent-ready` plugin, the swarm, the dispatcher, most of what parts 3 and 4 are about. None of it has a run record. The busiest stretch of the project is invisible to the tool built to learn from it.

The fix is boring: record runs. `/agent-loop:retro --record` after a big session writes one, and that gives the next retro something to verify the new rules against.

I found a small example while writing this post. `CONTRIBUTING.md` on main says "No status check is required by the ruleset yet". That was true when it was written; now a second ruleset requires nine of them, with no bypass. That's `doc-drift`, a category already in the new ledger, and no record anywhere says it happened.

### The machinery around it

A few supporting pieces, briefly:

- **Prose linting for prompts.** Vale lints the skills, agents, `CLAUDE.md` and even the always-on descriptions as prompts. Claude's first version hand-rolled its own styles until my review pointed it at Vale's upstream packages for agent prose and at `proselint`; those now come pinned to versioned zips with checksums. A token budget fails a pull request if a plugin's always-on cost passes its ceiling; `agent-loop` ended at about 805 of 840.
- **Behavioural evaluations.** Every case scored 1.00 with the plugin and between 0.13 and 0.73 without. A nightly run costs about US$2.
- **Version bumps.** Reviewing the first pull request, I asked whether CI should make sure the version always gets bumped. It should: `claude plugin update` only picks up a release when the version changes.
- **Merging against my own ruleset.** `gh stack merge` can't use the admin bypass, and stacked pull requests can't go through `gh pr merge`, so the stack was unlinked and merged one at a time. Then `claude plugin update` took my install from 0.1.0 to 0.3.0.

### Where it goes from here

At the start of this series, Claude told me the model doesn't learn, the scaffolding does, and only where something can check it. One retro in, that holds up. The interesting output wasn't the two new rules. It was the note it declined to promote, the proposals it threw away because they'd shipped, and the plain admission that it couldn't see most of the work.

So the next steps are small. Review the retro branch and merge it, or not. Record runs. Then run the retro again and find out whether `unhandled-input` and `contract-gap` actually stopped coming back. That's the first verdict this ledger will ever hand down, and I'm curious which way it goes.

That's the series. Thanks for reading along.

---

*This post was written with the help of Claude, which also proposed the rules it's about. I still have to approve them.*
