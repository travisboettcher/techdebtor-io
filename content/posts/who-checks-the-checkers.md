---
title: "Who Checks the Checkers?"
date: 2026-11-22
draft: true
tags: ["AI", "Claude Code"]
summary: "Turning one tester and one reviewer into a swarm of specialists picked by risk, with floors a hostile repo can't remove and tests pushed down to the lowest level that can prove them."
---

*Part 3 of a series on building an agent graph that learns from its mistakes.* [Part 1](/posts/the-missing-loop/) · [Part 2](/posts/building-it-with-itself/)

At the end of [the last post](/posts/building-it-with-itself/) the first run record had turned into four framework proposals and v0.1.1. Two were new checks: the tester learned to time regexes, and the reviewer learned a standing least-privilege check.

Which is great, until you notice where those checks went. Issue 3, filed the same morning, says it plainly: "Today every new check makes one prompt longer." Every lesson the loop learned was another paragraph in one of two briefs. Keep that up for a few months and the reviewer is a wall of text that skims its own instructions, much like I do.

### A swarm, picked by risk

PR 15 turned the tester and the reviewer into **coordinators**, each over a pool of specialists. The tester's pool *runs things*: a test runner, a `fuzzer` (which inherited the regex timing), a mutation tester, a system tester, a security scanner and so on. The reviewer's pool *reads code*: correctness, security, permissions (which inherited least privilege), API compatibility, and docs drift. Each specialist gets one narrow brief and the narrowest tools that work.

The clever bit isn't the pools, it's the choosing. While planning, the lead tags each unit of work with risk tags like `untrusted-input`, `permissions`, `public-api` or `regex`. A selection table, `docs/selection.yml`, maps tags to specialists. Every change gets a baseline of two (the test runner and the correctness reviewer) and the tags add the rest.

So a change that adds a regex to a parser gets tagged `regex` and `untrusted-input`, which pulls in the `fuzzer` and the security reviewer on top of the baseline. A change with no tags at all skips the coordinators entirely: the lead calls the two baseline specialists itself. That fast path costs about 2.3k tokens a round, down from about 3.2k before the swarm, so the common case got *cheaper*, though the always-on cost (what every session pays just to have the plugin installed) went up by about a third. The coordinators also have to say what they chose, what they skipped, and why.

### Floors a hostile repo can't remove

A project can tune the table with its own `.claude/agent-loop/selection.yml`. Reasonable, until the independent reviewer on PR 15 pointed out what that file also is: a file in whatever repo you've just cloned. A hostile repo could ship an override that quietly empties the safeguards that used to run on every change.

The fix is **floors**. Some tags have specialists no override can remove: `permissions` always gets the permissions reviewer, `regex` always gets the `fuzzer`, `untrusted-input` and `security-sensitive` always get the security reviewer, test infrastructure always gets the measurement auditor. Nor can an override disable the baseline, and a budget over the ceiling is clamped to it; every refusal is reported. The lead then re-ran the reviewer's hostile override itself, and every change in it was refused and reported.

It's the same shape as part 2's "the human gate was prose" moment: a safety rule that a config file can switch off is only a default.

### Report-only until it earns it

A verification playbook I'd shared from work had a rule I agreed with immediately: new checks start opt-in and report-only, and the default run must not get slower. A brand-new mutation tester that blocks every change on day one is how you teach people to ignore it.

So the expensive specialists (mutation testing, API fuzzing, integration, service and system tests, performance, security scanning) are opt-in, and once enabled, their findings are shown to me but don't block until the project marks them `blocking`. The independent review found report-only checks that *still stopped runs*. Fixed, but "report-only" is a promise the code has to keep, not a label.

Heavy specialists also run one at a time, within a budget of 6 runs and 60 minutes (capped at 12 and 120). The PR admits those numbers are guesses. The one-at-a-time part isn't a guess: part 1 has the story.

### The lowest level that can prove it

The swarm still treated "the test suite" as one lump, so issue 19 added levels (unit, component, contract, integration, system) and one rule: **prove each behaviour at the lowest level that can prove it**, and only go higher for what lower levels can't see. Each acceptance criterion in the plan now gets a target level, and the test-writer writes the test there. Tests are classified by what they really pull in, not by their markers.

On a follow-up I asked for one more level: **service**. That's the project's own packaged image, started with Testcontainers, with its direct collaborators stubbed over the wire or in containers. It's Toby Clemson's "out-of-process component test", or the "service tests" in Mike Cohn's pyramid, and it proves what in-process tests can't: the image starts, the environment is wired up, migrations run on boot, the health check answers.

A new test strategist checks each criterion's level and reports the pyramid's shape. That shape is always report-only, because one change can't fix a whole suite. The review caught the first version blocking on it anyway. It also caught a regression test added to an existing file knocking the run off the fast path, and a service tester that could push images (it now builds under a unique local tag and never logs in or pushes).

### The ones that scared me

Most review catches were "fair, fixed". A few made my stomach drop.

**The work branch that tracked main.** The lead creates its branch from `origin/main`. Without `--no-track`, git quietly sets that branch to track main, so a bare `git push` could have gone straight to the default branch. The reviewer marked it major. One flag, and exactly the sort of default I'd never have spotted.

**The sneaky push.** In PR 16's dispatcher, which runs several leads in the background, only my own words can approve a push. The review found a way round the first push detection: push early under a different branch name, then rebase. Preflight now snapshots `git ls-remote` of every remote, and the gate fails on any new, moved or deleted ref that an approved push doesn't explain. The lead verified that exact dodge by hand.

**GitHub's `base_ref` in a stack.** The CI version-bump check treats a stacked PR differently from one going straight into main, but in a GitHub stack, `github.base_ref` reports the stack's trunk for every PR in it, so every stacked PR was being judged as if it targeted main. The workflow now asks the API for the real base.

None of these are exotic. They're all "the default does something slightly different from what you'd assume", which is exactly where an agent's confidence and mine overlap.

### What only instructions can hold

Issue 3's open question was whether a plugin agent could start other agents at all. It can; the lead checked before writing the coordinators. But `Agent(<type>)` in a coordinator's tool list doesn't limit *which* agents it starts: on Claude Code 2.1.322 it's accepted and then ignored for a subagent. So a coordinator stays in its own pool because its instructions say so, and nothing else. DESIGN.md says that in so many words, which I'd rather have than a design that pretends.

So who checks the checkers? Partly the floors, partly me at the gate, and partly the retro, which counts each specialist's **misses**: findings in its own categories that got past the whole swarm to me, CI or a hook. A specialist that never catches anything for a tag becomes a proposal to drop it; a category that keeps escaping, a proposal to add one.

And when a specialist's tooling is missing, it reports BLOCKED and names what's missing rather than installing anything. That's a measurement of the repo, not the agents, and it's where part 4 picks up.

---

*This post was written with the help of Claude, and checked by a second agent that hadn't seen the first one's reasoning.*
