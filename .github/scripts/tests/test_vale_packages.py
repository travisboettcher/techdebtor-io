"""vale_packages.py installs pinned, checksummed Vale packages into the StylesPath."""

import hashlib
import io
import json
import stat
import sys
import zipfile
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import vale_packages as vp  # noqa: E402


def make_zip(members):
    """Return zip bytes; members maps a name to text, or to (text, unix mode) for a symlink or other mode."""
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for name, content in members.items():
            if isinstance(content, tuple):
                info = zipfile.ZipInfo(name)
                info.external_attr = content[1] << 16
                z.writestr(info, content[0])
            else:
                z.writestr(name, content)
    return buf.getvalue()


def setup(tmp_path, packages):
    """Write each package's zip into a cache directory and a manifest pinning it; return the paths."""
    cache = tmp_path / "cache"
    cache.mkdir()
    entries = []
    for name, version, data, sha in packages:
        (cache / f"{name}-{version}.zip").write_bytes(data)
        entries.append({"name": name, "version": version,
                        "url": f"https://github.com/example/{name}/releases/download/{version}/{name}.zip",
                        "sha256": sha or hashlib.sha256(data).hexdigest()})
    manifest = tmp_path / "packages.json"
    manifest.write_text(json.dumps({"packages": entries}))
    styles = tmp_path / "styles"
    styles.mkdir(exist_ok=True)
    return manifest, styles, cache


def run(manifest, styles, cache):
    return vp.main(["--manifest", str(manifest), "--styles", str(styles), "--cache", str(cache)])


def test_a_style_package_lands_under_its_own_name(tmp_path):
    data = make_zip({"proselint/": "", "proselint/Very.yml": "extends: existence\n", "proselint/meta.json": "{}"})
    manifest, styles, cache = setup(tmp_path, [("proselint", "v1", data, None)])
    assert run(manifest, styles, cache) == 0
    assert (styles / "proselint" / "Very.yml").read_text() == "extends: existence\n"


def test_a_config_package_contributes_only_its_styles_directory(tmp_path):
    data = make_zip({"Voices/.vale.ini": "Packages = latest\n", "Voices/meta.json": "{}",
                     "Voices/LICENSE": "MIT", "Voices/styles/Voices/Recap.yml": "a",
                     "Voices/styles/config/vocabularies/Voices/accept.txt": "b"})
    manifest, styles, cache = setup(tmp_path, [("Voices", "v2", data, None)])
    assert run(manifest, styles, cache) == 0
    assert (styles / "Voices" / "Recap.yml").read_text() == "a"
    assert (styles / "config" / "vocabularies" / "Voices" / "accept.txt").read_text() == "b"
    assert not (styles / ".vale.ini").exists() and not (styles / "Voices" / ".vale.ini").exists()


def test_a_checksum_mismatch_installs_nothing(tmp_path, capsys):
    data = make_zip({"P/R.yml": "x"})
    manifest, styles, cache = setup(tmp_path, [("P", "v1", data, "0" * 64)])
    assert run(manifest, styles, cache) == 1
    assert "sha256" in capsys.readouterr().err
    assert list(styles.iterdir()) == []


@pytest.mark.parametrize("member", ["../evil.yml", "/abs/evil.yml", "P/../../evil.yml", "P\\..\\evil.yml",
                                    "C:/evil.yml"])
def test_a_member_outside_the_styles_path_is_refused(tmp_path, member):
    data = make_zip({"P/R.yml": "x", member: "evil"})
    manifest, styles, cache = setup(tmp_path, [("P", "v1", data, None)])
    assert run(manifest, styles, cache) == 1
    assert not (tmp_path / "evil.yml").exists()
    assert list(styles.iterdir()) == []


def test_a_symlink_member_is_refused(tmp_path):
    data = make_zip({"P/R.yml": "x", "P/link.yml": ("/etc/passwd", stat.S_IFLNK | 0o777)})
    manifest, styles, cache = setup(tmp_path, [("P", "v1", data, None)])
    assert run(manifest, styles, cache) == 1
    assert list(styles.iterdir()) == []


def test_an_oversized_archive_is_refused(tmp_path, monkeypatch):
    monkeypatch.setattr(vp, "MAX_UNPACKED", 100)
    data = make_zip({"P/R.yml": "x" * 101})
    manifest, styles, cache = setup(tmp_path, [("P", "v1", data, None)])
    assert run(manifest, styles, cache) == 1
    assert list(styles.iterdir()) == []


