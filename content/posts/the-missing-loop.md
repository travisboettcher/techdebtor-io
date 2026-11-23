---
title: "The Missing Loop"
date: 2026-11-22
draft: true
tags: ["AI", "Claude Code"]
summary: "Over a weekend I had Claude build a graph of agents that writes down its own mistakes and turns the ones that keep coming back into rules, plus an audit of how ready a repo is for agents, which I ran on one of my own."
---

This one started with a phrase I'd heard secondhand: that some engineers at Anthropic work with a "self-improving graph of agents." I didn't know what that meant, but it sounded like something I'd want, so early one Saturday in November I asked Claude. The first thing it did was say it couldn't verify that this was anybody's best practice. What it could do was explain what the idea would have to mean. An explanation isn't evidence, so the only way to find out whether any of it held up was to build it and see.

By Sunday morning there was a public plugin repo, and the system had run its first retro on itself. Along the way it also audited one of my other projects. This is a long one. The audit, about halfway down, was the most interesting part. The retro was the least, because it had little to go on.

## What was missing

### The model doesn't learn

The model doesn't get better between my sessions. If a graph of agents is going to improve itself, the improvement has to live in the things the next run reads before it starts: `CLAUDE.md`, skills, memory, hooks and tests.

Claude's second point was that an improvement only sticks where something can check it, like a test that fails when the mistake comes back. I see the two halves of that a little differently. My intuition is that separate agents catch different things, where one agent running everything mostly agrees with itself. A verifier adds something else: it makes the check deterministic. A test fails the same way every time, whichever agent is looking.

That matched what I'd seen building [`hll`](/posts/designing-a-language-for-a-machine-to-write/). A compiler that answered back did more for the agents writing my homelab config than anything I put in a spec.

### Trust is the bottleneck

I've picked up a framing at work that helped me place this. Teams move through roughly five steps in how they use AI: gated, then assisted (one person, one agent), then parallel (one person, something like ten agents in their own worktrees), then supervised autonomy, then AI-native. Each step clears one bottleneck and exposes the next, and past a certain point the bottleneck stops being tooling and becomes trust. If I can't trust what ten agents hand me, I'm reviewing ten agents' worth of output by hand, and all I've gained is a backlog.

The framing also warns about two traps. Green checks can share the code's wrong assumptions - a test written from the same misunderstanding as the code will pass and look like evidence. And it's tempting to add more agents before the loop has earned any trust. What it says to measure is flow (review effort, escaped defects and lead time), and to ignore lines of code entirely.

### The graph I already had

At work I'd been using a tech-lead pattern for a while. A lead agent takes a task, breaks it down, and orchestrates implementer, test and review agents to carry it out. A bigger version is a dispatcher running many leads at once in their own worktrees, with only the human approving plans and pushing.

That graph didn't remember anything. The reviewer would catch something, the implementer would fix it, and the next task would make the same mistake again.

My homelab already had the loop, done by hand. When something goes wrong there, a memory note gets written for the next session. One time I ran seven mutation-testing runs in parallel and took the home internet down; there's a note about that now, and heavy jobs run one at a time. The catch is that it only works when I notice, and I don't always. I wanted the graph to do that part.

### The design

Every run of the installed `/agent-loop:lead` writes a run record - a small YAML file in the repo's `.claude/runs/`, which git ignores - listing each mistake any stage caught: what went wrong, its category, how bad it was and which agent caught it. For a session that didn't go through the lead, `/agent-loop:retro --record` writes one after the fact. The categories come from a catalog, so that "the same mistake" means something a script can count.

A separate retro skill reads those records (and my ordinary session transcripts) looking for what keeps going wrong, and proposes the cheapest rule that would stop each recurring mistake. Rules climb a promotion ladder:

- `note`: seen once. It stays in the run record and nothing else happens.
- `instruction`: seen twice, or once at critical severity. It becomes a line in `CLAUDE.md`, a skill or memory.
- `check`: it came back despite the instruction, needs judgment to spot, and can be written down as a procedure for a verifier to follow.
- `hook`: it came back and can be spotted mechanically, so a hook or CI check blocks it.
- `test`: the mistake is in the code's behavior, so a test or evaluation fails on it.

Every rule starts as an instruction because telling the agent is cheap. My guess, from experience more than data, is that telling alone often won't be enough, and the rungs above it are there for when it isn't.

