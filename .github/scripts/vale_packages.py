#!/usr/bin/env python3
"""Install the pinned Vale packages into the StylesPath, checking each against its sha256.

Usage: python3 vale_packages.py [--manifest .github/vale/packages.json]
                                [--styles .github/vale/styles] [--cache DIR]

The manifest pins each package to a versioned GitHub release zip and its sha256
({"packages": [{"name", "version", "url", "sha256"}]}); never a `latest` URL.
Each zip is downloaded (or read from DIR/<name>-<version>.zip when --cache is
given; a download is saved there), checked against its sha256, checked for
members that would land outside the StylesPath, symlinks and size, and only
then unpacked. A style package (Name/Rule.yml) lands in <styles>/Name/; a
config package (Name/styles/... beside a .vale.ini) contributes only its
styles/ directory, as `vale sync` would; its .vale.ini is not used:
.vale.ini at the repository root is the whole configuration.

<styles>/.vale-packages.json records the pins and the files installed, so a
second run with the same pins does nothing, and a new pin removes the old
version's files first. A package never overwrites a file it did not install
(the repository's own vocabulary and rules). Use this instead of `vale sync`.

Exit 0 when the packages are installed, 1 when a zip fails a check or cannot
be fetched (nothing is changed), 2 when the manifest is invalid. Standard
library only.
"""

import argparse
import hashlib
import io
import json
import re
import stat
import sys
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath

STAMP = ".vale-packages.json"
MAX_UNPACKED = 20 * 1024 * 1024  # bytes per package; the real ones are well under 1 MB
MAX_DOWNLOAD = 20 * 1024 * 1024
TIMEOUT = 60
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*")
URL = re.compile(r"https://github\.com/[\w.-]+/[\w.-]+/releases/download/[^/?#]+/[\w.-]+\.zip")
SHA256 = re.compile(r"[0-9a-f]{64}")


class Refused(Exception):
    """A package failed a check; nothing was installed."""


def read_manifest(path):
    """Return the manifest's packages, or raise ValueError if an entry is not a pinned release zip."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    packages = data.get("packages") if isinstance(data, dict) else None
    if not isinstance(packages, list) or not packages:
        raise ValueError("the manifest has no packages list")
    for p in packages:
        if not isinstance(p, dict) or not all(isinstance(p.get(k), str) for k in ("name", "version", "url", "sha256")):
            raise ValueError(f"{p!r}: needs name, version, url and sha256")
        if not NAME.fullmatch(p["name"]) or not NAME.fullmatch(p["version"]):
            raise ValueError(f"{p['name']!r}: name and version are plain words")
        if not URL.fullmatch(p["url"]) or "/releases/download/latest/" in p["url"]:
            raise ValueError(f"{p['name']}: the url must be a versioned GitHub release download over https")
        if not SHA256.fullmatch(p["sha256"]):
            raise ValueError(f"{p['name']}: sha256 must be 64 lowercase hex digits")
    return packages


def download(url):
    with urllib.request.urlopen(url, timeout=TIMEOUT) as r:  # noqa: S310 (the url is checked above)
        data = r.read(MAX_DOWNLOAD + 1)
    if len(data) > MAX_DOWNLOAD:
        raise Refused(f"{url}: larger than {MAX_DOWNLOAD} bytes")
    return data


def fetch(package, cache):
    cached = cache / f"{package['name']}-{package['version']}.zip" if cache else None
    if cached and cached.is_file():
        data = cached.read_bytes()
    else:
        try:
            data = download(package["url"])
        except OSError as e:
            raise Refused(f"{package['name']}: cannot download {package['url']}: {e}") from e
        if cached:
            cache.mkdir(parents=True, exist_ok=True)
            cached.write_bytes(data)
    digest = hashlib.sha256(data).hexdigest()
    if digest != package["sha256"]:
        raise Refused(f"{package['name']} {package['version']}: sha256 is {digest}, the manifest pins {package['sha256']}")
    return data


def plan(package, data):
    """Return {relative target path: bytes} for the zip's files, or raise Refused."""
    name = package["name"]
    try:
        z = zipfile.ZipFile(io.BytesIO(data))
    except zipfile.BadZipFile as e:
        raise Refused(f"{name}: not a zip: {e}") from e
    members, total = [], 0
    for info in z.infolist():
        raw = info.filename
        path = PurePosixPath(raw)
        if ("\\" in raw or path.is_absolute() or ".." in path.parts or not path.parts
                or ":" in path.parts[0]):
            raise Refused(f"{name}: member {raw!r} would land outside the styles directory")
        mode = info.external_attr >> 16
        if stat.S_ISLNK(mode):
            raise Refused(f"{name}: member {raw!r} is a symlink")
        total += info.file_size
        if total > MAX_UNPACKED:
            raise Refused(f"{name}: unpacks to more than {MAX_UNPACKED} bytes")
        if not info.is_dir():
            members.append((path, info))
    config_package = any(len(p.parts) > 2 and p.parts[1] == "styles" for p, _ in members)
    files = {}
    for path, info in members:
        if config_package:
            if len(path.parts) < 3 or path.parts[1] != "styles":
                continue  # .vale.ini, meta.json, LICENSE: not part of the StylesPath
            target = PurePosixPath(*path.parts[2:])
        else:
            if len(path.parts) < 2:
                continue  # a file beside the package's directory
            target = path
        data_bytes = z.read(info)
        if len(data_bytes) != info.file_size:
            raise Refused(f"{name}: member {info.filename!r} does not match its stated size")
        files[target.as_posix()] = data_bytes
    if not files:
        raise Refused(f"{name}: the zip holds no style files")
    return files