def test_a_package_never_overwrites_a_file_it_did_not_install(tmp_path, capsys):
    data = make_zip({"V/styles/config/vocabularies/Repo/accept.txt": "theirs"})
    manifest, styles, cache = setup(tmp_path, [("V", "v1", data, None)])
    own = styles / "config" / "vocabularies" / "Repo" / "accept.txt"
    own.parent.mkdir(parents=True)
    own.write_text("ours")
    assert run(manifest, styles, cache) == 1
    assert own.read_text() == "ours"
    assert "not installed by" in capsys.readouterr().err


def test_upgrading_removes_the_old_versions_files_and_keeps_the_repos_own(tmp_path):
    old = make_zip({"P/Old.yml": "1", "P/Kept.yml": "1"})
    manifest, styles, cache = setup(tmp_path, [("P", "v1", old, None)])
    (styles / "Repo").mkdir()
    (styles / "Repo" / "Rule.yml").write_text("ours")
    assert run(manifest, styles, cache) == 0
    new = make_zip({"P/Kept.yml": "2", "P/New.yml": "2"})
    (cache / "P-v2.zip").write_bytes(new)
    manifest.write_text(json.dumps({"packages": [{
        "name": "P", "version": "v2", "url": "https://github.com/example/P/releases/download/v2/P.zip",
        "sha256": hashlib.sha256(new).hexdigest()}]}))
    assert run(manifest, styles, cache) == 0
    assert sorted(p.name for p in (styles / "P").iterdir()) == ["Kept.yml", "New.yml"]
    assert (styles / "P" / "Kept.yml").read_text() == "2"
    assert (styles / "Repo" / "Rule.yml").read_text() == "ours"


def test_a_second_run_with_the_same_pins_changes_nothing(tmp_path, capsys):
    data = make_zip({"P/R.yml": "x"})
    manifest, styles, cache = setup(tmp_path, [("P", "v1", data, None)])
    assert run(manifest, styles, cache) == 0
    (cache / "P-v1.zip").unlink()  # nothing is read or downloaded when the pins are already installed
    assert run(manifest, styles, cache) == 0
    assert "up to date" in capsys.readouterr().err
    assert (styles / "P" / "R.yml").read_text() == "x"


def test_a_cached_zip_with_a_wrong_checksum_is_refused_not_trusted(tmp_path, monkeypatch):
    data = make_zip({"P/R.yml": "x"})
    manifest, styles, cache = setup(tmp_path, [("P", "v1", data, None)])
    (cache / "P-v1.zip").write_bytes(make_zip({"P/R.yml": "tampered"}))
    monkeypatch.setattr(vp, "download", lambda url: pytest.fail("a pinned zip in the cache is never re-fetched"))
    assert run(manifest, styles, cache) == 1
    assert list(styles.iterdir()) == []


@pytest.mark.parametrize("entry", [
    {"name": "P", "version": "v1", "url": "http://github.com/x/P.zip", "sha256": "a" * 64},
    {"name": "P", "version": "v1", "url": "https://example.com/P.zip", "sha256": "a" * 64},
    {"name": "P", "version": "v1", "url": "https://github.com/x/P/releases/latest/download/P.zip", "sha256": "a" * 64},
    {"name": "P", "version": "v1", "url": "https://github.com/x/P/releases/download/v1/P.zip", "sha256": "abc"},
    {"name": "../P", "version": "v1", "url": "https://github.com/x/P/releases/download/v1/P.zip", "sha256": "a" * 64},
    {"name": "P", "version": "v1", "url": "https://github.com/x/P/releases/download/v1/P.zip"},
])
def test_a_manifest_entry_must_be_a_pinned_github_release(tmp_path, entry):
    manifest = tmp_path / "packages.json"
    manifest.write_text(json.dumps({"packages": [entry]}))
    styles = tmp_path / "styles"
    styles.mkdir()
    assert vp.main(["--manifest", str(manifest), "--styles", str(styles)]) == 2


def test_the_repositorys_manifest_is_valid():
    manifest = Path(__file__).resolve().parents[2] / "vale" / "packages.json"
    packages = vp.read_manifest(manifest)
    assert {p["name"] for p in packages} >= {"Prompts", "Voices", "proselint"}