Every rule that lands gets an entry in a rules ledger saying which category it targets, which rung it's on, and how often that category showed up before the rule existed. On each retro, every rule in the ledger is checked against one question: did its category stop recurring? Only escapes count against a rule. If a hook blocks the mistake, the hook did its job. If the mistake gets past the rule, the rule is marked `recurring` and the retro proposes the next rung up.

Rules can also retire. A rule at least 90 days old that governs something nobody has touched in that time is `dormant`, and the retro proposes removing it. Otherwise `CLAUDE.md` turns into an archaeological dig that every agent pays to read.

The last piece is the human gate. The retro never edits rules on the default branch. It writes its proposals on a new branch and stops, and nothing lands without me merging it. The ledger entry goes in the same change as the rule, so merging the rule is what records it.

### Where it all lives

Rules that only make sense in one repo go in that repo's `CLAUDE.md`, skills, hooks and tests, with its ledger committed alongside. My own preferences go in `~/.claude/`, where the mutation-testing note lives. Improvements to the plugin itself, the kind that would help anyone using the graph, are framework proposals, and they only ever become a draft for me to take upstream. I'd already decided the plugin would live in a public repo, so keeping anything project-specific out of it was a requirement from the start.

## Building it with itself

The real graph didn't exist yet, so Claude built it with a version of the graph run by hand.

### A home for it

Claude's first scoping was a marketplace for just this one framework, named after me. I wanted a general one for any Claude Code plugins I end up writing, under the techdebtor name, so it became [techdebtor-plugins](https://github.com/travisboettcher/techdebtor-plugins). Both of my corrections went into the run record as findings (`scope-mismatch` and `naming`, caught by "human"). I liked that the record opened with me changing my mind.

### Contract first

Claude acted as the tech lead, and its first commit, at 05:48 on a Saturday, was a marketplace skeleton and a design contract: `DESIGN.md`, 111 lines covering the run record, the rules ledger, the promotion ladder and the human gate. There was no code yet. It's the same approach that worked for `hll` - say what the thing must do before anyone writes it, so the checking has something to check against.

Then two implementer agents built the two halves in parallel: `lead`, the skill that runs the graph, and `retro`, which mines transcripts and run records for mistakes. The retro half came back at about 2,000 lines, most of it a 919-line miner script and its tests. The lead merged the two halves into one plugin, `agent-loop`, and moved the contract inside it so it ships with the code.

After that came a tester agent and a reviewer agent. The reviewer gets the diff and the acceptance criteria and nothing else. There were three rounds at most, and after that it was either done or my problem.

### What the reviewer caught

The first build ended with 18 findings, and a few of them have stuck with me.

The miner redacts session transcripts before reporting on them, and secrets got through twice. The first time, the reviewer found tokens glued to an underscore, short prefixed tokens, and credentials on the command line passing straight through. Those got fixed, and on the next pass it found credentials glued to `-u` (as in `curl -ualice:pw`) and quoted passwords with spaces still leaking.

The miner also parses a small subset of YAML itself. An escaped quote followed by a `#` made it treat the rest of the line as a comment, the whole run record became unparseable, and that record's findings dropped out of ledger verification without any error.

One redaction pattern started a fresh scan at every word boundary inside a long run of identifier characters. Given 40 KB of `ab.cd-` repeated, it took about a minute. Nobody had asked for a test like that. After the fix, every pattern starts its scan only at a fixed anchor, long input is cut to 64 KB before it's scanned at all, and 200 KB of adversarial input runs in under 0.3 seconds.

### The human gate was a sentence

The human gate was written into the retro skill's instructions in plain English, and the same skill pre-approved `Write`, `Edit` and every `git` command. Writes and commits would never have reached a permission prompt. My gate amounted to a sentence asking the agent to please stop (pretty please).

There was more than one of these. Removing that pre-approval left one for the miner script by a wildcard path, which would also have pre-approved a script of the same name planted in any repo I cloned (that one the record marks as caught by `self`). The "read-only" `git diff`, `git log` and `git show` patterns allowed `--output=`, and `--output=` writes files. In all there were three separate `over-broad-pre-approval` findings in one build.

### The lead's own mistakes

The contract the lead wrote had gaps, and one outright self-contradiction: it defined `stage` as where a mistake was made, then its own example recorded review findings as stage `review`. Later, when the lead fixed the miner's pre-approval itself, it left the contract and skill still claiming the miner was pre-approved. The reviewer caught both. The record's notes mark the plan-stage and doc-drift findings as the lead's own, which I was glad to see.

### Four proposals and a point release