def install(packages, styles, cache):
    stamp_path = styles / STAMP
    try:
        stamp = json.loads(stamp_path.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        stamp = {}
    pins = [{k: p[k] for k in ("name", "version", "sha256")} for p in packages]
    if stamp.get("pins") == pins and all((styles / f).is_file() for f in stamp.get("files", [])):
        print("vale_packages: up to date", file=sys.stderr)
        return
    previous = set(stamp.get("files", [])) if isinstance(stamp.get("files"), list) else set()
    planned = {}
    for p in packages:
        for target, data in plan(p, fetch(p, cache)).items():
            if target in planned:
                raise Refused(f"{p['name']}: {target} is also in another package")
            if target == STAMP:
                raise Refused(f"{p['name']}: holds {STAMP}")
            if (styles / target).exists() and target not in previous:
                raise Refused(f"{p['name']}: {target} exists and was not installed by vale_packages.py")
            planned[target] = data
    root = styles.resolve()
    for target in sorted(previous):
        path = styles / target
        if path.is_file() and not path.is_symlink() and root in path.resolve().parents:
            path.unlink()
            for parent in path.parents:
                if parent == styles or any(parent.iterdir()):
                    break
                parent.rmdir()
    for target, data in sorted(planned.items()):
        path = styles / target
        path.parent.mkdir(parents=True, exist_ok=True)
        if root not in path.resolve().parents:
            raise Refused(f"{target} resolves outside the styles directory")
        path.write_bytes(data)
    stamp_path.write_text(json.dumps({"pins": pins, "files": sorted(planned)}, indent=1) + "\n", encoding="utf-8")
    for p in packages:
        print(f"vale_packages: {p['name']} {p['version']} installed", file=sys.stderr)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--manifest", default=".github/vale/packages.json")
    ap.add_argument("--styles", default=".github/vale/styles")
    ap.add_argument("--cache", help="read and save the zips here (they are checked either way)")
    args = ap.parse_args(argv)
    try:
        packages = read_manifest(args.manifest)
    except (OSError, ValueError) as e:
        print(f"vale_packages: bad manifest: {e}", file=sys.stderr)
        return 2
    styles = Path(args.styles)
    try:
        styles.mkdir(parents=True, exist_ok=True)
        install(packages, styles, Path(args.cache) if args.cache else None)
    except (Refused, OSError) as e:
        print(f"vale_packages: {e}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
