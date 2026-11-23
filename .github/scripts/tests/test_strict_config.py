"""The strict config for new posts (.github/vale/new-posts.ini) still catches AI tells.

Runs the pinned Vale over two fixtures: one built from agent-written drafts, on which every
rule the config enables must fire, and one from the blog's own pre-2023 posts, which must
pass clean. A rule whose pattern stops matching, or a config edit that switches a rule off
or below warning, fails here instead of letting drafts through silently.

Needs Vale on PATH (or $VALE) and the packages installed (.github/scripts/vale_packages.py).
Skipped without Vale, unless VALE_REQUIRED=1 (the Vale job in prose.yml sets it).
"""

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[3]
CONFIG = ".github/vale/new-posts.ini"
TELLS = ".github/vale/fixtures/ai-tells.md"
HUMAN = ".github/vale/fixtures/human.md"
REPO_STYLE = ROOT / ".github/vale/styles/Repo"


def vale_binary():
    vale = os.environ.get("VALE") or shutil.which("vale")
    if not vale:
        if os.environ.get("VALE_REQUIRED") == "1":
            pytest.fail("Vale is not on PATH, and VALE_REQUIRED=1")
        pytest.skip("Vale is not installed")
    return vale


def lint(path):
    out = subprocess.run([vale_binary(), f"--config={CONFIG}", "--minAlertLevel=warning", "--output=JSON",
                          "--no-exit", path], cwd=ROOT, capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr
    return [a for alerts in json.loads(out.stdout or "{}").values() for a in alerts]


def enabled_rules():
    """Every rule the strict config names or takes from Repo, except those it turns off.

    A rule set to `suggestion` stays in the set, so the warning-level run below fails on it.
    """
    text = (ROOT / CONFIG).read_text()
    assert re.search(r"(?m)^BasedOnStyles = Repo$", text), "the strict config no longer uses the Repo style"
    off = set(re.findall(r"(?m)^(\w+\.\w+) = NO$", text))
    assert not {r for r in off if r.startswith("Repo.AITells")}, "an AI-tell rule is switched off"
    repo = {f"Repo.{p.stem}" for p in REPO_STYLE.glob("*.yml")}
    named = set(re.findall(r"(?m)^(\w+\.\w+) = \w+$", text))
    return (repo | named) - off


def test_every_enabled_rule_fires_on_the_ai_tells_fixture():
    rules = enabled_rules()
    assert {r for r in rules if r.startswith("Repo.AITells")}, "no AI-tell rules are enabled"
    fired = {a["Check"] for a in lint(TELLS)}
    assert rules - fired == set()


def test_the_blogs_own_voice_passes():
    alerts = lint(HUMAN)
    assert [f"{a['Line']}: {a['Check']} {a['Match']!r}" for a in alerts] == []
