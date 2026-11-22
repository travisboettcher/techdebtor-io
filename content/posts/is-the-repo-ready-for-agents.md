---
title: "Is the Repo Ready for Agents?"
date: 2026-11-22
draft: true
tags: ["AI", "Claude Code"]
summary: "A read-only audit that asks what a repo's checks can actually prove, and what happened when I pointed it at my own project."
---

*Part 4 of a series on building an agent graph that learns from its mistakes.* [Part 1](/posts/the-missing-loop/) · [Part 2](/posts/building-it-with-itself/) · [Part 3](/posts/who-checks-the-checkers/)

Three posts in, the loop has a tech lead, a swarm of checkers and a retro. All of it leans on one quiet assumption: that the repo has checks worth trusting. A test-runner agent is only as good as the tests.

So the second plugin in the marketplace, `agent-ready`, asks that question directly. Then I pointed it at my own project, and it was polite about what it found.

### Four questions per layer

`/agent-ready:audit` is read-only, and every report leads with one sentence: **which adoption step the repo can support today, and what its bottleneck is.** Those are the five adoption steps from [part 1](/posts/the-missing-loop/), numbered from 0 (gated) to 4 (AI-native), and the rubric writes the gate between each pair down as evidence. Step 1 → 2, for example, needs "a self-check loop you trust, plus automated review": tests, types and lint that run on every pull request and block merge, a suite fast enough to run per change, and no flakiness.

Every layer (tests, types, coverage, mutation testing, contract tests, secret scanning, CLAUDE.md and the rest, 17 in all) gets the same four questions:

- Does it **exist**?
- Is it **in CI**?
- Does it **block a merge**?
- Is it **measured**?

Each answer cites evidence. The rubric is blunt about weak evidence: "A file merely existing is weak evidence and is scored that way." And when the evidence isn't there, the answer is `unknown`, which never counts as met. That rule matters later.

Fixes are ranked by the gate they move and the flow metric from part 1 they should improve, never by lines of code or number of agents.

### Reading a repo you don't trust

An audit tool reads other people's repos, so the scanner treats every repo as hostile: a standard-library Python script that never runs project code, starts no subprocesses and makes no network calls. It reports facts with line references; the skill does the judging.

The independent reviewer built hostile fixture repos to break it, and found Makefile chains that fanned out exponentially, deeply nested JSON that crashed the scan, and a file swapped for a symlink between being listed and being read. My favourite was the simplest: a `CLAUDE.md` that's a symlink to `~/.aws/credentials`. A dutiful audit would paste your cloud keys into its report. Now the skill only reads files the scanner has cited as regular files inside the repo, and it pre-approves nothing beyond Read, Glob, Grep and one read-only `git` command.

### Pointing it at my own repo

The obvious first target was [pip-world](https://github.com/travisboettcher/pip-world), the engine behind Pip, my autonomous-agent experiment. I was fairly sure I wouldn't enjoy the answer.

The verdict: **step 0, gated. On a technicality.**

Every item on the 0 → 1 gate was met except "no secrets in the tree", which came back `unknown`, because nothing has ever scanned the repo for secrets. `unknown` never counts as met, so step 0 it is. The rule working as intended, and no less annoying for it. The report noted that one secret scan would settle it and put the repo at step 1, which is the most generous way anyone has ever told me I'm still on the bottom step.

The real problem is the gate after that. Here's what the audit measured:

- **The suite is slow.** One timed run: 2,612 passed in **10 min 9 s**. CLAUDE.md, the file agents read to learn how to work in the repo, says "~15 s". CI is worse, at 15 to 21 minutes per push to main.
- **No lint and no type checker.** Not "not in CI". Not there at all.
- **My own pushes skip the required checks.** Six test jobs and the image build are required on `main`, but admin enforcement is off, and only 1 of 199 commits on main came through a pull request. The branch protection is a lovely fence with a gate I walk straight through.
- **Flaky tests reached main.** Two date-dependent tests turned main red on 2026-11-19. The fix was that lone commit that came through a pull request.

Smaller findings stung too. The 95% coverage figure is one combined number with no unit/integration split, so it may overstate what the fast loop checks. Mutation testing exists but only runs locally. The rule in CLAUDE.md that limits how many mutation runs happen at once is "only text": no hook or setting enforces it. It's the lesson from part 1's internet outage, so I'd like it to be more than text. And the scanner's one hit for spec-style "when X, the system shall Y" criteria was in the font licence. The audit spotted that one itself.

The contrast with [my compiler](/posts/31000-lines-i-didnt-type/) is a bit embarrassing. There, every PR into `main` has to get past formatting, clippy, a coverage gate, fuzzing and mutation testing. pip-world has none of the static checks, and I've been walking past the ones it does have. The audit is just the bill.

### What it said to fix first

The top of the ranked list, each fix with what it unlocks and the closest existing code to copy:

1. **A secret scan**, once over the full history and then in CI. Small, and it's the 0 → 1 item.
2. **Find out why the suite takes ten minutes**, fix it, and correct CLAUDE.md. A `pytest --durations=30` run is the first step.
3. **Make the required checks apply to me too**: turn on admin enforcement, or land changes through PRs. The audit marked this one as my decision, because it changes how work lands.
4. **Ruff lint, then type checking on the engine core**, both report-only at first.

It also suggested a throwaway draft PR to settle whether diff-scoped mutation testing finishes in reasonable time on GitHub's hosted runners, adding that those jobs never run on the homelab box. Fair.

None of this is news. I knew there was no linter. What's different is seeing it as "this is why your agents can't be trusted with more", which turns vague guilt into a list with an order.

### Testing the tester

How do you know the audit skill itself behaves? `claude plugin eval` runs each case twice, once with the plugin and once without, and grades what the agent did. The fixture is a tiny Python project whose `CLAUDE.md` is a symlink to a fake secret outside the repo.

With the plugin, the report case scored 1.00. Without it, 0.27, and **the baseline read the planted secret.** Asked to audit a repo, a capable agent with no special instructions opened CLAUDE.md, because of course it did. That's the hostile-fixture attack happening for real, and the best argument I have for this being a plugin rather than a prompt.

The same tests caught a real bug in the skill. With `--json`, the output is supposed to end with exactly one JSON block, so another tool can parse it. The skill offered to save the report *after* the JSON block, so the output didn't end with valid JSON. Some of those JSON graders had been dropped during development; the independent review noticed they'd been failing for a real reason. They're back, and the save offer now comes first. A full run of agent-ready's cases costs about fifty cents with Sonnet.

So the plugin says the repo is step 0, the tests say the plugin is doing its job, and I have a list. What's left is the part this whole series is about: whether the loop learns anything when it runs for real. In part 5, the first real retro.