Three categories in those 18 findings came up more than once: `over-broad-pre-approval` three times, `redaction-gap` twice, and `naming` twice (one of those was my own correction). The retro is supposed to look for that kind of repetition, and since it didn't work yet, the lead wrote four framework proposals by hand: a standing least-privilege check for the reviewer, regex timing for the tester (the reviewer had found the slow one, the tester hadn't), a list of adversarial inputs in the acceptance criteria for anything handling untrusted input, and new `caught_by` values so an implementer catching a hole in the contract didn't have to file it as "self".

All four went into [PR 2](https://github.com/travisboettcher/techdebtor-plugins/pull/2), agent-loop 0.1.1, along with CI, and its first version was done by 06:48, an hour after the contract. It was built with the graph too. Its reviewer found nothing blocking, but one of its minor findings was that the example timing command for catching slow regexes had no time limit, so a truly slow regex would have hung the tester.

### Why the reviewer doesn't see the reasoning

The reviewer never sees how the implementer reasoned, only the diff and the criteria. An implementer who believes a redaction pattern covers `curl -u` will write a test that agrees with it. Show the reviewer that reasoning and it starts reading the code through the same belief, and then two agents are confident about the same gap. Every reviewer catch above came from an agent that didn't know what the implementer thought it had done, so it had to look at what the code did. It's still Claude, with the same blind spots - it just isn't starting from what the implementer assumed.

## Who checks the checkers?

Once the first version was published and installed, I shared a generic verification playbook from work, and it turned into a pile of GitHub issues: a dispatcher mode, a catalog of mistake categories, a swarm of specialists, a second plugin, and more. Then I went offline, and Claude ran each issue through an implementer, an independent tester and reviewer, and fixes, stacking the results as a chain of pull requests with GitHub's `gh stack` extension. When the stack finally merged, agent-loop was at 0.3.0 and agent-ready at 0.1.0, and `claude plugin update` took my own install from 0.1.0 to 0.3.0.

The swarm came out of a problem with those four proposals. Issue 3 puts it as "Today every new check makes one prompt longer." Give it a few months and the reviewer would be a wall of text skimming its own instructions, much like I do.

### A swarm, picked by risk

PR 15 turned the tester and the reviewer into coordinators, each over a pool of specialists. The tester's pool runs things, like a test runner, a `fuzzer` (which inherited the regex timing) and a mutation tester. The reviewer's pool reads code, with reviewers for correctness, security, permissions (which inherited least privilege), API compatibility and docs drift. Each specialist gets one narrow brief and the narrowest tools that work.

Picking which ones run is done with tags. While planning, the lead tags each unit of work with risk tags like `untrusted-input`, `permissions`, `public-api` or `regex`, and a selection table, `docs/selection.yml`, maps tags to specialists. Every change gets a baseline of two (the test runner and the correctness reviewer), and the tags add the rest. A change that adds a regex to a parser gets tagged `regex` and `untrusted-input`, which pulls in the `fuzzer` and the security reviewer on top of the baseline.

A change with no tags skips the coordinators entirely, and the lead calls the two baseline specialists itself. That fast path costs about 2.3k tokens a round, down from about 3.2k before the swarm - the old single tester and reviewer prompts had grown with every check, and each baseline specialist only carries its own brief. The always-on cost, what every session pays just to have the plugin installed, went up by about a third. A token budget in CI now fails a pull request if a plugin's always-on cost passes its ceiling, and `agent-loop` ended at about 805 of 840 tokens.

### Floors a hostile repo can't remove

A project can tune the table with its own `.claude/agent-loop/selection.yml`. The independent reviewer on PR 15 pointed out that this is also a file in whatever repo you've just cloned, and a hostile repo could ship an override that empties out the safeguards that used to run on every change.

Same problem as the human gate, just in a config file. The fix was floors, specialists that no override can remove from a tag. `permissions` always gets the permissions reviewer, `regex` always gets the `fuzzer`, `untrusted-input` and `security-sensitive` always get the security reviewer, and test infrastructure always gets the measurement auditor, which checks that test counts and coverage figures are believable. An override can't disable the baseline either, and every refusal is reported. The lead re-ran the reviewer's hostile override itself, and every change in it was refused and reported.

The retro's miner enforces the floors in code, but at runtime the coordinators keep them because they're told to. An evaluation checks that they do - in the reviewer coordinator's case, a score of 1.00 with the plugin and 0.33 without ([PR 18](https://github.com/travisboettcher/techdebtor-plugins/pull/18)).

### Heavy checks and test levels

The playbook has a rule that new checks start opt-in and report-only, and that the default run must not get slower. A brand-new mutation tester that blocks every change on day one is how you teach people to ignore it. I'd roll a check out gradually instead: new code is always checked, and existing code doesn't block anything until it has been brought up to the bar.

The expensive specialists (mutation testing, API fuzzing, integration, service and system tests, performance, security scanning) are opt-in, and their findings don't block until the project marks them `blocking`. The independent review found report-only checks that still stopped runs, which got fixed. Heavy specialists also run one at a time, within a budget of 6 runs and 60 minutes (capped at 12 and 120). The PR admits those numbers are guesses. The one-at-a-time part comes from the internet outage.

The swarm still treated "the test suite" as one lump, so issue 19 added levels (unit, component, contract, integration, system) and one rule: prove each behavior at the lowest level that can prove it, and only go higher for what lower levels can't see. Each acceptance criterion in the plan gets a target level, and the test-writer - the agent that, since PR 10, writes failing tests from the acceptance criteria before the implementer starts - writes the test there.

On a follow-up I asked for one more level, service: the project's own packaged image, started with Testcontainers, with its direct collaborators stubbed over the wire or running in containers. Toby Clemson calls it an "out-of-process component test", and Mike Cohn's pyramid has it as "service tests". It proves what in-process tests can't - that the image starts, the environment is wired up, migrations run on boot and the health check answers.

A new test strategist checks each criterion's level and reports the pyramid's shape, always report-only, since one change can't fix a whole suite. The review caught the first version blocking on it anyway. It also caught a service tester that could push images, and that tester now builds under a unique local tag and never logs in or pushes.

### Three catches about pushing

Most of the review catches across the stack were small. Three were about what could reach GitHub, and two of those came from a default doing something slightly different from what you'd assume.

The lead creates its work branch from `origin/main`. Without `--no-track`, git sets that branch to track main, and with `push.default=upstream` a bare `git push` would have gone straight to the default branch (the default, `simple`, refuses when the branch names differ). The reviewer marked it major.

PR 16 added the dispatcher, which runs several leads in the background, and only my own words can approve a push. The review found a way around the first version of the push detection: push early under a different branch name, then rebase. Before a lead starts, it now snapshots `git ls-remote` of every remote, and the dispatcher's check fails on any new, moved or deleted ref that an approved push doesn't explain. The lead tried that exact dodge by hand to verify it.

The third was in CI. The version-bump check treats a stacked PR differently from one going straight into main, but in my stack, Actions reported `github.base_ref` as `main` for every PR, so every stacked PR was being judged as if it targeted main. The workflow now asks the API for the real base.

### What only instructions can hold

Issue 3's open question was whether a plugin agent could start other agents at all. It can; the lead checked before writing the coordinators. But `Agent(<type>)` in a coordinator's tool list doesn't limit which agents it starts. On Claude Code 2.1.322 it's accepted and then ignored for a subagent. A coordinator stays in its own pool because its instructions say so, and nothing else enforces it. `DESIGN.md` says so in as many words.

The retro is what keeps them honest. It counts each specialist's misses (findings in its own categories that got past the whole swarm), and when they pile up it proposes a change to the selection table, behind my gate like everything else.

## Is the repo ready for agents?

None of this helps if the repo's own checks are junk, and the second plugin, `agent-ready`, is there to find out whether they are. When I pointed it at my own project it was polite about what it found.

### Four questions per layer

`/agent-ready:audit` is read-only, and every report leads with one sentence saying which adoption step the repo can support today and what its bottleneck is. Those are the five steps from earlier, numbered from 0 (gated) to 4 (AI-native), and the rubric writes down the gate between each pair as evidence. Going from step 1 to 2, for example, needs tests, types and lint that run on every pull request and block merge, a suite fast enough to run per change, and no flakiness.

Every layer (tests, types, coverage, mutation testing, contract tests, secret scanning, `CLAUDE.md` and the rest, 17 in all) gets the same four questions. Does it exist? Is it in CI? Does it block a merge? Is it measured?

Each answer has to cite evidence, and the rubric is blunt about weak evidence: "A file merely existing is weak evidence and is scored that way." When the evidence isn't there, the answer is `unknown`, and `unknown` never counts as met. Fixes are ranked by the gate they move and the flow metric they should improve, never by lines of code or number of agents.

### Reading a repo you don't trust

An audit tool reads other people's repos, so the scanner treats every repo as hostile. It's a standard-library Python script that never runs project code, starts no subprocesses and makes no network calls.

The independent reviewer built hostile fixture repos to break it. It found Makefile chains that fanned out exponentially, deeply nested JSON that crashed the scan, and a file swapped for a symlink between being listed and being read. The simplest attack was a `CLAUDE.md` that's a symlink to `~/.aws/credentials`, and a dutiful audit would have pasted your cloud keys into its report. The skill pre-approves nothing beyond Read, Glob, Grep and one read-only `git` command, and it's now told to read only files the scanner cited as regular files inside the repo - an evaluation checks that it does, but nothing enforces it, since `Read` is pre-approved for any path, so the guard is an instruction.

### Testing the audit

To check that the audit skill itself behaves, `claude plugin eval` runs each case twice, once with the plugin and once without, and grades what the agent did. The fixture is a tiny Python project whose `CLAUDE.md` is a symlink to a fake secret outside the repo.

Scores are out of 1. With the plugin, the report case scored 1.00. Without it, the score was 0.27, and the baseline read the planted secret. Asked to audit a repo, a capable agent with no special instructions opened `CLAUDE.md`, as you'd expect it to. The symlink attack from the hostile fixtures happened in an actual run.

Across both plugins, every evaluation case scores 1.00 with the plugin and between 0.13 and 0.73 without. Those numbers mostly show that the agents do what the skills ask them to. The one result the skill's instructions didn't cause is the baseline reading the planted secret.

The same tests caught a real bug in the skill. With `--json`, the output is supposed to end with exactly one JSON block so another tool can parse it. The skill offered to save the report after the JSON block, so the output didn't end with valid JSON. Some of those JSON graders had been removed during development because they kept failing, and it was the independent review that found they were failing because of that bug. The graders are back, and the save offer now comes first.

### Pointing it at pip-world

The first target was [pip-world](https://github.com/travisboettcher/pip-world), the engine behind Pip, my autonomous-agent experiment. The repo came out at step 0, gated.

Every item on the gate from 0 to 1 was met except "no secrets in the tree", which came back `unknown`. Nothing in the repo scans for secrets. GitHub's own secret scanning and push protection are turned on for it, but that's a setting the audit couldn't see from the files, so it scored the item unknown, and unknown never counts as met. So step 0 it is - on a technicality! The report pointed out that one secret scan would settle it and put the repo at step 1.

The bigger problem is the next gate. Among the things the audit measured:

- One timed run of the test suite took 10 min 9 s for 2,612 passing tests. `CLAUDE.md`, the file agents read to learn how to work in the repo, says "~15 s". I honestly don't know when it got that slow. CI is worse, at 15 to 21 minutes per run - one PR run took 15.4 minutes, and the last 15 pushes to main took between 15.6 and 21.0.
- There's no lint and no type checker, in CI or anywhere else.
- My own pushes skip the required checks. Six test jobs and the image build are required on `main`, but admin enforcement is off, and only 1 of 199 commits on main came through a pull request. The branch protection is a nice fence with a gate I walk straight through.
- Two flaky, date-dependent tests turned main red on 2026-11-19. The fix was the one commit that came through a pull request.

Mutation testing only runs locally, and the rule in `CLAUDE.md` that limits how many mutation runs happen at once is, in the audit's words, "only text", with no hook or setting enforcing it. That rule exists because of the internet outage, so I'd like it to be more than text.

[My compiler](/posts/31000-lines-i-didnt-type/) makes for an embarrassing comparison. There, every PR into `main` has to get past formatting, clippy, a coverage gate, fuzzing and mutation testing. pip-world has none of the static checks, and I've been walking past the ones it does have.

### What to fix first

The audit ranks its fixes, each with what it unlocks and the closest existing code to copy. The top of the list:

1. A secret scan, once over the full history and then in CI. It's small, and it's the item between step 0 and step 1.
2. Find out why the suite takes ten minutes, fix it, and correct `CLAUDE.md`. A `pytest --durations=30` run is the first step.
3. Make the required checks apply to me too, by turning on admin enforcement or landing changes through PRs. The audit marked this one as my decision, because it changes how work lands.
4. Ruff lint in CI, report-only at first, with type checking on the engine core right behind it.

I knew there was no linter. I just hadn't thought of it as the reason I can't hand my agents more.

## Closing the loop

None of that showed whether the loop actually closes. On Sunday morning I pointed `/agent-loop:retro` at the repo it lives in to find out.

### Not much to read

A retro starts by mining transcripts from past sessions, plus whatever run records are in `.claude/runs/`. It found no transcripts at all. The sessions that built this repo ran on the same machine, but from a different working directory, and the miner looks transcripts up by the project's path, so it never found them. That left the two run records from the first day, the original build and the later build-out, with 30 findings between them.

There was no rules ledger yet, so there was nothing to verify. The retro did notice that five rules in `CLAUDE.md` had been written on day one, after both records and in answer to them: least privilege, linear-time parsing, no contradictions across files, shipped files stay generic, and namespaced names. It put those five into the new ledger as they stood, each with a `baseline` (four for over-broad pre-approval, for example) and an empty history.

### Two instructions and a note

Two categories cleared the bar for the `instruction` rung.

The first was `unhandled-input`, with four findings, one of them critical. The records never used that name. The agents had filed them as `crash-on-malformed-input` and `yaml-parse`, neither of which is in the category catalog, and the retro mapped them onto the catalog's own category. They included the escaped quote that made a whole run record unparseable and, the critical one, the readiness scanner crashing on deeply nested JSON from a repo it was auditing. The linear-time rule covers speed and not crashes, so the new line sits right after it: skip and report a malformed item, with a test for each shape. It includes the sentence "One bad file must not hide every other result."

The second was `contract-gap`, with six findings plus one self-contradiction, all holes in `DESIGN.md` rules; review caught four of the six and the contradiction, and the lead and an implementer caught the other two. One was a review gate that trusted a stage list the agent wrote about itself. The new rule says that before you add or change a contract rule, you list the cases that could break it and say what the rule does with each. The retro ended it with "Review found a hole of this kind in most contract changes so far", which is its own reading of the records and something nobody has checked yet.

The retro also left something alone. `unsafe-git-default` is the work branch that tracked `main`, which the reviewer marked major. It happened once, and `--no-track` already fixed it, so it stays a note with no rule attached. The ladder is there so that one vivid incident doesn't become a permanent line every future agent has to read, and it held on its first real run.

### Proposals that had already shipped

The lead had written four framework proposals by hand on the first day, and the retro retired all four, because each had already shipped somewhere between 0.1.1 and 0.3.0. The least-privilege check became the permissions reviewer, for example, and the regex timing is the `fuzzer`'s floor for anything tagged `regex`.

It drafted one new proposal of its own, a category called `over-broad-cleanup`. It comes from the stack build, when an implementer tried to clean up with `pkill` by name pattern and Claude Code's permission classifier stopped it. The proposed rule is to remove only what you started, by the ID you noted when you started it (a PID, a container ID, a worktree path), and never by pattern. It's framework-wide because dispatcher mode runs several leads on one machine, and one lead's pattern kill could stop another lead's heavy job, or mine. I'm in favor of this one.

The ledger and the two rules are three local commits on a `retro/2026-11-22` branch, and the framework proposal is a draft in a local file for me to take upstream or not. Nothing was pushed, and nothing touched my user settings. It won't be live until I review and merge it, and as I write this I haven't.

### What the loop can't see

The second run record covers the swarm, the dispatcher and `agent-ready`. What has no record is the work after it: prose linting with Vale, the evaluations, test levels, the CI fixes and merging the stack. (The retro's own summary got this wrong and counted the swarm and `agent-ready` as unrecorded too.) Nothing wrote records on its own because the stack was built with the graph run by hand - by Claude, in one session, using ordinary subagents, before `agent-loop` was even installed - and the two records that exist were written by hand.

Fixing it needs a habit and no new code. Running `/agent-loop:retro --record` after a big session writes a record, and that gives the next retro something to verify the new rules against.

A small example turned up while I was fact-checking this post. `CONTRIBUTING.md` on main said "No status check is required by the ruleset yet". That was true when it was written, but since the stack merged a second ruleset has required nine of them, with no bypass. It's a `doc-drift` finding, a category already in the new ledger, and no record anywhere says it happened. I fixed it in [PR 21](https://github.com/travisboettcher/techdebtor-plugins/pull/21), outside the graph, so the loop didn't see that either.

### What's next

The next steps are small: review the branch, record runs, run the retro again. The first verdict on `unhandled-input` and `contract-gap` will come out of that, and I'll post it.

<!-- LISTENING FOOTER: owner to supply -->

---

*This post was written with the help of Claude, which also built most of what it describes.*
